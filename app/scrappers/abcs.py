from abc import ABC, abstractmethod
import pandas as pd
from app.scrappers.interfaces import ScrappingToolsInterface

class MeteoScrapper(ABC, ScrappingToolsInterface):

    '''
    Scrapper de base.

    Après instanciation, initialiser les attributs du scrapper avec update(config).
    Une fois initialisé, appeler scrap() pour récupérer les données.

    Cette classe implémente la ScrappingToolsInterface qui contient les méthodes permettant de
    scrapper les pages html.

    Elle définit le processus de récupération des données avec et certains outils à implémenter.
    '''

    # (1) Nombre de jours dans chaque mois.
    #     Wunderground et météociel récupèrent le 29ème jour de février s'il existe.
    # (2) Dictionnaire contenant les messages à afficher en cas d'erreur

    # (1)
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

    # (2)
    ERROR_MESSAGES = {
        "load": "erreur lors du chargement de la page html",
        "search": "aucun tableau de données trouvé",
        "scrap": "erreur lors de la récupération des données",
        "rework": "erreur lors du traitement des données"
    }

    # Constructeur
    def __init__(self):
        self.errors = dict()
        self._todos = tuple()
        self._city = ""
        self._waiting = 3
        self._url = ""

    # Méthodes publiques
    def update(self, config: dict) -> None:
        '''
        Mise à jour des variables d'instance à partir d'une configuration json.

        @param config - infos qui permettront de reconstruire l'url.
        '''
        self.errors.clear()
        self._url = ""
        self._city = config["city"]
        self._waiting = config["waiting"]

    def scrap(self) -> pd.DataFrame:

        '''
        Méthode pour démarrer le scrapping.
        '''

        try:
            data = next(self._generate_data())

            for df in self._generate_data():
                data = pd.concat([data, df])

        except StopIteration:
            data = pd.DataFrame()

        return data

    # Méthodes privées
    def _register_error(self, key: str, url: str, message: str) -> None:
        '''
        Garder une trace d'une erreur et la signaler.

        @params
            key - identifiant d'un job pour une ville à une date donnée, fournit par build_key()
            url - l'url du tableau de données à récupérer
            message - le message à afficher et à enregistrer
        '''
        self.errors[key] = {"url": url, "error": message}
        print(f"\t{message}")

    @abstractmethod
    def _build_key(self, todo: tuple) -> str:
        '''
        Génère une str au format city_yyyy_mm_dd.
        Elle sert de clé pour sauvegarder les erreurs dans le dictionnaire errors.
        Cette fonction est implémentée dans les Monthly / Daily Scrappers.

        @param todo - Un tuple contenant 2 à 3 int : l'année, le mois, le jour.
                      Généré par update() dans les Monthly / Daily Scrappers.

        @return une str au format city_yyyy_mm_dd.
        '''

    @abstractmethod
    def _build_url(self, todo: tuple) -> str:
        '''
        Reconstruction de l'url où se trouvent les données à récupérer.
        Implémentée dans chaque scrapper concrêt.

        @param todo - Un tuple contenant 2 à 3 int : l'année, le mois, le jour.
                      Généré par update() dans les Monthly / Daily Scrappers.

        @return l'url complète au format str du tableau de données à récupérer.
        '''

    @abstractmethod
    def _rework_data(self, values: list, columns_names: "list[str]", todo: tuple) -> pd.DataFrame:
        '''
        Mise en forme du tableau de données. Implémentée dans chaque scrapper concrêt.

        @params
            values - La liste des valeurs contenues dans le tableau.
            column_names - La liste des noms de colonnes.
            todo - Un tuple contenant 2 à 3 int : l'année, le mois, le jour.
                   Généré par update() dans les Monthly / Daily Scrappers.

        @return le dataframe équivalent au tableau de données html.
        '''

    # Méthode principale
    def _generate_data(self) -> pd.DataFrame:

        '''Générateur des dataframes à enregistrer.'''
        # (1) On créé une clé de dictionnaire à partir du todo.
        # (2) On reconstitue l'url et on charge la page html correspondante.
        # (3) On récupère la table de données html.
        # (4) On récupère le noms des colonnes et les valeurs de la table de données html.
        # (5) On met les données sous forme de dataframe.
        #
        # A chaque étape, si un problème est rencontré, on le signale et on passe au todo suivant.

        for todo in self._todos:

            # (1)
            key = self._build_key(todo)

            # (2)
            url = self._build_url(todo)
            self._url = url
            print(todo , self)
            html_page = self._load_html_page(url, self._waiting)
            if html_page is None:
                self._register_error(key, url, self.ERROR_MESSAGES["load"])
                continue

            # (3)
            table = self._find_table_in_html(html_page, self.CRITERIA)
            if table is None:
                self._register_error(key, url, self.ERROR_MESSAGES["search"])
                continue

            # (4)
            try:
                col_names = self._scrap_columns_names(table)
                values = self._scrap_columns_values(table)
            except Exception:
                self._register_error(key, url, self.ERROR_MESSAGES["scrap"])
                continue

            # (5)
            try:
                df = self._rework_data(values, col_names, todo)
            except Exception:
                self._register_error(key, url, self.ERROR_MESSAGES["rework"])
                continue

            yield df

    # Dunder methods
    def __repr__(self):
        return f"<{self.__class__.__name__} ville:{self._city}, url:{self._url}>"

class MonthlyScrapper(MeteoScrapper):
    '''
    Scrapper spécialisé dans la récupération de données mensuelles.

    L'ensemble des dates à traiter est généré dans update().
    '''
    def update(self, config):

        super().update(config)

        self._todos = (

            (year, month)

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)
        )

    def _build_key(self, todo: "tuple[int, int]"):

        year, month = todo
        month = "0" + str(month) if month < 10 else str(month)

        return f"{self._city}_{year}_{month}"

class DailyScrapper(MeteoScrapper):
    '''
    Scrapper spécialisé dans la récupération de données quotidiennes.

    L'ensemble des dates à traiter est généré dans update().
    '''

    def update(self, config):

        super().update(config)

        self._todos = (

            (year, month, day)

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)

            for day in range(config["day"][0],
                             config["day"][-1] + 1)

            if self._check_day( (year, month, day) )
        )

    def _build_key(self, todo: "tuple[int, int, int]"):

        year, month, day = todo
        month = "0" + str(month) if month < 10 else str(month)
        day = "0" + str(day) if day < 10 else str(day)

        return f"{self._city}_{year}_{month}_{day}"

    def _check_day(self, todo: "tuple[int, int, int]") -> str:
        '''return False si on veut traiter un jour qui n'existe pas, comme le 31 février'''
        _, month, day = todo
        return False if day > self.DAYS[month] else True
