import numpy as np
import pandas as pd
from app.scrappers.abcs import BaseScrapper

class WundergroundScrapper(BaseScrapper):
    
    ''' scrapper pour le site wunderground'''

    UNITS_CONVERSION = {
        "°_f": { "new_unit": "°C", "func": (lambda x: (x-32)*5/9 )},
        "(mph)": { "new_unit": "(km/h)", "func": (lambda x: x*1.609344) },
        "(in)": { "new_unit": "(mm)", "func": (lambda x: x*25.4) },
        "(hg)": { "new_unit": "(hPa)",  "func": (lambda x: x*33.86388) }
    }

    # Critère de sélection qui servira à récupérer le tableau voulu
    CRITERIA = ("aria-labelledby", "History days")
    SCRAPPER = "wunderground"
    BASE_URL = "https://www.wunderground.com/history/monthly/"
    
    def from_config(self, config):

        super().from_config(config)
        self._url = self.BASE_URL + f"{config['country_code']}/{config['city']}/{config['region']}/date"

        return self

    def _set_url(self, year, month):
        return self._url + f"/{year}-{int(month)}"

    @staticmethod
    def _scrap_columns_names(table):
        
        '''
        _scrap_columns_names: récupère les valeurs de chaque cellule td de la partie
        thead du tableau html.
            args: table (requests_html.Element)
            return: (list)
        '''
        return [td.text for td in table.find("thead")[0].find("td")]

    @staticmethod
    def _scrap_columns_values(table):
        
        '''
        _scrap_columns_values: récupère les valeurs de chaque cellule td de la partie
        tbody du tableau html.
            args: table (requests_html.Element)
            return: col_names (list)
        '''
        # La structure html du tableau est tordue, ce qui conduit à des doublons dans values.
        # Daily Observations compte 7 colonnes principales et 17 sous-colonnes.
        # Elle est donc de dimension (lignes, sous-colonnes).
        # values devrait être de longueur lignes * sous-colonnes.
        # Elle est en réalité de longueur lignes * sous-colonnes + 7.
        # Pour janvier 2020 à bergamo, la 1ère des 7 valeurs additionnelles sera "Jan\n1\n2...",
        # la 2ème valeur sera "Max\nAvg\nMin\n52\n39.9\n32\n...",
        # la nième valeur contient les données de la nième colonne principale,
        # et donc de toutes ses sous-colonnes.
        # On récupère ces 7 valeurs additionnelles qui contiennent le caractère \n.
        
        return [ td.text for td in table.find("tbody")[0].find("td") if "\n" in td.text ]

    @classmethod
    def _rework_data(cls, values, main_names, year, month):
        '''_rework_data : création du dataframe final
            args: values (list), main_names (list), year (int), month (str)
            return : df (pandas.DataFrame)
        '''
        # (1) values est une liste de str. Chaque str contient toutes les données d'1 colonne principale
        # séparées par des \n ("x\nx\nx\nx..."). On convertit ces str en liste de données [x,x,x, ...].
        # values devient une liste de listes.
        # On définit aussi le nombre de ligne comme étant égal à la longueur de la 1ère liste de values,
        # qui correspond à la colonne Time.
        # (2) On initialise la matrice qui constituera le dataframe final avec la 1ère liste (Time) transformée en vecteur colonne.
        # (3) Le dataframe aura besoin de noms pour ses colonnes. Le nom final est composé d'un nom
        # principal et d'un complément, sauf pour les colonnes Time et Précipitations.
        # Les noms principaux sont contenus dans main_names, les compléments correspondent aux 1 ou 3
        # premières valeurs des listes dans values. Pour chaque liste, on détermine le nombre de colonnes
        # qu'elle contient, et on récupère les compléments (si elle compte pour 3 colonnes, on prend les 3
        # premières valeurs). On transforme la liste courante en vecteur colonne ou en matrice à 3 colonnes,
        # puis on accolle ces colonnes au dataframe principal.
        # (4) On a récupéré tous les compléments et tous les nomes principaux. On créer tous les couples
        # nom prinicpal - complément qu'il faut pour obtenir les noms des colonnes du dataframe.
        # Le nom de la colonne des dates est actuellement Time. On le remplace par date.
        # (5) On créer le dataframe final à partir de la matrice et des noms de colonnes. La 1ère ligne,
        # contenant les compléments, est supprimée.
        # (6) La colonne date ne contient que les numéros du jour du mois (1 à 31, ou moins). On remplace
        # par la date au format AAAA-MM-JJ et on trie.
        # (7) Jusqu'ici les valeur du dataframe sont au format str. On les convertit en numérique.
        # (8) On convertit vers les unités S.I. .
        
        # (1)
        values = [string.split("\n") for string in values]
        n_rows = len(values[0])
        # (2)
        df = np.array(values[0]).reshape(n_rows, 1)
        # (3)
        sub_names = [[""]]

        for values_list in values[1:]:
            
            n_cols = len(values_list) // n_rows

            sub_names += [values_list[0:n_cols]]

            new_columns = np.array(values_list).reshape(n_rows, n_cols)
            
            df = np.hstack((df, new_columns))
        
        # (4)
        col_names = [
            "_".join( [ main.strip(), sub.strip() ] ).lower()

            for main, subs in zip(main_names, sub_names)
            for sub in subs
        ]

        col_names[0] = "date"
        # (5)
        df = pd.DataFrame(df, columns=col_names)
        df = df.drop([0], axis="index")
        # (6)
        df["date"] = [
            
            f"{year}/{month}/0{day}" if int(day) < 10 else f"{year}/{month}/{day}" 
            
            for day in df.date
        ]
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(by="date")
        # (7)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col])
        # (8)
        for old_unit, dico in cls.UNITS_CONVERSION.items():

            cols_toconvert = [col for col in df.columns if old_unit in col]

            df[cols_toconvert] = np.round(dico["func"](df[cols_toconvert]), 1)

            df = df.rename(columns={
                col: col.replace(old_unit, dico["new_unit"]) for col in cols_toconvert
            })

        return df