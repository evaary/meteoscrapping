
import numpy as np
import pandas as pd
import re
from requests_html import HTMLSession
from app.scrappers.abcs import BaseScrapper

class MeteocielScrapper(BaseScrapper):

    UNITS = {"temperature": "°C", "precipitations": "mm", "ensoleillement": "h"}

    CRITERIA = ("cellpadding", "2")
    SCRAPPER = "meteociel"
    BASE_URL = "https://www.meteociel.com/climatologie/obs_villes.php?"

    def from_config(self, config):
        
        super().from_config(config)   
        self._url = self.BASE_URL + f"code{config['code_num']}={config['code']}"

        return self

    def _set_url(self, year, month):
        return self._url + f"&mois={month}&annee={year}"

    @classmethod
    def _scrap_columns_names(cls, table):
        
        '''
        _scrap_columns_names: récupère les valeurs de chaque cellule td de la 1ère tr
        du tableau html.
            args: table (requests_html.Element)
            return: (list)
        '''
        # (2) On récupère les noms des colonnes contenus dans la 1ère ligne du tableau.
        # (3) Certains caractères à accents passent mal, on les remplace, et on enlève les . .
        # (4) On remplace les espaces par des _, on renomme la colonne jour en date.
        # (5) La dernière colonne contient des images etn'a pas de noms. On la supprimera,
        #     on la nomme to_delete.
        # (6) On ajoute au nom de la colonne son unité.
        
        # (2)
        cols = [td.text.lower() for td in table.find("tr")[0].find("td")]
        # (3)
        cols = [col.replace("ã©", "e").replace(".", "") for col in cols]
        # (4)
        cols = ["date" if col == "jour" else "_".join(col.split(" ")) for col in cols]
        # (5)
        cols = ["to_delete" if col == "" else col for col in cols]
        # (6)
        cols = [ f"{col}_{cls.UNITS[col.split('_')[0]]}" if col not in ("date", "to_delete") else col for col in cols ]

        return cols

    @staticmethod
    def _scrap_columns_values(table):
        # On récupère toutes les valeurs des cellules de toutes les lignes,
        # sauf la 1ère (noms des colonnes) et la denrière (cumul mensuel).
        return [ td.text for tr in table.find("tr")[1:-1] for td in tr.find("td") ]

    @staticmethod
    def _rework_data(values, col_names, year, month):
        
        # (1) On définit les dimensions du tableau puis on le créé.
        # (2) Si une colonne to_delete exite, on la supprime.
        # (3) Le tableau ne contient que des string composées d'une valeur et d'une unité.
        #     On définit une regex chargée de récupérer uniquement les float d'une string.
        #     La regexp est ensuite utilisée par une fonction lambda vectorisée. La fonction
        #     renvoie la valeur trouvée dans une string, convertie en float si elle existe, ou nan.
        #     On définit aussi une fonction lambda vectorisée qui met la date en forme.
        # (4) On reconstruit les dates à partir des numéros des jours extraits de la colonne des dates.
        # (5) On extrait les valeurs des autres colonnes.
        # (6) On réaffecte les nouvelles dates, puis on trie le dataframe selon la date.

        # (1)
        n_rows = len(values) // len(col_names)
        n_cols = len(col_names)
        df = pd.DataFrame(np.array(values).reshape(n_rows, n_cols), columns=col_names)
        # (2)
        try:
            df = df.drop("to_delete", axis=1)
        except KeyError:
            pass
        # (3)
        template = r'-?\d+\.?\d*'
        f_num_extract = np.vectorize(lambda string : np.NaN if string in("---", "") else float(re.findall(template, string)[0]))
        f_rework_dates = np.vectorize(lambda numero : f"{year}-{month}-0{int(numero)}" if numero < 10 else f"{year}-{month}-{int(numero)}")
        # (4)
        dates = f_num_extract(df["date"])
        dates = f_rework_dates(dates)
        # (5)
        df.iloc[:, 1:] = f_num_extract(df.iloc[:, 1:])
        # (6)
        df["date"] = dates
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(by="date")
        
        return df

class MeteocielDailyScrapper:

    UNITS = {
        "visi": "km",
        "temperature": "°C",
        "humidite": "%",
        "vent (rafales)": "km/h",
        "pression": "hPa",
        "precip": "mm",
    }

    ASSOCIATIONS = {
        "1" : {"num":  0, "days": 31},
        "2" : {"num":  1, "days": 28},
        "3" : {"num":  2, "days": 31},
        "4" : {"num":  3, "days": 30},
        "5" : {"num":  4, "days": 31},
        "6" : {"num":  5, "days": 30},
        "7" : {"num":  6, "days": 31},
        "8" : {"num":  7, "days": 31},
        "9" : {"num":  8, "days": 30},
        "11": {"num":  9, "days": 30},
        "10": {"num": 10, "days": 31},
        "12": {"num": 11, "days": 31},
    }

    CRITERIA = ("bgcolor", "#EBFAF7")
    SCRAPPER = "meteociel_daily"
    BASE_URL = " https://www.meteociel.com/temps-reel/obs_villes.php?"

    _instance = None

    def __init__(self):
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):
        cls._instance = cls._instance if cls._instance is not None else cls.__new__(cls)
        return cls._instance

    def from_config(self, config):

        self.errors = {}
        self._url = self.BASE_URL + f"code{config['code_num']}={config['code']}"
        self._city = config["city"]
        
        try:
            self._waiting = config["waiting"]
        except KeyError:
            self._waiting = 10
        
        self._todos = (
            (year, month, day)
            for year in range(config["year"][0], config["year"][-1] + 1)
            for month in range(config["month"][0], config["month"][-1] + 1)
            for day in range(config["day"][0], config["day"][-1] + 1)
        )

        return self

    def _get_html_page(self, url):
        
        html_page = None
        i = 0
        with HTMLSession() as session:
        
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
        
        attr, val = cls.CRITERIA
        
        try:
            table = [
                tab for tab in html_page.html.find("table")
                if attr in tab.attrs and tab.attrs[attr] == val
            ][0]
        except Exception:
            table = None
            return table

        return table

    @classmethod
    def _scrap_columns_names(cls, table):
        
        cols = [td.text.lower() for td in table.find("tr")[0].find("td")]
        
        cols = [col.replace("ã©", "e").replace(".", "") for col in cols]
        
        cols = [col.split("\n")[0] if "\n" in col else col for col in cols]
        
        cols = [ f"{col}_{cls.UNITS[col]}" if col not in ("heure", "temps", "neb", "humidex", "windchill") else col for col in cols ]

        indexe = cols.index("windchill")
        cols.insert(indexe + 1, "winddir")
        
        return cols
    
    @staticmethod
    def _scrap_columns_values(table):
        return [ td.text for tr in table.find("tr")[1:] for td in tr.find("td") ]

    @staticmethod
    def _rework_data(values, col_names, year, month, day):
        
        n_rows = 24
        n_cols = len(col_names)
        
        df = pd.DataFrame(np.array(values).reshape(n_rows, n_cols), columns=col_names)
        # on met de coté cette colonne car il faut la séparer en 2
        vent_rafale = df[["heure", "vent (rafales)_km/h"]].copy(deep=True)
        df = df.drop(["vent (rafales)_km/h", "winddir", "temps"], axis=1)

        not_numeric = ["date", "heure", "neb"]
        numerics = [x for x in df.columns if x not in not_numeric]
        
        template = r'-?\d+\.?\d*'
        f_num_extract = np.vectorize(lambda string : np.NaN if string in("---", "", "aucune", "traces") else float(re.findall(template, string)[0]))
        f_rework_dates = np.vectorize(lambda heure : f"{year}-{month}-{day} 0{int(heure)}:00:00" if heure < 10 else f"{year}-{month}-{day} {int(heure)}:00:00")
        
        dates = f_num_extract(df["heure"])
        dates = f_rework_dates(dates)
        df["date"] = dates
        df["date"] = pd.to_datetime(df["date"])
        
        df[numerics] = f_num_extract(df[numerics])
        
        df = df[not_numeric + numerics]
        
        separated = np.array(
            [x.split("(") for x in vent_rafale["vent (rafales)_km/h"].values]
        )
        separated = f_num_extract(separated)
        separated = pd.DataFrame(separated, columns=["vent", "rafale"])
        separated["heure"] = vent_rafale["heure"]

        df = pd.merge(df, separated, on="heure", how="inner")
        del df["heure"], separated, vent_rafale
        df = df.sort_values(by="date")
        
        return df
    
    def _scrap_data(self):
                
        for todo in self._todos:
            
            year, month, day = todo
            # Pour éviter de chercher les data du 31 février, entre autre ...
            if day > self.ASSOCIATIONS[str(month)]["days"]:
                continue

            month = "0" + str(month) if month < 10 else str(month)
            day = "0" + str(day) if day < 10 else str(day)
            
            url = self._url + f"&jour2={int(day)}&mois2={self.ASSOCIATIONS[str(int(month))]['num']}&annee2={year}"
            print(f"\n{self.SCRAPPER} - {self._city} - {day}/{month}/{year} - {url}")
            
            html_page = self._get_html_page(url)
            if html_page is None:
                error = "error while loading html page"
                self.errors[f"{self._city}_{year}_{month}_{day}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue
            
            table = self._find_table_in_html(html_page)
            if table is None:
                error = "no data table found"
                self.errors[f"{self._city}_{year}_{month}_{day}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue
            
            try:
                col_names = self._scrap_columns_names(table)
                values = self._scrap_columns_values(table)
            except Exception:
                error = "error while scrapping data"
                self.errors[f"{self._city}_{year}_{month}_{day}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue
            
            try:
                df = self._rework_data(values, col_names, year, month, day)
            except Exception:
                error = "error while reworking data"
                self.errors[f"{self._city}_{year}_{month}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue

            yield df

    def get_data(self):
        
        try:
            data = next(self._scrap_data())

            for df in self._scrap_data():
                data = pd.concat([data, df])
        
        except StopIteration:
            data = pd.DataFrame()
        
        return data

    def __repr__(self):
        return f"<{self.__class__.__name__}> ville:{self._city}, url:{self._url}"
