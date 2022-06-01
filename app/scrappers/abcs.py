from abc import ABC, abstractmethod
import pandas as pd
from app.scrappers.interfaces import ScrappingToolsInterface

class MeteoScrapper(ABC, ScrappingToolsInterface):

    '''
    Scrapper de base, qui doit être configuré à partir d'une configuration avec from_config.

    Les méthodes instance, from_config et get_data sont destinées à être directement utilisées
    par l'utilisateur. Les autres sont des méthodes internes au scrapper.

    La méthode importante est scrap_data qui fixe l'enchainement des actions à réaliser pour 
    récupérer les données et exploite toutes les autres méthodes.

    scrap_data est déclenchée par l'appel à la méthode get_data par l'utilisateur.

    Les autres méthodes sont des utilitaires permettant de réaliser des opérations simples.
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
        "loading": "error while loading html page",
        "searching": "no data table found",
        "scrapping": "error while scrapping data",
        "reworking": "error while reworking data"
    }
    
    # pattern singleton ************************************************************************************** 
    _instance = None

    def __init__(self):
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):
        cls._instance = cls.__new__(cls) if cls._instance is None else cls._instance
        return cls._instance
    
    #  **************************************************************************************
    def from_config(self, config: dict):
        '''
        Mise à jour des variables d'instance.
        
        @param config : un dictionnaire contenant la ville, la date, et autres infos propres à chaque scrapper
            qui permettront de reconstruire l'url.
        '''

        self.errors = {}
        self._city = config["city"]
        
        try:
            self._waiting = config["waiting"]
        except KeyError:
            self._waiting = 10

        return self
    
    def _register_error(self, key: str, url: str, message: str) -> None:
        '''
        Garder une trace d'une erreur et la signaler.
        
        @param key : une str identifiant un job pour une ville à une date donnée
        @param url : l'url du tableau de données à récupérer
        @param message : le message à afficher
        '''
        self.errors[key] = {"url": url, "error": message}
        print(f"\t{message}")
    
    @abstractmethod
    def _get_key(self, todo: tuple) -> str:
        '''
        Génère une str contenant la ville et la date (format city_yyyy_mm_dd).
        Elle sert de clé pour sauvegarder les erreurs dans le dictionnaire errors.
        Cette fonction est implémentée dans les scrappers quotidiens ou mensuels.
        
        @todo : un tuple contenant 2 à 3 int : l'année, le mois, le jour.
            Le tuple est issu de from_config dans les scrappers mensuels / quotidiens.

        @return : str au format city_yyyy_mm_dd.
        '''

    @abstractmethod
    def _set_url(self, todo: tuple) -> str:
        '''
        @todo : un tuple contenant 2 à 3 int : l'année, le mois, le jour
            le tuple est issu de from_config dans les scrappers mensuels / quotidiens

        @return : str, l'url complète au format str du tableau de données à récupérer.
        '''

    @abstractmethod
    def _rework_data(self) -> pd.DataFrame:
        '''Mise en forme du tableau de données.'''
    
    # **************************************************************************************
    def _scrap_data(self) -> pd.DataFrame:
        
        '''Générateur des dataframes à enregistrer.'''
        # (0) Pour éviter de chercher les data du 31 février, entre autre, pour les daily_scrapper
        # (1) On créé une clé de dictionnaire à partir du todo.
        # (2) On reconstitue l'url et on charge la page html correspondante.
        # (3) On récupère la table de données html.
        # (4) On récupère le noms des colonnes et les valeurs de la table de données html.
        # (5) On met les données sous forme de dataframe.
        #
        # A chaque étape, si un problème est rencontré, on le signale et on passe au todo suivant.
        
        for todo in self._todos:
            # (0)
            try:
                if not self._check_days(todo):
                    continue
            except AttributeError:
                pass
            # (1)
            key = self._get_key(todo)
            # (2)
            url = self._set_url(todo)
            
            html_page = self._get_html_page(url, self._waiting)
            if html_page is None:
                self._register_error(key, url, self.ERROR_MESSAGES["loading"])
                continue
            # (3)
            table = self._find_table_in_html(html_page, self.CRITERIA)
            if table is None:
                self._register_error(key, url, self.ERROR_MESSAGES["searching"])
                continue
            # (4)
            try:
                col_names = self._scrap_columns_names(table)
                values = self._scrap_columns_values(table)
            except Exception:
                self._register_error(key, url, self.ERROR_MESSAGES["scrapping"])
                continue
            # (5)
            try:
                df = self._rework_data(values, col_names, todo)
            except Exception:
                self._register_error(key, url, self.ERROR_MESSAGES["reworking"])
                continue

            yield df

    def get_data(self) -> pd.DataFrame:
        
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
    Complétion du from_config qui génère l'ensemble des couples année - mois à traiter,
    et implémentation du read_todo qui fournit l'année et le mois dans la clé.
    '''
    def from_config(self, config):
        
        super().from_config(config)

        self._todos = (
            (year, month)
            for year in range(config["year"][0], config["year"][-1] + 1)
            for month in range(config["month"][0], config["month"][-1] + 1)
        )

        return self

    def _get_key(self, todo):
        
        year, month = todo
        month = "0" + str(month) if month < 10 else str(month)
        
        return f"{self._city}_{year}_{month}"

class DailyScrapper(MeteoScrapper):
    '''
    Scrapper spécialisé dans la récupération de données quotidiennes.
    Complétion du from_config qui génère l'ensemble des trios année - mois - jour à traiter,
    et implémentation du read_todo qui fournit l'année, le mois et le jour dans la clé.
    Ajout d'une fonction permet également de passer les traitements de jours qui n'existent pas.
    '''

    def from_config(self, config):
        
        super().from_config(config)

        self._todos = (
            (year, month, day)
            for year in range(config["year"][0], config["year"][-1] + 1)
            for month in range(config["month"][0], config["month"][-1] + 1)
            for day in range(config["day"][0], config["day"][-1] + 1)
        )

        return self

    def _get_key(self, todo):
        
        year, month, day = todo
        month = "0" + str(month) if month < 10 else str(month)
        day = "0" + str(day) if day < 10 else str(day)
        
        return f"{self._city}_{year}_{month}_{day}"

    @classmethod
    def _check_days(cls, todo: tuple) -> str:
        '''return false si on veut traiter un jour qui n'existe pas, comme le 31 février'''
        _, month, day = todo
        return False if day > cls.DAYS[month] else True
