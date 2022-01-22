from requests_html import HTMLSession
from abc import ABC, abstractmethod
import pandas as pd

class BaseScrapper(ABC):

    '''Scrapper de base qui récupère les données brutes d'une table html.'''

    _instance = None

    def __init__(self):
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):
        cls._instance = cls._instance if cls._instance is not None else cls.__new__(cls)
        return cls._instance

    def from_config(self, config):

        self.errors = {}
        self._city = config["city"]
        self._todos = (
            (year, month)
            for year in range(config["year"][0], config["year"][-1] + 1)
            for month in range(config["month"][0], config["month"][-1] + 1)
        )
        try:
            self._waiting = config["waiting"]
        except KeyError:
            self._waiting = 10

        return self
    
    ### METHODES ABSTRAITES ###
    @abstractmethod
    def _set_url(self, year, month):
        '''crétion de l'url'''

    @abstractmethod
    def _scrap_columns_names(table):
        '''fonction à redéfinir dans chaque scrapper qui récupère les noms des colonnes'''
    
    @abstractmethod
    def _scrap_columns_values(table):
        '''fonction à redéfinir dans chaque scrapper qui récupère les valeurs du tableau de données'''

    @abstractmethod
    def _rework_data(self):
        '''fonction à redéfinir dans chaque scrapper qui met en forme le tableau de données'''
    

    ### METHODES CONCRETES ###
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
        # Il se compose d'un attribut html et de sa valeur.
        # (2) On cherche une table html correspondant au critère parmis toutes celles de la page.
        # On récupère la 1ère trouvée. Si on ne trouve pas de table, on la déclare inexistante.  
        # (3) On vérifie que la table n'indique pas l'absence de données (spécifique à ogimet).
        # Voir http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2016&mes=4&day=0&hora=0&min=0&ndays=31
        # Si elle l'est, on déclare la table inexistante. Sinon on ne fait rien.
        
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
            condition =  "no valid" in table.find("thead")[0].find("th")[0].text.lower().strip()
            table = None if condition else table
        except IndexError:
            pass

        return table

    def _scrap_data(self):
        
        '''_scrap_data : générateur des dataframes à enregistrer.
            return: table (requests-html.Element, voir doc requests-html python) ou None
        '''
        # (1) On récupère l'année et le mois courant à partir du tuple todo.
        # On affiche dans le terminal le job en cours. On convertit le mois (int) en string.
        # (2) On reconstitue l'url et on charge la page html correspondante. S'il y a une erreur,
        # on le signale et on passe au tuple suivant.
        # (3) On récupère la table de données html. Si elle n'existe pas, on le signal
        # et on passe au tuple suivant.
        # (4) On récupère le noms des colonnes et les valeurs de la table de données html.
        # (5) On met les données sous forme de dataframe.
        # Si on ne peut pas, on le signale et on passe à la table suivante.
        
        for todo in self._todos:
            # (1)
            year, month = todo
            month = "0" + str(month) if month < 10 else str(month)
            # (2)
            url = self._set_url(year, month)
            print(f"\n{self.SCRAPPER} - {self._city} - {month}/{year} - {url}")
            
            html_page = self._get_html_page(url)
            if html_page is None:
                error = "error while loading html page"
                self.errors[f"{self._city}_{year}_{month}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue
            # (3)
            table = self._find_table_in_html(html_page)
            if table is None:
                error = "no data table found"
                self.errors[f"{self._city}_{year}_{month}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue
            # (4)
            try:
                col_names = self._scrap_columns_names(table)
                values = self._scrap_columns_values(table)
            except Exception:
                error = "error while scrapping data"
                self.errors[f"{self._city}_{year}_{month}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue
            # (5)
            try:
                df = self._rework_data(values, col_names, year, month)
            except Exception:
                error = "error while reworking data"
                self.errors[f"{self._city}_{year}_{month}"] = {"url": url, "error": error}
                print(f"\t{error}")
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
        return f"<{self.__class__.__name__}> ville:{self._city}, url:{self._url}"
