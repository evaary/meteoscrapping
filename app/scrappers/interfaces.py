import pandas as pd
from abc import abstractmethod, abstractstaticmethod
from requests_html import HTMLSession, Element
from requests import Response
from requests.exceptions import ConnectionError

class ScrapperInterface:
    """
    Une interface compilant les méthodes destinées à récupérer une page html,
    identifier le tableau de données et scrapper les data.
    """
    @staticmethod
    def _load_html_page(url: str, waiting: int) -> Response:
        """
        Charge la page html où se trouvent les données à récupérer.

        @param url : L'url de la page contenant le tableau de données
        @param waiting : Le temps à attendre pour que les données soient disponibles sur la page (wunderground et ogimet).
        @return La page html
        """
        # On tente max 3 fois de charger la page à l'url donnée. Si le chargement réussit, on garde la page.
        # Sinon, on la déclare inexistante. A l'origine, cela sert à palier de mauvaises connexions internet.
        html_page = None

        with HTMLSession() as session:

            for _ in range(3):

                try:
                    html_page = session.get(url) # long

                    if html_page.status_code == 200:
                        html_page.html.render(sleep=waiting, keep_page=True, scrolldown=1)
                        break

                except ConnectionError:
                    html_page = None

        if(html_page is None):
            raise ValueError()

        return html_page

    @staticmethod
    def _find_table_in_html(html_page: Response, criteria: "tuple[str, str]") -> Element:
        """
        Extrait la table html contenant les données à récupérer à l'url retournée par _load_html_page.

        @param html_page : La page html contenant le tableau de données.
        @param criteria : L'attribut css et sa valeur permettant d'identifier la table à récupérer.
        @return La table html contenant les données.
        """
        # (1) Le critère permet d'identifier le tableau que l'on cherche dans la page html.
        #     Il se compose d'un attribut html et de sa valeur.
        # (2) On cherche une table html correspondant au critère parmi toutes celles de la page.
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
        Récupération des noms des colonnes du tableau issu de _find_table_in_html.

        @param table : Le tableau html.
        @return La liste des noms des colonnes.
        """
        pass

    @abstractstaticmethod
    def _scrap_columns_values(table: Element) -> "list[str]":
        """
        Récupération des valeurs du tableau sous forme de liste de str.

        @param table : Le tableau html retourné par _find_table_in_html.
        @return La liste des valeurs contenues dans la table.
        """
        pass

    @abstractmethod
    def _rework_data(self, values: "list[str]", columns_names: "list[str]", parameters: dict) -> pd.DataFrame:
        """
        Mise en forme du tableau de données.

        @param values : La liste des valeurs retournée par _scrap_columns_values.
        @param column_names : La liste des noms de colonnes retournée par _scrap_columns_names.
        @param parameters : dict contenant les paramètres du job.
        @return Le dataframe équivalent au tableau de données html.
        """
        pass



class ConfigScrapperInterface:
    """
    Une interface pour exploiter un fichier de configuration.
    """
    @abstractmethod
    def scrap_from_config(self, config: dict) -> pd.DataFrame:
        """
        Récupération de données à partir d'un fichier de configuration.

        @param config : Le dictionnaire issu d'un fichier config.
        @return Le dataframe des données pour toutes les dates contenues dans la config.
        """
        pass

    @abstractmethod
    def _build_parameters_generator(self, config: dict) -> "tuple[dict]":
        """
        Création du générateur de paramètres.

        @param config : Le dictionnaire issu d'un fichier config.
        @return Un tuple contenant les paramètres des jobs à traiter.
        """
        pass

    @abstractmethod
    def _build_url(self, parameters: dict) -> str:
        """
        Reconstruction de l'url où se trouvent les données à récupérer.

        @param parameters : Le dictionnaire contenant les paramètres d'un job.
        @return L'url complète au format str du tableau de données à récupérer.
        """
        pass
