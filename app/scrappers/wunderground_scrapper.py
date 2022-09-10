from string import Template
import numpy as np
import pandas as pd
from app.scrappers.abcs import MonthlyScrapper

class WundergroundMonthly(MonthlyScrapper):

    UNITS_CONVERSION = {
        "dew" : {"new_name": "dew_point_°C",
                 "func": (lambda x: (x-32)*5/9 )},

        "wind": {"new_name": "wind_speed_(km/h)",
                 "func": (lambda x: x*1.609344)},

        "pressure": {"new_name": "pressure_(hPa)",
                     "func": (lambda x: x*33.86388)},

        "humidity": {"new_name": "humidity_(%)",
                     "func": (lambda x: x)},

        "temperature": {"new_name": "temperature_°C",
                        "func": (lambda x: (x-32)*5/9 )},

        "precipitation": {"new_name": "precipitation_(mm)",
                          "func": (lambda x: x*25.4)}
    }

    # Critère de sélection qui sert à retrouver le tableau de donner dans la page html
    CRITERIA = ("aria-labelledby", "History days")

    BASE_URL = Template("https://www.wunderground.com/history/monthly/$country_code/$city/$region/date/$year-$month")

    def __init__(self):
        super().__init__()
        self._country_code = ""
        self._region = ""

    def update(self, config):

        super().update(config)
        self._country_code = config["country_code"]
        self._region = config["region"]

    def _build_url(self, todo):

        year, month = todo

        url = self.BASE_URL.substitute(country_code = self._country_code,
                                       city = self._city,
                                       region = self._region,
                                       year = year,
                                       month = month)
        return url

    @staticmethod
    def _scrap_columns_names(table):
        return [td.text for td in table.find("thead")[0].find("td")]

    @staticmethod
    def _scrap_columns_values(table):

        # La structure html du tableau est tordue, ce qui conduit à des doublons dans values.
        # Daily Observations compte 7 colonnes principales et 17 sous-colonnes.
        # Elle est donc de dimension (lignes, sous-colonnes).
        # values devrait être de longueur lignes * sous-colonnes.
        # Elle est en réalité de longueur lignes * sous-colonnes + 7. Il y a 7 valeurs additionnelles.
        # Pour janvier 2020 à bergamo, la 1ère des 7 valeurs additionnelles sera "Jan\n1\n2...",
        # la 2ème valeur sera "Max\nAvg\nMin\n52\n39.9\n32\n...",
        # la nième valeur contient les données de la nième colonne principale,
        # et donc de toutes ses sous-colonnes.
        # On récupère ces 7 valeurs additionnelles qui contiennent le caractère \n.

        return [ td.text for td in table.find("tbody")[0].find("td") if "\n" in td.text ]

    def _rework_data(self, values, columns_names, todo):

        # (1) values est une liste de str. Chaque str contient toutes les données d'1 colonne principale
        #     séparées par des \n ("x\nx\nx\nx..."). On convertit ces str en liste de données [x,x,x, ...].
        #     values devient une liste de listes.
        #     On définit aussi le nombre de ligne comme étant égal à la longueur de la 1ère liste de values,
        #     qui correspond à la colonne Time.
        # (2) On initialise la matrice qui constituera le dataframe final avec la 1ère liste (Time) transformée en vecteur colonne.
        # (3) Le dataframe aura besoin de noms pour ses colonnes. Le nom final est composé d'un nom
        #     principal et d'un complément, sauf pour les colonnes Time et Précipitations.
        #     Les noms principaux sont contenus dans main_names, les compléments correspondent aux 1 ou 3
        #     premières valeurs des listes dans values. Pour chaque liste, on détermine le nombre de colonnes
        #     qu'elle contient, et on récupère les compléments (si elle compte pour 3 colonnes, on prend les 3
        #     premières valeurs). On transforme la liste courante en vecteur colonne ou en matrice à 3 colonnes,
        #     puis on accolle ces colonnes au dataframe principal.
        # (4) Les main_names ne vont pas, les unités précisées ne vont pas, il y a des majuscules et des espaces.
        #     On veut tout en minsucule, avec des _ et dans les bonnes unités.
        #     On remplace les main_names par leurs nouvelles valeurs : si la clé du dict UNITS_CONVERSION est présente
        #     dans le main_name, on remplace et on passe au main_name suivant.
        #     Ensuite, on associe les main_names avec leurs sub_names.
        #     Enfin, le nom de la colonne des dates est actuellement Time. On le remplace par date.
        # (5) On créé le dataframe final à partir de la matrice et des noms de colonnes. La 1ère ligne,
        #     contenant les compléments, est supprimée.
        # (6) La colonne date ne contient que les numéros du jour du mois (1 à 31, ou moins). On remplace
        #     par la date au format AAAA-MM-JJ et on trie.
        # (7) Jusqu'ici les valeur du dataframe sont au format str. On les convertit en numérique.
        # (8) On convertit vers les unités classiques .

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
        for index, main_name in enumerate(columns_names):

            for key in self.UNITS_CONVERSION.keys():

                is_key_in_name = key in main_name.lower().strip()

                if is_key_in_name:
                    columns_names[index] = self.UNITS_CONVERSION[key]["new_name"]
                    break

        final_col_names = [
            "_".join( [ main, sub.strip().lower() ] ) if sub else main

            for main, subs in zip(columns_names, sub_names)
            for sub in subs
        ]

        final_col_names[0] = "date"

        # (5)
        df = pd.DataFrame(df, columns=final_col_names)
        df = df.drop([0], axis="index")

        # (6)
        year, month = todo
        month = "0" + str(month) if month < 10 else str(month)

        df["date"] = [
            f"{year}/{month}/0{day}" if int(day) < 10 else f"{year}/{month}/{day}" for day in df.date
        ]

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(by="date")

        # (7)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col])

        # (8)
        for variable, dico in self.UNITS_CONVERSION.items():

            cols_to_convert = [col for col in df.columns if variable in col]

            df[cols_to_convert] = np.round(dico["func"](df[cols_to_convert]), 1)

        return df
