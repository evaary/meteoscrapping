from abc import ABC
import pandas as pd
from multiprocessing import current_process
from app.scrappers.exceptions import HtmlPageException, HtmlTableException, ReworkException, ScrapException
from app.scrappers.interfaces import ScrapperInterface, ConfigScrapperInterface

class MeteoScrapper(ABC,
                    ScrapperInterface,
                    ConfigScrapperInterface):

    # Nombre de jours dans chaque mois.
    # Wunderground et Météociel récupèrent le 29ème jour de février s'il existe.
    DAYS = {
        1  : 31,
        2  : 28,
        3  : 31,
        4  : 30,
        5  : 31,
        6  : 30,
        7  : 31,
        8  : 31,
        9  : 30,
        11 : 30,
        10 : 31,
        12 : 31,
    }

    MIN_WAITING = 3

    def __init__(self):
        self.errors = dict()
        try:
            self._current_process_number = int(current_process().name.split("-")[1])
        except:
            self._current_process_number = 1
        self._waiting = self.MIN_WAITING
        # quantité de jobs traités
        self._done = 0
        # quantité de jobs à traiter
        self._todo = -1
        # % de jobs traités (en multiple de 10%)
        self._progress = 0

    def _upate_progress(self) -> bool:
        """
        Avancement du job, en %.
        """
        progress = round(self._done / self._todo * 100)

        if(progress % 10 == 0 and progress != self._progress):
            self._progress = progress
            return True

        return False

    def _print_progress(self) -> None:
        print(f"{self.__class__.__name__} ({self._current_process_number}) - {self._progress}%")

    def _scrap(self, url, parameters) -> pd.DataFrame:
        """
        Récupération des données contenues dans une page html à partir de son url.
        La variable CRITERIA est créée dans chaque scrapper concrêt.

        @param url : L'adresse à scrapper.
        @param parameters : Le dictionnaire contenant les paramètres du job.
        @return Le dataframe contenant les données.
        """
        try:
            html_page = self._load_html_page(url, self._waiting)
        except Exception:
            raise HtmlPageException()

        try:
            table = self._find_table_in_html(html_page, self.CRITERIA)
        except Exception:
            raise HtmlTableException()

        try:
            col_names = self._scrap_columns_names(table)
            values = self._scrap_columns_values(table)
        except Exception:
            raise ScrapException()

        try:
            df = self._rework_data(values, col_names, parameters)
        except Exception:
            raise ReworkException()

        return df

    def scrap_from_config(self, config):
        # Implémentation de ConfigScrapperInterface.scrap_from_config

        # (1) Initialisation du résultat du job.
        # (2) Mise à jour du waiting et de la quantité de jobs à faire.
        # (3) Affichage de l'avancement initial, 0%.
        # (4) La config est convertie en liste de dictionnaires contenant chacun les paramètres
        #     permettant de récupérer les données d'1 adresse url.
        # (5) Reconstruction de l'url à partir des paramètres et création d'une clé pour enregistrer
        #     les erreurs dans un dict.
        # (6) Récupération des données à l'url, ou enregistrement des erreurs en cas d'échec.
        # (7) Mise à jour et affichage de l'avancement.

        # (1)
        data = pd.DataFrame(columns=["date"])

        # (2)
        try:
            self._waiting = config["waiting"] if config["waiting"] >= self.MIN_WAITING else self.MIN_WAITING
        except KeyError:
            pass

        self._todo = sum([1 for _ in self._build_parameters_generator(config)])

        # (3)
        self._print_progress()

        # (4)
        for parameters in self._build_parameters_generator(config):

            # (5)
            url = self._build_url(parameters)

            try:
                key = f"{parameters['city']}_{parameters['year_str']}_{parameters['month_str']}_{parameters['day_str']}"
            except KeyError:
                key = f"{parameters['city']}_{parameters['year_str']}_{parameters['month_str']}"

            # (6)
            try:
                data = pd.concat([data, self._scrap(url, parameters)])
            except Exception as e:
                self.errors[key] = {"url": url, "error": str(e)}

            # (7)
            self._done += 1
            has_updated = self._upate_progress()

            if(has_updated):
                self._print_progress()

        return data
