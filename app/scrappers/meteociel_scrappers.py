
import numpy as np
import pandas as pd
import re
from app.scrappers.abcs import MonthlyScrapper, DailyScrapper

class MeteocielScrapper(MonthlyScrapper):
    
    '''
    Les méthodes from_config, set_url et rework_data complètent ou sont
    l' implémententation des méthodes de l'abc MeteoScrapper.

    Les méthodes scrap_columns_names et scrap_columns_values sont l'implémentation
    des méthodes de l'interface ScrappingToolsInterface.
    '''

    UNITS = {"temperature": "°C", "precipitations": "mm", "ensoleillement": "h"}
    # Critère de sélection qui sert à retrouver le tableau de donner dans la page html
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
        
        # (1) On récupère les noms des colonnes contenus dans la 1ère ligne du tableau.
        # (2) Certains caractères à accents passent mal, on les remplace, et on enlève les . .
        # (3) On remplace les espaces par des _, on renomme la colonne jour en date.
        # (4) La dernière colonne contient des images et n'a pas de noms. On la supprimera,
        #     on la nomme to_delete.
        # (5) On ajoute au nom de la colonne son unité.
        
        # (1)
        cols = [td.text.lower() for td in table.find("tr")[0].find("td")]
        # (2)
        cols = [col.replace("ã©", "e").replace(".", "") for col in cols]
        # (3)
        cols = ["date" if col == "jour" else "_".join(col.split(" ")) for col in cols]
        # (4)
        cols = ["to_delete" if col == "" else col for col in cols]
        # (5)
        cols = [ f"{col}_{cls.UNITS[col.split('_')[0]]}" if col not in ("date", "to_delete") else col for col in cols ]

        return cols

    @staticmethod
    def _scrap_columns_values(table):
        # On récupère les valeurs des cellules de toutes les lignes,
        # sauf la 1ère (noms des colonnes) et la denrière (cumul mensuel).
        return [ td.text for tr in table.find("tr")[1:-1] for td in tr.find("td") ]

    @staticmethod
    def _rework_data(values, col_names, todo):
        
        # (1) On définit les dimensions du tableau puis on le créé.
        # (2) Si une colonne to_delete existe, on la supprime.
        # (3) Le tableau ne contient que des string composées d'une valeur et d'une unité.
        #     On définit une regex chargée de récupérer uniquement les float d'une string.
        #     La regexp est ensuite utilisée par une fonction lambda vectorisée. La fonction
        #     renvoie la valeur trouvée dans une string, convertie en float si elle existe, ou nan.
        #     On définit aussi une fonction lambda vectorisée qui met la date en forme.
        # (4) On reconstruit les dates à partir des numéros des jours extraits de la colonne des dates.
        # (5) On extrait les valeurs des autres colonnes.
        # (6) On trie le dataframe selon la date.

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
        f_num_extract = np.vectorize(lambda string : np.NaN if string in("---", "") else 0 if string in ("aucune", "traces") else float(re.findall(template, string)[0]))
        f_rework_dates = np.vectorize(lambda day : f"{year}-{month}-0{int(day)}" if day < 10 else f"{year}-{month}-{int(day)}")
        # (4)
        df["date"] = f_num_extract(df["date"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])
        # (5)
        df.iloc[:, 1:] = f_num_extract(df.iloc[:, 1:])
        # (6)
        df = df.sort_values(by="date")
        
        return df

class MeteocielDailyScrapper(DailyScrapper):

    '''
    Les méthodes from_config, set_url et rework_data complètent ou sont
    l' implémententation des méthodes de l'abc MeteoScrapper.

    Les méthodes scrap_columns_names et scrap_columns_values sont l'implémentation
    des méthodes de l'interface ScrappingToolsInterface.
    '''

    UNITS = {
        "visi": "km",
        "temperature": "°C",
        "humidite": "%",
        "vent (rafales)": "km/h",
        "pression": "hPa",
        "precip": "mm",
    }
    # La numérotation des mois sur météociel est décalée.
    # Ce dictionnaire associe la numérotation usuelle (clés) et celle de météociel (valeurs).
    NUMEROTATIONS = {
        1  :  0,
        2  :  1,
        3  :  2,
        4  :  3,
        5  :  4,
        6  :  5,
        7  :  6,
        8  :  7,
        9  :  8,
        11 :  9,
        10 : 10,
        12 : 11,
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
        url = self._url + f"&jour2={day}&mois2={self.NUMEROTATIONS[month]}&annee2={year}"

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
        
        # La colonne vent est composée de 2 sous colonnes: direction et vitesse.
        # Le tableau compte donc n colonnes mais n-1 noms de colonnes.
        # On rajoute donc un nom pour la colonne de la direction du vent.
        indexe = cols.index("vent (rafales)_km/h")
        cols.insert(indexe, "winddir")
        
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
        df = df[[col for col in df.columns if col not in ("vent (rafales)_km/h", "winddir", "temps")]]

        not_numeric = ["date", "heure", "neb"]
        numerics = [x for x in df.columns if x not in not_numeric]
        
        template = r'-?\d+\.?\d*'
        f_num_extract = np.vectorize(lambda string : np.NaN if string in("---", "") else 0 if string in ("aucune", "traces") else float(re.findall(template, string)[0]))
        f_rework_dates = np.vectorize(lambda heure : f"{year}-{month}-{day} 0{int(heure)}:00:00" if heure < 10 else f"{year}-{month}-{day} {int(heure)}:00:00")
        
        df["date"] = f_num_extract(df["heure"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])
        
        df[numerics] = f_num_extract(df[numerics])
        
        df = df[not_numeric + numerics] # juste pour l'ordre des colonne, avoir la date en 1er
        
        # ajout des colonnes vent et rafales
        separated = [x.split("(") for x in vent_rafale["vent (rafales)_km/h"].values]
        
        # si 1 seule valeur est présente dans la colonne, on en rajoute une vide
        for x in [separated.index(x) for x in separated if len(x) != 2]:
            separated[x].append("")
        
        separated = np.array(separated)
        separated = f_num_extract(separated)
        separated = pd.DataFrame(separated, columns=["vent", "rafale"])
        separated["heure"] = vent_rafale["heure"]

        df = pd.merge(df, separated, on="heure", how="inner")
        del df["heure"], separated, vent_rafale
        df = df.sort_values(by="date")
        
        return df
