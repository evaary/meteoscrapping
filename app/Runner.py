from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
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

    MAX_PROCESSES = cpu_count() - 1

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
    def _rework_configs(cls, configs: dict) -> "list[dict]":
        """
        Exploitation du fichier config, transformation en liste de configuration.
        @param config : Le dict contenu dans un fichier config.
        @return La liste des configs à traiter.
        """
        all_configs = []

        for scrapper_type in {x for x in configs.keys() if x != "waiting"}:

            for config in configs[scrapper_type]:

                config["scrapper_type"] = scrapper_type

                try:
                    config["waiting"] = configs["waiting"]
                except KeyError:
                    config["waiting"] = 3

                all_configs.append(config)

        return all_configs

    @classmethod
    def _run_one_job(cls, config) -> None:
        """
        Traitement réalisé pour chaque job du fichier config.
        @param config : le contenu du fichier config.
        """
        scrapper_type = config["scrapper_type"]
        scrapper: MeteoScrapper = cls.SCRAPPERS[scrapper_type]()

        id = random.randint(0, 10**6)

        datafilename = "_".join([str(id), config['city'], scrapper_type]).lower() + ".csv"
        errorsfilename = "_".join([str(id), config['city'], scrapper_type, "errors.json"]).lower()

        path_data = os.path.join(cls.PATHS["results"], datafilename)
        path_errors = os.path.join(cls.PATHS["errors"], errorsfilename)

        data = scrapper.scrap_from_config(config)

        if not data.empty:
            to_csv(data, path_data)

        if scrapper.errors:
            to_json(scrapper.errors, path_errors)

    @classmethod
    def run_from_config_in_parallele(cls) -> None:
        """
        Lancement de jobs en parallèle.
        """
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

        configs = cls._rework_configs(configs)

        with ProcessPoolExecutor(max_workers=cls.MAX_PROCESSES) as executor:
            executor.map(cls._run_one_job, configs)
