import pandas as pd
from abc import abstractmethod, abstractstaticmethod
from requests_html import HTMLSession, Element
from requests import Response
from requests.exceptions import ConnectionError

class ConfigScrapperInterface:

    """
    Une interface compilant les méthodes destinées à récupérer une page html,
    identifier le tableau de données et scrapper les data.
    """

    @abstractmethod
    def scrap_from_config(self, config: dict) -> pd.DataFrame:
        """
        Récupération de données à partir d'un fichier de configuration.

        @param un dict contenant les paramètres
        @return le dataframe des données pour toutes les dates contenues dans la config
        """
        pass

    @abstractmethod
    def _build_parameters_generator(self, config: dict) -> "tuple[dict]":
        """
        Création du générateur de paramètres.

        @param le dict contenant les paramètres
        @return un tuple contenant les dates à traiter.
        """
        pass

    @abstractmethod
    def _build_url(self, parameters: dict) -> str:
        """
        Reconstruction de l'url où se trouvent les données à récupérer.
        Implémentée dans chaque scrapper concrêt.

        @return l'url complète au format str du tableau de données à récupérer.
        """
        pass

    @staticmethod
    def _load_html_page(url: str, waiting: int) -> Response:

        """
        Charge la page html où se trouvent les données à récupérer

        @param
            url - l'url de la page contenant le tableau de données
            waiting - le temps que l'on doit attendre pour que le javascript s'éxecute
                      et que les données soient disponibles sur la page (wunderground et ogimet).

        @return la page html, ou None
        """
        # On tente max 3 fois de charger la page à l'url donnée. Si le chargement réussit, on garde la page.
        # Sinon, on la déclare inexistante. A l'origine, cela sert à palier de mauvaises connexions internet.
        html_page = None

        with HTMLSession() as session:

            for i in range(3):

                if(i > 0):
                    print("\tretrying...")

                try:
                    html_page = session.get(url) # long

                    if html_page.status_code == 200:
                        html_page.html.render(sleep=waiting, keep_page=True, scrolldown=1)
                        break

                except ConnectionError:
                    html_page = None

        return html_page

    @staticmethod
    def _find_table_in_html(html_page: Response, criteria: "tuple[str, str]") -> Element:

        """
        Extrait la table html contenant les données à récupérer.

        @param
            html_page - la page html contenant le tableau de données retourée par _load_html_page.
            criteria - l'attribut css et sa valeur permettant d'identifier la table à récupérer.

        @return la table html contenant les données.
        """
        # (1) Le critère permet d'identifier le tableau que l'on cherche dans la page html.
        #     Il se compose d'un attribut html et de sa valeur.
        # (2) On cherche une table html correspondant au critère parmis toutes celles de la page.
        #     On récupère la 1ère trouvée. Si on ne trouve pas de table, on la déclare inexistante.
        # (3) On vérifie que la table n'indique pas l'absence de données (spécifique à ogimet).
        #     Voir http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2016&mes=4&day=0&hora=0&min=0&ndays=31
        #     Si elle l'est, on déclare la table inexistante.

        # (1)
        attr, val = criteria

        # (2)
        try:
            table = [
                tab for tab in html_page.html.find("table")
                if attr in tab.attrs and tab.attrs[attr] == val
            ][0]
        except Exception:
            table = None
            return table

        # (3)
        try:
            condition = "no valid" in table.find("thead")[0].find("th")[0].text.lower().strip()
            table = None if condition else table
        except IndexError:
            pass

        return table

    @abstractstaticmethod
    def _scrap_columns_names(table: Element) -> "list[str]":
        """
        récupération des noms des colonnes

        @param le tableau html retourné par _find_table_in_html
        @return la liste des noms des colonnes.
        """
        pass

    @abstractstaticmethod
    def _scrap_columns_values(table: Element) -> "list[str]":
        """
        @param le tableau html retourné par _find_table_in_html.
        @return la liste des valeurs contenues dans la table.
        """
        pass

    @abstractmethod
    def _rework_data(self, values: "list[str]", columns_names: "list[str]", parameters: dict) -> pd.DataFrame:
        """
        Mise en forme du tableau de données. Implémentée dans chaque scrapper concrêt.

        @param
            values - La liste des valeurs contenues dans le tableau.
            column_names - La liste des noms de colonnes.

        @return le dataframe équivalent au tableau de données html.
        """
        pass
