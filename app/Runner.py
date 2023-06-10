import os
from datetime import datetime
from json.decoder import JSONDecodeError

from app.checkers.ConfigFileChecker import ConfigFilesChecker
from app.checkers.exceptions import ConfigFileCheckerException
from app.data_managers import from_json, to_csv, to_json
from app.scrappers.abcs import MeteoScrapper
from app.scrappers.meteociel_scrappers import MeteocielDaily, MeteocielMonthly
from app.scrappers.ogimet_scrappers import OgimetMonthly
from app.scrappers.wunderground_scrappers import WundergroundMonthly


class Runner:

    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {   "results": os.path.join(WORKDIR, "results"),
                "errors" : os.path.join(WORKDIR, "errors") }

    SCRAPPERS = {   "ogimet"         : OgimetMonthly,
                    "wunderground"   : WundergroundMonthly,
                    "meteociel"      : MeteocielMonthly,
                    "meteociel_daily": MeteocielDaily }

    CHECKER = ConfigFilesChecker.instance()

    @classmethod
    def _create_data_and_errors_filenames(cls, config: dict) -> "tuple[str]":

        """
        Création des paths des fichiers contenant les data, résultats du scrap, et les erreurs.

        @params
            config : une des configs du fichier config

        @return
            le tuple contenant les noms du fichiers de données et celui des erreurs
        """

        date = str( int( datetime.now().timestamp() ) )

        datafilename = "_".join( [ date,
                                   config["city"],
                                   config["scrapper"],
                                   ".csv" ] )\
                                .lower()

        errorsfilename = "_".join( [ date,
                                     config["city"],
                                     config["scrapper"],
                                     "_errors.json" ] )\
                            .lower()

        path_data = os.path.join(cls.PATHS["results"],
                                    datafilename)

        path_errors = os.path.join(cls.PATHS["errors"],
                                    errorsfilename)

        return (path_data, path_errors)



    @staticmethod
    def _get_all_configs(config_file: dict) -> "list[dict]":

        """
        Réunit toutes les configs du fichier config en une liste unique.

        @param
            config_file : le fichier config

        @return
            la liste de toutes les configs à traiter
        """

        all_configs = []

        for scrapper_type in config_file.keys():

            if scrapper_type == "waiting":
                continue

            all_scrapper_configs = config_file[scrapper_type]

            for one_config in all_scrapper_configs:
                one_config["scrapper"] = scrapper_type
                try:
                    one_config["waiting"] = config_file["waiting"]
                except KeyError:
                    pass

            all_configs.extend(all_scrapper_configs)

        return all_configs



    @classmethod
    def run(cls):

        # (1) Lecture et contôle du fichier config.
        # (2) le fichier config contient 1 champs waiting et les autres champs sont des noms de
        #     scrappers, associés à des listes. Ces listes contiennent les configs.
        #     Pour chaque config de chaque liste, on ajoute le waiting et le type de scrapper.
        #     Puis toutes les listes sont réunies en 1, all_configs.
        # (3) Pour chaque config, on instancie le scrapper correspondant et on lance la récupération de données.
        #     On enregistre les données récuéprées si elles existent et les erreurs rencontrées.

        # (1)
        try:
            config_file: dict = from_json(os.path.join(cls.WORKDIR, "config.json"))
            cls.CHECKER.check(config_file)
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

        # (2)
        # (3)
        for config in cls._get_all_configs(config_file):

            scrapper: MeteoScrapper = cls.SCRAPPERS[ config["scrapper"] ]()

            path_data, path_errors = cls._create_data_and_errors_filenames(config)

            data = scrapper.scrap_from_config(config)

            if not data.empty:
                to_csv(data, path_data)

            if scrapper.errors:
                to_json(scrapper.errors, path_errors)

            print("\n")
