import multiprocessing
from datetime import datetime
import os

from json.decoder import JSONDecodeError
from app.data_managers import from_json, to_csv, to_json
from app.scrappers.abcs import MeteoScrapper
from app.scrappers.meteociel_scrappers import MeteocielDaily, MeteocielMonthly
from app.scrappers.wunderground_scrappers import WundergroundMonthly
from app.scrappers.ogimet_scrappers import OgimetMonthly
from app.checkers.ConfigFileChecker import ConfigFilesChecker
from app.checkers.exceptions import ConfigFileCheckerException

class Runner:

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
    def launch_scrapping(cls, scrapper_type: str, config: dict) -> None:

        date = str( int( datetime.now().timestamp() ) )

        datafilename = "_".join([date, config['city'], scrapper_type, ".csv"]).lower()
        errorsfilename = "_".join([date, config['city'], scrapper_type, "_errors.json"]).lower()

        path_data = os.path.join(cls.PATHS["results"], datafilename)
        path_errors = os.path.join(cls.PATHS["errors"], errorsfilename)

        scrapper: MeteoScrapper = cls.SCRAPPERS[scrapper_type]()
        data = scrapper.scrap_from_config(config)

        if not data.empty:
            to_csv(data, path_data)

        if scrapper.errors:
            to_json(scrapper.errors, path_errors)

        print("\n")

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

        processes: list[multiprocessing.Process] = []

        for scrapper_type in {x for x in configs.keys() if x != "waiting"}:

            for config in configs[scrapper_type]:

                try:
                    config["waiting"] = configs["waiting"]
                except KeyError:
                    config["waiting"] = 3

                process = multiprocessing.Process(target=cls.launch_scrapping, args=[scrapper_type, config] )
                process.start()
                processes.append(process)

        for process in processes:
            process.join()
