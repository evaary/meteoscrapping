import os
from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.UserConfigFile import UserConfigFile
from app.exceptions.ucf_checker_exceptions import UCFCheckerException
from app.boite_a_bonheur.utils import to_csv, to_json
from app.scrappers_module import MeteoScrapper
import multiprocessing as mp


class Main:

    DIRECTORIES = {"data": "resultats",
                   "errors": "erreurs"}

    @classmethod
    def run(cls) -> None:
        """lancer les téléchargements"""
        #   (1) Lecture du fichier config.
        #   (2) Pour chaque UC, on créé un nom de fichier pour le CSV (résultats) et pour le JSON (erreurs).
        #   (3) Instanciation du scrapper et téléchargement des données.
        #   (4) Enregistrement des résultats et des erreurs.

        # (1)
        try:
            print("lecture du fichier config.json...")
            ucf = UserConfigFile.from_json(os.path.join(os.getcwd(), "config.json"))
        except UCFCheckerException as e:
            print(e)
            input("Tapez 'Entrée' pour quitter")
            return
        except Exception as e:
            print("erreur : " + str(e))
            return

        print("fichier config.json trouvé, lancement des téléchargements\n")

        for uc in ucf.get_all_ucs():
            workdir = os.getcwd()
            start_date = f"{uc.months[0]}_{uc.years[0]}"
            end_date = f"{uc.months[-1]}_{uc.years[-1]}"
            is_one_date = False

            if uc.scrapper_type in ScrapperType.hourly_scrappers():
                start_date = f"{uc.days[0]}_{start_date}"
                end_date = f"{uc.days[-1]}_{end_date}"

            is_one_date = start_date == end_date

            if is_one_date:
                base_filename = "_".join([uc.scrapper_type.name,
                                          uc.city,
                                          start_date])\
                                    .lower()
            else:
                base_filename = "_".join([uc.scrapper_type.name,
                                        uc.city,
                                        f"du_{start_date}",
                                        f"au_{end_date}"])\
                                    .lower()

            data_filename = os.path.join(workdir,
                                         cls.DIRECTORIES["data"],
                                         base_filename + ".csv")

            errors_filename = os.path.join(workdir,
                                           cls.DIRECTORIES["errors"],
                                           base_filename + ".json")
            # (3)
            scrapper = MeteoScrapper.scrapper_instance(uc)
            data = scrapper.scrap_uc(uc)

            # (4)
            if not data.empty:
                to_csv(data, data_filename)

            if scrapper.errors:
                to_json(scrapper.errors, errors_filename)

    @staticmethod
    def stop() -> None:
        print("arrêt du programme sur demande de l'utilisateur")
        for active_process in mp.active_children():
            active_process.terminate()


if __name__ == "__main__":
    try:
        mp.freeze_support()  # pour ne pas que le main se relance en boucle
        Main.run()
    except KeyboardInterrupt:
        Main.stop()
