from abc import abstractmethod, abstractstaticmethod

import pandas as pd
from requests_html import Element, HTMLSession

from app.job_parameters import JobParameters
from app.scrappers.exceptions import HtmlPageException


class Scrapper:

    @abstractmethod
    def scrap_from_config(self, config: dict) -> pd.DataFrame:
        """
        Récupération de données à partir d'une config du fichier de configuration.

        @param
            config : une config du fichier de configuration

        @return
            le dataframe des données pour toutes les dates contenues dans la config
        """
        pass

    @abstractstaticmethod
    def _build_parameters_generator(config: dict) -> "tuple[JobParameters]":
        """
        Création du générateur de paramètres à partir de la config.

        @param
            config : une config du fichier de configuration

        @return
            un tuple contenant les paramètres du job à réaliser
        """
        pass

    @staticmethod
    def _load_html(parameters: JobParameters):

        try:

            with HTMLSession() as session:

                html_page = session.get(parameters.url)
                html_page.html.render( sleep=parameters.waiting,
                                       keep_page=True,
                                       scrolldown=1 )

            if html_page.status_code != 200:
                raise HtmlPageException()

        except Exception:
            raise HtmlPageException()

        attr, val = parameters.criteria

        # (2)
        table: Element = [ tab for tab in html_page.html.find("table")
                           if attr in tab.attrs and tab.attrs[attr] == val ][0]
        try:

            condition = "no valid" in table.find("thead")[0]\
                                           .find("th")[0]\
                                           .text\
                                           .lower()\
                                           .strip()

            table = None if condition else table

        except IndexError:
            pass

        if table is None:
            raise HtmlPageException()

        return table

    @abstractstaticmethod
    def _scrap_columns_names(table: Element) -> "list[str]":
        """
        Récupération des noms des colonnes du tableau issu de _find_table_in_html.

        @param
            table : le tableau html retourné par _find_table_in_html

        @return
            la liste des noms des colonnes.
        """
        pass

    @abstractstaticmethod
    def _scrap_columns_values(table: Element) -> "list[str]":
        """
        @param
            table : le tableau html retourné par _find_table_in_html.

        @return
            la liste des valeurs contenues dans la table.
        """
        pass

    @abstractmethod
    def _rework_data( self,
                      values: "list[str]",
                      columns_names: "list[str]",
                      parameters: JobParameters ) -> pd.DataFrame:
        """
        Mise en forme du tableau de données.

        @param
            values : La liste des valeurs contenues dans le tableau.
            column_names : La liste des noms de colonnes.
            parameters : les paramètres du job.

        @return
            le dataframe équivalent au tableau de données html.
        """
        pass
