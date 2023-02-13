from concurrent.futures import ProcessPoolExecutor
import os
import random
from json.decoder import JSONDecodeError
from app.data_managers import from_json, to_csv, to_json
from app.scrappers.abcs import MeteoScrapper
from app.scrappers.meteociel_scrappers import MeteocielDaily, MeteocielMonthly
from app.scrappers.wunderground_scrappers import WundergroundMonthly
from app.scrappers.ogimet_scrappers import OgimetMonthly
from app.checkers.ConfigFileChecker import ConfigFilesChecker
from app.checkers.exceptions import ConfigFileCheckerException

class Runner:

    MAX_PROCESSES = 5

    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {
        "results": os.path.join(WORKDIR, "results"),
        "errors":  os.path.join(WORKDIR, "errors")
    }

    SCRAPPERS = {
        "ogimet": OgimetMonthly,
        "wunderground": WundergroundMonthly,
        "meteociel": MeteocielMonthly,
        "meteociel_daily": MeteocielDaily
    }

    CHECKER = ConfigFilesChecker.instance()

    @classmethod
    def _run_wrapper(cls, config):

        scrapper_type = config["scrapper_type"]
        scrapper: MeteoScrapper = cls.SCRAPPERS[scrapper_type]()

        id = random.randint(0, 100_000)

        datafilename = "_".join([str(id), config['city'], scrapper_type, ".csv"]).lower()
        errorsfilename = "_".join([str(id), config['city'], scrapper_type, "_errors.json"]).lower()

        path_data = os.path.join(cls.PATHS["results"], datafilename)
        path_errors = os.path.join(cls.PATHS["errors"], errorsfilename)

        data = scrapper.scrap_from_config(config)

        if not data.empty:
            to_csv(data, path_data)

        if scrapper.errors:
            to_json(scrapper.errors, path_errors)

    @classmethod
    def run(cls):

        try:
            configs: dict = from_json(os.path.join(cls.WORKDIR, "config.json"))
            cls.CHECKER.check(configs)
        except FileNotFoundError:
            # from_json ne trouve pas le fichier
            print("ERREUR : pas de fichier config.json")
            return
        except JSONDecodeError:
            # from_json n'arrive pas à lire le fichier
            print("ERREUR : le fichier config est mal formé, impossible de charger un format json.")
            return
        except ConfigFileCheckerException as e:
            # le checker a trouvé un problème avec le fichier
            print(e)
            return

        all_configs = []

        for scrapper_type in {x for x in configs.keys() if x != "waiting"}:

            for config in configs[scrapper_type]:

                config["scrapper_type"] = scrapper_type

                try:
                    config["waiting"] = configs["waiting"]
                except KeyError:
                    config["waiting"] = 2

                all_configs.append(config)

        with ProcessPoolExecutor(max_workers=cls.MAX_PROCESSES) as executor:
            executor.map(cls._run_wrapper, all_configs)
