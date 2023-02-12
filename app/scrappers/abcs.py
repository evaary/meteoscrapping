from abc import ABC
import pandas as pd
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

    def __init__(self):
        self.errors = dict()
        self._waiting = 1

    def scrap_from_config(self, config):

        """Récupération de données à partir d'un fichier de configuration."""

        data = pd.DataFrame(columns=["date"])

        try:
            self._waiting = config["waiting"]
        except KeyError:
            pass

        for parameters in self._build_parameters_generator(config):

            parameters["url"] = self._build_url(parameters)

            try:
                key = f"{parameters['city']}_{parameters['year_str']}_{parameters['month_str']}_{parameters['day_str']}"
            except KeyError:
                key = f"{parameters['city']}_{parameters['year_str']}_{parameters['month_str']}"

            print(parameters["url"])

            try:
                # (3)
                data = pd.concat([data, self._scrap(parameters)])
            except Exception as e:
                # (4)
                print(str(e))
                self.errors[key] = {"url": parameters["url"], "error": str(e)}

        data.sort_index()

        return data

    def _scrap(self, url, parameters) -> pd.DataFrame:

        """
        Récupération des données contenues dans une page html à partir de son url.
        La variable CRITERIA est créée dans chaque scrapper concrêt.

        @params
            url : l'adresse à scrapper
            parameters : le dictionnaire contenant les paramètres du job

        @return le dataframe contenant les données.
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
