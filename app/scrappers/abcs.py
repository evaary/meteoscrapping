from requests_html import HTMLSession
from abc import ABC, abstractmethod
import pandas as pd

class Singleton:

    _instance = None

    def __init__(self):
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):
        cls._instance = cls._instance if cls._instance is not None else cls.__new__(cls)
        return cls._instance

# entorse aux règles de l'héritage
class MeteoScrapper(Singleton, ABC):

    '''
    Scrapper de base.
    La méthode _scrap_data permet d'enchainer les actions à réaliser pour récupérer
    les tableaux de données.
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

    def from_config(self, config):
        '''mise à jour des variables d'instance'''

        self.errors = {}
        self._city = config["city"]
        try:
            self._waiting = config["waiting"]
        except KeyError:
            self._waiting = 10

        return self
    
    ### METHODES ABSTRAITES ###
    @abstractmethod
    def _read_todo(self, todo):
        '''récupération de la clé pour sauvegarder les erreurs dans le dictionnaire errors'''

    @abstractmethod
    def _set_url(self, year, month):
        '''return l'url complète au format str'''

    @abstractmethod
    def _scrap_columns_names(table):
        '''return la liste des noms des colonnes du tableau de données (list de str)'''
    
    @abstractmethod
    def _scrap_columns_values(table):
        '''return la liste des valeurs du tableau de données (list de str)'''

    @abstractmethod
    def _rework_data(self):
        '''mise en forme du tableau de données, return un dataframe pandas'''

    ### METHODES CONCRETES ###
    def _register_error(self, key, url, message):
        self.errors[key] = {"url": url, "error": message}
        print(f"\t{message}")

    def _get_html_page(self, url):
        
        '''_get_html_page : charge la page internet où se trouvent les données à récupérer
            args: url (string)
            return: html_page (requests.Response ou None, voir doc requests python)
        '''
        # (1) Instanciation de l'objet qui récupèrera le code html. i est le nombre de tentatives de connexion.
        # (2) On tente max 3 fois de charger la page à l'url donnée. Si le chargement réussit, on garde la page. 
        #     Sinon, on la déclare inexistante.
        #     waiting nécéssaire pour charger les données sur wunderground et ogimet.
        # (1)
        html_page = None
        i = 0
        with HTMLSession() as session:
        # (2)
            while(html_page is None and i < 3):
                i += 1
                if(i > 1):
                    print("\tretrying...")
                try:
                    html_page = session.get(url) # long
                    html_page.html.render(sleep=self._waiting, keep_page=True, scrolldown=1)
                except Exception:
                    html_page = None

        return html_page

    @classmethod
    def _find_table_in_html(cls, html_page):
        
        '''_find_table_in_html : extrait la table html contenant les données à récupérer
            args:
                html_page (requests.Response)
            return: table (requests-html.Element ou None, voir doc requests-html python)
        '''
        # (1) Le critère permet d'identifier le tableau que l'on cherche dans la page html.
        #     Il se compose d'un attribut html et de sa valeur.
        # (2) On cherche une table html correspondant au critère parmis toutes celles de la page.
        #     On récupère la 1ère trouvée. Si on ne trouve pas de table, on la déclare inexistante.  
        # (3) On vérifie que la table n'indique pas l'absence de données (spécifique à ogimet).
        #     Voir http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2016&mes=4&day=0&hora=0&min=0&ndays=31
        #     Si elle l'est, on déclare la table inexistante.
        
        # (1)
        attr, val = cls.CRITERIA
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

    def _scrap_data(self):
        
        '''_scrap_data : générateur des dataframes à enregistrer.'''
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
            key = self._read_todo(todo)
            # (2)
            url = self._set_url(todo)
            
            html_page = self._get_html_page(url)
            if html_page is None:
                self._register_error(key, url, "error while loading html page")
                continue
            # (3)
            table = self._find_table_in_html(html_page)
            if table is None:
                self._register_error(key, url, "no data table found")
                continue
            # (4)
            try:
                col_names = self._scrap_columns_names(table)
                values = self._scrap_columns_values(table)
            except Exception:
                self._register_error(key, url, "error while scrapping data")
                continue
            # (5)
            try:
                df = self._rework_data(values, col_names, todo)
            except Exception:
                self._register_error(key, url, "error while reworking data")
                continue

            yield df

    def get_data(self):
        
        '''get_data : réunit les dataframes en csv'''
        
        try:
            data = next(self._scrap_data())

            for df in self._scrap_data():
                data = pd.concat([data, df])
        
        except StopIteration:
            data = pd.DataFrame()
        
        return data

    ### DUNDER METHODS ###
    def __repr__(self):
        return f"<{self.__class__.__name__} ville:{self._city}, url:{self._url}>"

class MonthlyScrapper(MeteoScrapper):

    def from_config(self, config):
        
        super().from_config(config)

        self._todos = (
            (year, month)
            for year in range(config["year"][0], config["year"][-1] + 1)
            for month in range(config["month"][0], config["month"][-1] + 1)
        )

        return self

    def _read_todo(self, todo):
        
        year, month = todo
        month = "0" + str(month) if month < 10 else str(month)
        
        return f"{self._city}_{year}_{month}"

class DailyScrapper(MeteoScrapper):

    def from_config(self, config):
        
        super().from_config(config)

        self._todos = (
            (year, month, day)
            for year in range(config["year"][0], config["year"][-1] + 1)
            for month in range(config["month"][0], config["month"][-1] + 1)
            for day in range(config["day"][0], config["day"][-1] + 1)
        )

        return self

    def _read_todo(self, todo):
        
        year, month, day = todo
        month = "0" + str(month) if month < 10 else str(month)
        day = "0" + str(day) if day < 10 else str(day)
        
        return f"{self._city}_{year}_{month}_{day}"

    @classmethod
    def _check_days(cls, todo):
        '''return false si on veut traiter un jour qui n'existe pas, comme le 31 février'''
        _, month, day = todo

        if day > cls.DAYS[month]:
            return False

        return True
