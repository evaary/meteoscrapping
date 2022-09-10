from abc import ABC, abstractmethod
import pandas as pd
from app.scrappers.interfaces import ScrappingToolsInterface

class MeteoScrapper(ABC, ScrappingToolsInterface):

    '''
    C'est quoi :

        Scrapper de base, construit sur le modèle du singleton.

        Les méthodes instance(), update() et run() sont destinées à être appelées
        par l'utilisateur. Les autres méthodes sont des utilitaires permettant de 
        réaliser des opérations simples.

        La méthode importante est scrap_data() qui fixe l'enchainement des actions à réaliser pour 
        récupérer les données et exploite toutes les autres méthodes. scrap_data() est déclenchée par 
        l'appel à la méthode run() par l'utilisateur.

        Cette classe implémente la ScrappingToolsInterface qui contient les méthodes permettant de
        scrapper les pages html.

        Les scrappers abstraits suivants implémentent get_key() et complètent update().

    Comment ça marche :

        Un scrapper doit être instancié avec la méthode instance().
        Une fois le scraper instancié, la méthode update() permet de le configurer.
        Une fois configuré, la méthode run() récupère les données.

        Lors de l'étape de configuration, on créé toutes les combinaisons de (jours/)mois/années
        à traiter. A partir des infos de la config et des dates créées, 
        on reconstruit une par une les url contenant les données à récupérer.
    
        On charge ensuite la page html à l'url courante, on isole le tableau de données, on récupère
        les data et les noms de colonnes, on met le tout en forme (conversions d'unités etc...),
        on obtient 1 dataframe par url. On regroupe tous lmes dataframes en 1 seul qui est retourné.
    
    '''

    # nombre de jours dans chaque mois
    # wunderground et météociel récupèrent le 29ème jour de février s'il existe 
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

    # dictionnaire contenant les messages à afficher en cas d'erreur
    ERROR_MESSAGES = {
        "load": "erreur lors du chargement de la page html",
        "search": "aucun tableau de données trouvé",
        "scrap": "erreur lors de la récupération des données",
        "rework": "erreur lors du traitement des données"
    }

    def __init__(self):
        self.errors = dict()
        self._todos = tuple()
        self._city = ""
        self._waiting = 3
    
    # utilitaires **************************************************************************************
    def update(self, config: dict):
        '''
        Mise à jour des variables d'instance.
        
        @params
            config - infos qui permettront de reconstruire l'url.
        '''
        self.errors.clear()
        self._city = config["city"]
        self._waiting = config["waiting"]
    
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
        Cette fonction est implémentée dans les scrappers quotidiens ou mensuels.
        
        @param
            todo - un tuple contenant 2 à 3 int : l'année, le mois, le jour.
                   Généré par update() dans les Monthly / Daily Scrappers.

        @return une str au format city_yyyy_mm_dd.
        '''

    @abstractmethod
    def _build_url(self, todo: tuple) -> str:
        '''
        @todo : un tuple contenant 2 à 3 int : l'année, le mois, le jour
            le tuple est issu de update dans les scrappers mensuels / quotidiens

        @return : str, l'url complète au format str du tableau de données à récupérer.
        '''

    @abstractmethod
    def _rework_data(self) -> pd.DataFrame:
        '''Mise en forme du tableau de données.'''
    
    # méthodes principales **************************************************************************************
    def _scrap_data(self) -> pd.DataFrame:
        
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

    def run(self) -> pd.DataFrame:
        
        '''Réunit les dataframes en csv'''
        
        try:
            data = next(self._scrap_data())

            for df in self._scrap_data():
                data = pd.concat([data, df])
        
        except StopIteration:
            data = pd.DataFrame()
        
        return data

    # dunder methods **************************************************************************************
    def __repr__(self):
        return f"<{self.__class__.__name__} ville:{self._city}, url:{self._url}>"

class MonthlyScrapper(MeteoScrapper):

    '''
    Scrapper spécialisé dans la récupération de données mensuelles.
    Complétion du update qui génère l'ensemble des couples année - mois à traiter,
    et implémentation du read_todo qui fournit l'année et le mois dans la clé.
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
    Complétion du update qui génère l'ensemble des trios année - mois - jour à traiter,
    et implémentation du read_todo qui fournit l'année, le mois et le jour dans la clé.
    Ajout d'une fonction permet également de passer les traitements de jours qui n'existent pas.
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

            if self._check_day(year, month, day)
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
