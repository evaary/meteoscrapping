from abc import ABC
import pandas as pd
from multiprocessing import current_process
import app.scrappers.exceptions as scrapex
from app.scrappers.interfaces import ScrapperInterface, ConfigScrapperInterface
from requests.exceptions import RequestException, ConnectionError

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
        self._done += 1
        progress = round(self._done / self._todo * 100)

        if(progress % 10 == 0 and progress != self._progress):
            self._progress = progress
            return True

        return False

    def _print_progress(self) -> None:
        print(f"{self.__class__.__name__} ({current_process().pid}) - {self._progress}%\n")

    def _scrap(self, url, parameters) -> pd.DataFrame:
        """
        Récupération des données contenues dans une page html à partir de son url.
        La variable CRITERIA est créée dans chaque scrapper concrêt.

        @param url : L'adresse à scrapper.
        @param parameters : Le dictionnaire contenant les paramètres du job.
        @return Le dataframe contenant les données.
        @raise HtmlPageException si la page html n'a pas été récupérée.
        @raise HtmlTableException si la table html n'a pas été trouvée.
        @raise ScrapException si les valeurs de la tables n'ont pas été récupérées.
        @raise ReworkException si les données n'ont pas pu être traitées.
        """
        try:
            html_page = self._load_html_page(url, self._waiting)
        except (RequestException,
                ConnectionError):
            raise scrapex.HtmlPageException()

        try:
            table = self._find_table_in_html(html_page, self.CRITERIA)
        except (ValueError,
                IndexError):
            raise scrapex.HtmlTableException()

        try:
            col_names = self._scrap_columns_names(table)
            values = self._scrap_columns_values(table)
        except (AttributeError,
                IndexError):
            raise scrapex.ScrapException()

        try:
            df = self._rework_data(values, col_names, parameters)
        except (AttributeError,
                IndexError,
                KeyError):
            raise scrapex.ReworkException()

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
            except scrapex.ProcessException as e:
                self.errors[key] = {"url": url, "error": str(e)}
                self._upate_progress()
                continue

            # (7)
            is_updated = self._upate_progress()
            if(is_updated):
                self._print_progress()

        return data
