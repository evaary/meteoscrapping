from abc import ABC

import pandas as pd

from app.job_parameters import JobParameters
from app.scrappers.exceptions import (HtmlPageException, HtmlTableException,
                                      ReworkException, ScrapException)
from app.scrappers.interfaces import Scrapper


class MeteoScrapper(ABC, Scrapper):

    def __init__(self):
        self.errors = dict()

    def scrap_from_config(self, config: dict) -> pd.DataFrame:

        data = pd.DataFrame(columns=["date"])

        for parameters in self._build_parameters_generator(config):

            print(parameters.url)

            try:
                # (3)
                data = pd.concat( [data, self._scrap(parameters)] )
            except Exception as e:
                # (4)
                print(str(e))
                self.errors[parameters.key] = {"url": parameters.url, "error": str(e)}
                continue

        data.sort_index()

        return data

    def _scrap(self, parameters: JobParameters) -> pd.DataFrame:

        """
        Récupération des données contenues dans une page html à partir de son url.

        @return le dataframe contenant les données.
        """

        try:
            html_page = self._load_html_page(parameters.url, parameters.waiting)
        except Exception:
            raise HtmlPageException()

        try:
            table = self._find_table_in_html(html_page, parameters.criteria)
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
