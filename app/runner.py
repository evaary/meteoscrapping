import os

from app.data_managers import from_json, to_csv, to_json
from app.scrappers.meteociel_scrappers import MeteocielDailyScrapper, MeteocielScrapper
from app.scrappers.wunderground_scrapper import WundergroundScrapper
from app.scrappers.ogimet_scrapper import OgimetScrapper
from app.ConfigFileChecker import ConfigFilesChecker

class Runner:

    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {
        "results": os.path.join(WORKDIR, "results"),
        "errors":  os.path.join(WORKDIR, "errors")
    }

    SCRAPPERS = {
        "ogimet": OgimetScrapper.instance(),
        "wunderground": WundergroundScrapper.instance(),
        "meteociel": MeteocielScrapper.instance(),
        "meteociel_daily": MeteocielDailyScrapper.instance()
    }

    CHECKER = ConfigFilesChecker.instance()

    JOB_ID = 0

    @classmethod
    def run(cls):
        
        try:
            configs = from_json(os.path.join(cls.WORKDIR, "config.json"))
        except FileNotFoundError:
            print("pas de fichier config.json")
            return
        
        cls.CHECKER.run(configs)

        if not cls.CHECKER.is_legal:
            print(cls.CHECKER.error)
            return
        
        for scrapper_type in {x for x in configs.keys() if x != "waiting"}:
            
            todos = configs[scrapper_type]
            scrapper = cls.SCRAPPERS[scrapper_type]

            for config in todos:

                cls.JOB_ID += 1

                try:
                    config["waiting"] = configs["waiting"]
                except KeyError:
                    config["waiting"] = 3

                scrapper = scrapper.from_config(config)
                
                path_data = os.path.join(cls.PATHS["results"], f"{config['city']}_{scrapper_type}_{cls.JOB_ID}.csv")
                path_errors = os.path.join(cls.PATHS["errors"], f"{config['city']}_{scrapper_type}_{cls.JOB_ID}_errors.json")

                data = scrapper.run()
                errors = scrapper.errors

                if data:
                    to_csv(data, path_data)
                
                if errors:
                    to_json(errors, path_errors)

                print("\n")
