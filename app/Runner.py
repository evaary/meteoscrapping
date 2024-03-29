import multiprocessing as mp
import os

from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.ucs.UserConfigFile import UserConfigFile
from app.ucs.ucs_module import ScrapperUC
from app.ucs.ucf_checker_exceptions import UCFCheckerException
from app.boite_a_bonheur.utils import to_csv, to_json
from app.scrappers.scrappers_module import MeteoScrapper


class Runner:
    # TODO faire passer ce truc dans GeneralParmetersUC
    MAX_PROCESSES = 1 if mp.cpu_count() == 1 else (mp.cpu_count() - 1) * 2

    REPERTORIES = {"data": "resultats",
                   "errors": "erreurs"}

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
        workdir = os.getcwd()
        start_date = f"{uc.months[0]}_{uc.years[0]}"
        end_date = f"{uc.months[-1]}_{uc.years[-1]}"
        if uc.scrapper_type in ScrapperType.hourly_scrapper_types():
            start_date = f"{uc.days[0]}_{start_date}"
            end_date = f"{uc.days[-1]}_{end_date}"

        base_filename = "_".join([uc.scrapper_type.name,
                                  uc.city,
                                  f"du_{start_date}",
                                  f"au_{end_date}"])\
                           .lower()

        data_filename = os.path.join(workdir,
                                     cls.REPERTORIES["data"],
                                     base_filename + ".csv")

        errors_filename = os.path.join(workdir,
                                       cls.REPERTORIES["errors"],
                                       base_filename + ".json")
        scrapper = MeteoScrapper.scrapper_instance(uc)
        data = scrapper.scrap_from_uc(uc)

        if not data.empty:
            to_csv(data, data_filename)

        if scrapper.errors:
            to_json(scrapper.errors, errors_filename)

    @classmethod
    def run_from_config(cls) -> None:

        try:
            print("lecture du fichier config.json...")
            ucf = UserConfigFile.from_json(os.path.join(os.getcwd(), "config.json"))
        except UCFCheckerException as e:
            print(e)
            input("Tapez 'Entrée' pour quitter")
            return

        print("fichier config.json trouvé, lancement des téléchargements\n")
        
        for uc in ucf.get_all_ucs():
            cls._run_one_job(uc)
