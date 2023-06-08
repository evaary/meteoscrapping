from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
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

    MAX_PROCESSES = 1 if mp.cpu_count() == 1 else mp.cpu_count() - 1

    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {
        "results": os.path.join(WORKDIR, "results"),
        "errors":  os.path.join(WORKDIR, "errors")
    }

    SCRAPPERS = {
        # "ogimet": OgimetMonthly,
        "wunderground": WundergroundMonthly,
        # "meteociel": MeteocielMonthly,
        # "meteociel_daily": MeteocielDaily
    }

    CHECKER = ConfigFilesChecker.instance()

    @classmethod
    def stop(cls):
        print("arrêt du programme sur demande de l'utilisateur")
        for active_process in mp.active_children():
            active_process.terminate()

    @classmethod
    def _rework_config(cls, global_config: dict) -> "list[dict]":
        """
        Exploitation du fichier config, transformation en liste de configuration.
        @param config : Le dict contenu dans un fichier config.
        @return La liste des configs à traiter.
        """
        all_configs = []

        try:
            waiting = global_config["waiting"]
        except KeyError:
            waiting = MeteoScrapper.MIN_WAITING

        for scrapper_type in {x for x in global_config.keys() if x != "waiting"}:

            for job_config in global_config[scrapper_type]:

                job_config["scrapper_type"] = scrapper_type
                job_config["waiting"] = waiting

                all_configs.append(job_config)

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

        # if not data.empty:
        to_csv(data, path_data)

        if scrapper.errors:
            to_json(scrapper.errors, path_errors)

    @classmethod
    def run_from_config(cls) -> None:
        """
        Lancement de jobs en parallèle.
        """
        mp.freeze_support() # pour ne pas que le main se relance en boucle

        try:
            print("lecture du fichier config.json...")
            global_config: dict = from_json(os.path.join(cls.WORKDIR, "config.json"))
            cls.CHECKER.check(global_config)
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

        print("fichier config.json trouvé, lancement des téléchargements\n")

        configs = cls._rework_config(global_config)

        with ProcessPoolExecutor(max_workers=cls.MAX_PROCESSES) as executor:
            executor.map(cls._run_one_job, configs)
