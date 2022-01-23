
import numpy as np
import pandas as pd
import re
from app.scrappers.abcs import MonthlyScrapper, DailyScrapper

class MeteocielScrapper(MonthlyScrapper):

    UNITS = {"temperature": "°C", "precipitations": "mm", "ensoleillement": "h"}

    CRITERIA = ("cellpadding", "2")
    SCRAPPER = "meteociel"
    BASE_URL = "https://www.meteociel.com/climatologie/obs_villes.php?"

    def from_config(self, config):
        
        super().from_config(config)   
        self._url = self.BASE_URL + f"code{config['code_num']}={config['code']}"

        return self

    def _set_url(self, todo):
        
        year, month = todo
        url = self._url + f"&mois={month}&annee={year}"

        month = "0" + str(month) if month < 10 else str(month)
        print(f"{self.SCRAPPER} - {self._city} - {month}/{year} - {url}")
        
        return url

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
    def _rework_data(values, col_names, todo):
        
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
        year, month = todo
        month = "0" + str(month) if month < 10 else str(month)
        
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

class MeteocielDailyScrapper(DailyScrapper):

    UNITS = {
        "visi": "km",
        "temperature": "°C",
        "humidite": "%",
        "vent (rafales)": "km/h",
        "pression": "hPa",
        "precip": "mm",
    }

    NUMEROTATIONS = {
        "1" :  0,
        "2" :  1,
        "3" :  2,
        "4" :  3,
        "5" :  4,
        "6" :  5,
        "7" :  6,
        "8" :  7,
        "9" :  8,
        "11":  9,
        "10": 10,
        "12": 11,
    }

    CRITERIA = ("bgcolor", "#EBFAF7")
    SCRAPPER = "meteociel_daily"
    BASE_URL = " https://www.meteociel.com/temps-reel/obs_villes.php?"

    def from_config(self, config):
        
        super().from_config(config)
        self._url = self.BASE_URL + f"code{config['code_num']}={config['code']}"

        return self

    def _set_url(self, todo):

        year, month, day = todo
        url = self._url + f"&jour2={day}&mois2={self.NUMEROTATIONS[str(month)]}&annee2={year}"

        month = "0" + str(month) if month < 10 else str(month)
        day = "0" + str(day) if day < 10 else str(day)

        print(f"{self.SCRAPPER} - {self._city} - {day}/{month}/{year} - {url}")
        
        return url

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
    def _rework_data(values, col_names, todo):

        year, month, day = todo
        month = "0" + str(month) if month < 10 else str(month)
        day = "0" + str(day) if day < 10 else str(day)
        
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
        
        separated = [x.split("(") for x in vent_rafale["vent (rafales)_km/h"].values]
        
        # si 1 seule valeur est présente dans la colonne, on en rajoute une vide
        for x in [separated.index(x) for x in separated if len(x) != 2]:
            separated[x].append("")
        
        separated = np.array(separated)
        print(separated)
        separated = f_num_extract(separated)
        separated = pd.DataFrame(separated, columns=["vent", "rafale"])
        separated["heure"] = vent_rafale["heure"]

        df = pd.merge(df, separated, on="heure", how="inner")
        del df["heure"], separated, vent_rafale
        df = df.sort_values(by="date")
        
        return df
