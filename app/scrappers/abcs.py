from abc import ABC, abstractmethod
import pandas as pd
from app.scrappers.exceptions import HtmlPageException, HtmlTableException, ReworkException, ScrapException
from app.scrappers.interfaces import ConfigScrapperInterface

class MeteoScrapper(ABC, ConfigScrapperInterface):

    """
    Scrapper de base.

    Une fois instancié, appeler scrap_from_config ou scrap_from_url pour récupérer les données.
    """
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

    def __init__(self):
        self.errors = dict()
        self._city = ""
        self._waiting = 3
        self._url = ""

    def _reinit(self) -> None:
        """Réinitialise les paramètres du scrapper."""
        self.errors.clear()
        self._city = ""
        self._waiting = 3
        self._url = ""

    # Méthodes publiques
    def scrap_from_config(self, config):

        """Récupération de données à partir d'un fichier de configuration."""

        # (1) Remise à 0 des paramètres du scrapper.
        # (2) Mise à jour des paramètres avec les nouvelles données.
        # (3) Récupération des données.
        # (4) En cas de problème on signale l'étape qui est en échec et on sauvegarde l'erreur.

        # (1)
        self._reinit()

        # (2)
        self._city = config["city"]
        self._update_specific_parameters_from_config(config)

        try:
            self._waiting = config["waiting"]
        except KeyError:
            pass

        data = pd.DataFrame()

        for dates_parameters in self._create_dates_generator(config):

            self.__dict__.update(dates_parameters)

            key = self._build_key()

            self._url = self._build_url()

            print(self)

            try:
                # (3)
                data = pd.concat([data, self._scrap()])
            except Exception as e:
                # (4)
                print(str(e))
                self.errors[key] = {"url": self._url, "error": str(e)}
                continue

        return data

    def scrap_from_url(self, url):
        """
        Récupération de données à l'url fournie.

        @param l'url à lquelle se trouvent les données à récupérer
        @return le dataframe contenant les données.
        """

        self._reinit()
        self._update_parameters_from_url(url)
        try:
            data = self._scrap()
        except Exception as e:
            print(str(e))
            data = pd.DataFrame()

        return data

    # Utilitaires
    @abstractmethod
    def _update_parameters_from_url(self, url: str) -> None:
        """
        Mise à jour des paramètres du scrapper à partir d'une url.
        Implémentée dans chaque scrapper concrêt.

        @param l'url passée par l'utilisateur.
        """
        pass

    @abstractmethod
    def _update_specific_parameters_from_config(self, config: dict) -> None:
        """
        Mise à jour des paramètres spécifiques à chaque scrapper concrêt.
        Utilisé lors de la récupération de données via un fichier config.
        Implémentée dans chaque scrapper concrêt.
        """
        pass

    @abstractmethod
    def _build_key(self) -> str:
        """
        Création de la clé au format city_yyyy_mm_dd pour sauvegarder les erreurs (dict).
        Implémentée dans les Monthly / Daily Scrapper.

        @return la clé" du dict errors.
        """
        pass

    # Méthode principale
    def _scrap(self) -> pd.DataFrame:

        """
        Récupération des données contenues dans une page html à partir de son url.
        La variable CRITERIA est créée dans chaque scrapper concrêt.

        @return le dataframe contenant les données.
        """

        try:
            html_page = self._load_html_page(self._url, self._waiting)
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
            df = self._rework_data(values, col_names)
        except Exception:
            raise ReworkException()

        return df



class MonthlyScrapper(MeteoScrapper):
    """Scrapper spécialisé dans la récupération de données mensuelles."""

    def __init__(self):

        super().__init__()

        self._year = -1
        self._month = -1

        self._year_str = ""
        self._month_str = ""

    def _reinit(self):

        super().__init__()

        self._year = -1
        self._month = -1

        self._year_str = ""
        self._month_str = ""

    def _create_dates_generator(self, config):

        return (

            {
                "_year": year,
                "_month": month,
                "_year_str": str(year),
                "_month_str": "0" + str(month) if month < 10 else str(month)
            }

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)
        )

    def _build_key(self):
        return f"{self._city}_{self._year_str}_{self._month_str}"

    # Dunder methods
    def __repr__(self):
        date = f"{self._month_str}/{self._year_str}"
        return f"<{self.__class__.__name__} ville: {self._city}, date: {date}, url: {self._url}>"



class DailyScrapper(MeteoScrapper):
    """Scrapper spécialisé dans la récupération de données quotidiennes."""

    def __init__(self):

        super().__init__()

        self._year = -1
        self._month = -1
        self._day = -1

        self._year_str = ""
        self._month_str = ""
        self._day_str = ""

    def _reinit(self):

        super()._reinit()

        self._year = -1
        self._month = -1
        self._day = -1

        self._year_str = ""
        self._month_str = ""
        self._day_str = ""

    def _create_dates_generator(self, config):

        return (

            {
                "_year": year,
                "_month": month,
                "_day": day,

                "_year_str": str(year),
                "_month_str": "0" + str(month) if month < 10 else str(month),
                "_day_str": "0" + str(day) if day < 10 else str(day)
            }

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)

            for day in range(config["day"][0],
                             config["day"][-1] + 1)

            if day <= self.DAYS[month]
        )

    def _build_key(self):
        return f"{self._city}_{self._year_str}_{self._month_str}_{self._day_str}"

    # Dunder methods
    def __repr__(self):
        date = f"{self._day_str}/{self._month_str}/{self._year_str}"
        return f"<{self.__class__.__name__} ville: {self._city}, date: {date}, url: {self._url}>"
