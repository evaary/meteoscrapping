import multiprocessing as mp
import os
import random
from concurrent.futures import ProcessPoolExecutor

from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.ucs.UserConfigFile import UserConfigFile
from app.ucs.ucs_module import ScrapperUC
from app.ucs.ucf_checker_exceptions import ConfigFileCheckerException
from app.boite_a_bonheur.utils import to_csv, to_json
from app.scrappers.abcs import MeteoScrapper
from app.scrappers.meteociel_scrappers import MeteocielHourly, MeteocielDaily
from app.scrappers.ogimet_scrappers import OgimetDaily
from app.scrappers.wunderground_scrappers import WundergroundDaily


class Runner:

    MAX_PROCESSES = 1 if mp.cpu_count() == 1 else (mp.cpu_count() - 1) * 2
    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {"resultats": os.path.join(WORKDIR, "resultats"),
             "erreurs": os.path.join(WORKDIR, "erreurs")}

    # Association entre le type de scrapper des UCs et le scrapper à instancier en lui même.
    # Les None ne posent pas de problème car lors de la lecture du fichier config,
    # on contrôle que tous les UCs sont bien pris en charge.
    SCRAPPERS = {ScrapperType.WUNDERGROUND_HOURLY: None,
                 ScrapperType.WUNDERGROUND_DAILY: WundergroundDaily,

                 ScrapperType.OGIMET_HOURLY: None,
                 ScrapperType.OGIMET_DAILY: OgimetDaily,

                 ScrapperType.METEOCIEL_HOURLY: MeteocielHourly,
                 ScrapperType.METEOCIEL_DAILY: MeteocielDaily}

    @classmethod
    def stop(cls) -> None:
        print("arrêt du programme sur demande de l'utilisateur")
        for active_process in mp.active_children():
            active_process.terminate()

    @classmethod
    def _run_one_job(cls, uc: ScrapperUC) -> None:
        """
        Traitement réalisé pour chaque UC du fichier config.
        @params
            uc : un jeu de paramètres wunderground, ogimet ou meteociel.
        """

        identifiant = random.randint(0, 10**9)

        data_filename = "_".join([str(identifiant),
                                  uc.scrapper_type.name,
                                  uc.city])\
                           .lower() + ".csv"

        data_filename = os.path.join(cls.PATHS["resultats"],
                                     data_filename)

        errors_filename = "_".join([str(identifiant),
                                    uc.scrapper_type.name,
                                    uc.city,
                                    "erreurs.json"])\
                             .lower()

        errors_filename = os.path.join(cls.PATHS["erreurs"],
                                       errors_filename)

        scrapper: MeteoScrapper = cls.SCRAPPERS[uc.scrapper_type]()
        data = scrapper.scrap_from_uc(uc)

        if not data.empty:
            to_csv(data, data_filename)

        if scrapper.errors:
            to_json(scrapper.errors, errors_filename)

    @classmethod
    def run_from_config(cls) -> None:

        mp.freeze_support()  # pour ne pas que le main se relance en boucle

        try:
            print("lecture du fichier config.json...")
            ucf = UserConfigFile.from_json(os.path.join(cls.WORKDIR, "config.json"))
        except ConfigFileCheckerException as e:
            print(e)
            return

        print("fichier config.json trouvé, lancement des téléchargements\n")

        with ProcessPoolExecutor(max_workers=cls.MAX_PROCESSES) as executor:
            executor.map(cls._run_one_job, ucf.get_all_ucs())
