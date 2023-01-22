from string import Template
import numpy as np
import pandas as pd
import re
from app.scrappers.abcs import MonthlyScrapper, DailyScrapper

class MeteocielMonthly(MonthlyScrapper):

    UNITS = {"temperature": "°C", "precipitations": "mm", "ensoleillement": "h"}

    # Critère de sélection qui sert à retrouver le tableau de donner dans la page html
    CRITERIA = ("cellpadding", "2")

    BASE_URL = Template("https://www.meteociel.com/climatologie/obs_villes.php?code$code_num=$code&mois=$mois&annee=$annee")

    # Regex pour récupérer uniquement les float d'une string pour la colonne des précipitations.
    TEMPLATE_PRECIPITATION = r'-?\d+\.?\d*'

    def __init__(self):
        super().__init__()
        self._code_num = ""
        self._code = ""

    def _reinit(self):
        super()._reinit()
        self._code_num = ""
        self._code = ""

    def _update_specific_parameters(self, config):
        self._code_num = config["code_num"]
        self._code = config["code"]

    def _build_url(self):
        return self.BASE_URL.substitute(code_num = self._code_num,
                                        code = self._code,
                                        mois = self._month,
                                        annee = self._year)

    def _update_parameters_from_url(self, url: str):

        base_url, month_part, year_part = url.split("&")

        year = int(year_part.split("=")[1])
        month = int(month_part.split("=")[1])

        _, code_part = base_url.split("?")
        code_num, code = code_part.split("=")
        code_num = code_num[-1]

        self.__dict__.update({
            "_url": url,
            "_code": code,
            "_code_num": code_num,
            "_year": year,
            "_month": month,
            "_year_str": str(year),
            "_month_str": str(month) if month >= 10 else "0" + str(month),
        })

    @staticmethod
    def _scrap_columns_names(table):

        # (1) On récupère les noms des colonnes contenus dans la 1ère ligne du tableau.
        # (2) Certains caractères à accents passent mal, on les remplace, et on enlève les . .
        # (3) On remplace les espaces par des _, on renomme la colonne jour en date.
        # (4) La dernière colonne contient des images et n'a pas de noms. On la supprimera,
        #     on la nomme to_delete.

        # (1)
        columns_names = [td.text.lower() for td in table.find("tr")[0].find("td")]
        # (2)
        columns_names = [col.replace("ã©", "e").replace(".", "") for col in columns_names]
        # (3)
        columns_names = ["date" if col == "jour" else "_".join(col.split(" ")) for col in columns_names]
        # (4)
        columns_names = ["to_delete" if col == "" else col for col in columns_names]

        return columns_names

    @staticmethod
    def _scrap_columns_values(table):
        # On récupère les valeurs des cellules de toutes les lignes,
        # sauf la 1ère (noms des colonnes) et la dernière (cumul / moyenne mensuel).
        return [ td.text for tr in table.find("tr")[1:-1] for td in tr.find("td") ]

    def _rework_data(self, values, columns_names):

        # (0) On ajoute au nom de la colonne son unité.
        # (1) On définit les dimensions du tableau puis on le créé.
        # (2) Si une colonne to_delete existe, on la supprime.
        # (3) Le tableau ne contient que des string composées d'une valeur et d'une unité.
        #     La fonction lambda renvoie la valeur trouvée dans une string, convertie en float si elle existe, ou nan.
        #     On définit aussi une fonction lambda vectorisée qui met la date en forme.
        # (4) On reconstruit les dates à partir des numéros des jours extraits de la colonne des dates.
        # (5) On extrait les valeurs des autres colonnes.
        # (6) On trie le dataframe selon la date.

        # (0)
        columns_names = [f"{col}_{self.UNITS[col.split('_')[0]]}"
                         if col not in ("date", "to_delete") else col
                         for col in columns_names]

        # (1)
        n_rows = len(values) // len(columns_names)
        n_cols = len(columns_names)
        df = pd.DataFrame(np.array(values).reshape(n_rows, n_cols),
                          columns=columns_names)

        # (2)
        try:
            df = df.drop("to_delete", axis=1)
        except KeyError:
            pass

        # (3)
        f_num_extract = np.vectorize(lambda string : np.NaN if string in("---", "")
                                                     else 0 if string in ("aucune", "traces")
                                                     else float(re.findall(self.TEMPLATE_PRECIPITATION, string)[0]))

        f_rework_dates = np.vectorize(lambda day :      f"{self._year_str}-{self._month_str}-0{int(day)}" if day < 10
                                                   else f"{self._year_str}-{self._month_str}-{int(day)}")

        # (4)
        df["date"] = f_num_extract(df["date"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])

        # (5)
        df.iloc[:, 1:] = f_num_extract(df.iloc[:, 1:])

        # (6)
        df = df.sort_values(by="date")

        return df



class MeteocielDaily(DailyScrapper):

    UNITS = {
        "visi": "km",
        "temperature": "°C",
        "humidite": "%",
        "vent": "km/h",
        "rafales": "km/h",
        "pression": "hPa",
        "precip": "mm",
    }

    # La numérotation des mois sur météociel par jour est décalée.
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

    # Critère de sélection qui sert à retrouver le tableau de donner dans la page html
    CRITERIA = ("bgcolor", "#EBFAF7")

    BASE_URL = Template("https://www.meteociel.com/temps-reel/obs_villes.php?code$code_num=$code&jour2=$jour2&mois2=$mois2&annee2=$annee2")

    # Regex pour récupérer uniquement les float d'une string pour la colonne des précipitations.
    TEMPLATE_PRECIPITATION = r'-?\d+\.?\d*'

    def __init__(self):
        super().__init__()
        self._code_num = ""
        self._code = ""

    def _reinit(self):
        super()._reinit()
        self._code_num = ""
        self._code = ""

    def _update_specific_parameters(self, config):
        self._code_num = config["code_num"]
        self._code = config["code"]

    def _build_url(self):
        return self.BASE_URL.substitute(code_num=self._code_num,
                                        code=self._code,
                                        jour2=self._day,
                                        mois2=self.NUMEROTATIONS[self._month],
                                        annee2=self._year)

    def _update_parameters_from_url(self, url: str):

        base_url, day_part, month_part, year_part = url.split("&")

        year = int(year_part.split("=")[1])
        month = int(month_part.split("=")[1])
        day = int(day_part.split("=")[1])

        revert_numerotation = { value : key for key, value in self.NUMEROTATIONS.items() }

        month = revert_numerotation[month]

        _, code_part = base_url.split("?")
        code_num, code = code_part.split("=")
        code_num = code_num[-1]

        self.__dict__.update({
            "_url": url,
            "_code": code,
            "_code_num": code_num,
            "_year": year,
            "_month": month,
            "_day": day,
            "_year_str": str(year),
            "_month_str": str(month) if month >= 10 else "0" + str(month),
            "_day_str": str(day) if day >= 10 else "0" + str(day)
        })

    @staticmethod
    def _scrap_columns_names(table):

        columns_names = [td.text.lower() for td in table.find("tr")[0].find("td")]

        columns_names = [col.replace("ã©", "e").replace(".", "") for col in columns_names]

        columns_names = [col.split("\n")[0] if "\n" in col else col for col in columns_names]

        # La colonne vent est composée de 2 sous colonnes: direction et vitesse.
        # Le tableau compte donc n colonnes mais n-1 noms de colonnes.
        # On rajoute donc un nom pour la colonne de la direction du vent.
        indexe = columns_names.index("vent (rafales)")
        columns_names.insert(indexe, "winddir")

        return columns_names

    @staticmethod
    def _scrap_columns_values(table):
        return [ td.text for tr in table.find("tr")[1:] for td in tr.find("td") ]

    def _rework_data(self, values, columns_names):

        # (1) On définit les dimensions du tableau puis on le créé.
        # (2) On met de coté la colonne vent car il faut la séparer en 2.
        #     On supprime les colonnes inutiles.
        # (3) On convertit les valeurs du format string vers le format qui leur vont.
        # (4) Ajout des colonnes vent et rafales. Si 1 seule valeur est présente dans la colonne,
        #     on en rajoute une vide pou bien avoir 2 valeurs, pour les 2 colonnes.
        # (5) On réunit les données, on met en forme le tableau.
        # (6) On ajoute au nom de la colonne son unité.

        # (1)
        n_rows = 24
        n_cols = len(columns_names)

        df = pd.DataFrame(np.array(values).reshape(n_rows, n_cols), columns=columns_names)

        # (2)
        vent_rafale = df[["heure", "vent (rafales)"]].copy(deep=True)
        df = df[[col for col in df.columns if col not in ("vent (rafales)", "winddir", "temps")]]

        # (3)
        not_numeric = ["date", "heure", "neb"]
        numerics = [x for x in df.columns if x not in not_numeric]

        f_num_extract = np.vectorize(lambda string : np.NaN if string in("---", "")
                                                     else 0 if string in ("aucune", "traces")
                                                     else float(re.findall(self.TEMPLATE_PRECIPITATION, string)[0]))

        f_rework_dates = np.vectorize(lambda heure :      f"{self._year_str}-{self._month_str}-{self._day_str} 0{int(heure)}:00:00" if heure < 10
                                                     else f"{self._year_str}-{self._month_str}-{self._day_str} {int(heure)}:00:00")

        df["date"] = f_num_extract(df["heure"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])

        df[numerics] = f_num_extract(df[numerics])

        df = df[not_numeric + numerics] # juste pour l'ordre des colonne, avoir la date en 1er

        # (4)
        separated = [x.split("(") for x in vent_rafale["vent (rafales)"].values]

        for x in [separated.index(x) for x in separated if len(x) != 2]:
            separated[x].append("")

        separated = np.array(separated)
        separated = f_num_extract(separated)
        separated = pd.DataFrame(separated, columns=["vent", "rafales"])
        separated["heure"] = vent_rafale["heure"]

        # (5)
        df = pd.merge(df, separated, on="heure", how="inner")
        df = df.drop(["heure"], axis=1)
        df = df.sort_values(by="date")

        # (6)
        df.columns = [f"{col}_{self.UNITS[col]}"
                      if col not in ("date", "neb", "humidex", "windchill") else col
                      for col in df.columns]

        return df
