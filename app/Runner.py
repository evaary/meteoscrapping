from datetime import datetime
import os

from json.decoder import JSONDecodeError
from app.data_managers import from_json, to_csv, to_json
from app.scrappers.abcs import MeteoScrapper
from app.scrappers.meteociel_scrappers import MeteocielDaily, MeteocielMonthly
from app.scrappers.wunderground_scrapper import WundergroundMonthly
from app.scrappers.ogimet_scrapper import OgimetMonthly
from app.ConfigFileChecker import ConfigFilesChecker, ConfigCheckerException

class Runner:

    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {
        "results": os.path.join(WORKDIR, "results"),
        "errors":  os.path.join(WORKDIR, "errors")
    }

    SCRAPPERS: "dict[str, MeteoScrapper]" = {
        "ogimet": OgimetMonthly(),
        "wunderground": WundergroundMonthly(),
        "meteociel": MeteocielMonthly(),
        "meteociel_daily": MeteocielDaily()
    }

    CHECKER = ConfigFilesChecker.instance()

    @classmethod
    def run(cls):

        try:
            configs = from_json(os.path.join(cls.WORKDIR, "config.json"))
            cls.CHECKER.check(configs)
        except FileNotFoundError:
            # from_json ne trouve pas le fichier
            print("pas de fichier config.json")
            return
        except JSONDecodeError:
            # from_json n'arrive pas à lire le fichier
            print("le fichier config est mal formé, impossible de charger un format json.")
            return
        except ConfigCheckerException as e :
            # le checker a trouvé un problème avec le fichier
            print(e)
            return

        for scrapper_type in {x for x in configs.keys() if x != "waiting"}:

            scrapper = cls.SCRAPPERS[scrapper_type]

            for config in configs[scrapper_type]:

                try:
                    config["waiting"] = configs["waiting"]
                except KeyError:
                    config["waiting"] = 3

                date = str( int( datetime.now().timestamp() ) )

                datafilename = "_".join([date, config['city'], scrapper_type, ".csv"]).lower()
                errorsfilename = "_".join([date, config['city'], scrapper_type, "_errors.json"]).lower()

                path_data = os.path.join(cls.PATHS["results"], datafilename)
                path_errors = os.path.join(cls.PATHS["errors"], errorsfilename)

                data = scrapper.scrap_from_config(config)
                errors = scrapper.errors

                if not data.empty:
                    to_csv(data, path_data)

                if errors:
                    to_json(errors, path_errors)

                print("\n")
