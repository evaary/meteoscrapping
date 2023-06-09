import re
from string import Template

import numpy as np
import pandas as pd

from app import utils
from app.job_parameters import (JobParametersBuilder, MeteocielDailyParameters,
                                MeteocielMonthlyParameters)
from app.scrappers.abcs import MeteoScrapper


class MeteocielMonthly(MeteoScrapper):

    UNITS = { "temperature": "°C",
              "precipitations": "mm",
              "ensoleillement": "h" }

    # Regex pour récupérer uniquement les float d'une string pour la colonne des précipitations.
    TEMPLATE_PRECIPITATION = r'-?\d+\.?\d*'

    def _build_parameters_generator(self, config):

        waiting_to_add = self.DEFAULT_WAITING

        try:
            waiting_to_add = config["waiting"]
        except KeyError:
            pass

        return (

            JobParametersBuilder().add_city( config["city"] )
                                  .add_code_num( config["code_num"] )
                                  .add_code( config["code"] )
                                  .add_waiting(waiting_to_add)
                                  .add_year(year)
                                  .add_month(month)
                                  .buildMeteocielMonthlyParameters()

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)
        )

    @staticmethod
    def _scrap_columns_names(table):

        # (1) On récupère les noms des colonnes contenus dans la 1ère ligne du tableau.
        # (2) Certains caractères à accents passent mal, on les remplace, et on enlève les . .
        # (3) On remplace les espaces par des _, on renomme la colonne jour en date.
        # (4) La dernière colonne contient des images et n'a pas de noms. On la supprimera,
        #     on la nomme to_delete.

        # (1)
        columns_names = [ td.text.lower() for td in table.find("tr")[0].find("td") ]
        # (2)
        columns_names = [ col.replace("ã©", "e").replace(".", "") for col in columns_names ]
        # (3)
        columns_names = [ "date" if col == "jour" else "_".join(col.split(" ")) for col in columns_names ]
        # (4)
        columns_names = [ "to_delete" if col == "" else col for col in columns_names ]

        return columns_names

    @staticmethod
    def _scrap_columns_values(table):
        # On récupère les valeurs des cellules de toutes les lignes,
        # sauf la 1ère (noms des colonnes) et la dernière (cumul / moyenne mensuel).
        return [ td.text for tr in table.find("tr")[1:-1] for td in tr.find("td") ]

    def _rework_data(self,
                     values,
                     columns_names,
                     parameters: MeteocielMonthlyParameters):

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
        columns_names = [ f"{col}_{self.UNITS[col.split('_')[0]]}"
                          if col not in ("date", "to_delete") else col
                          for col in columns_names ]

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

        f_rework_dates = np.vectorize(lambda day :      f"{parameters.year_str}-{parameters.month_str}-0{int(day)}" if day < 10
                                                   else f"{parameters.year_str}-{parameters.month_str}-{int(day)}")

        # (4)
        df["date"] = f_num_extract(df["date"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])

        # (5)
        df.iloc[:, 1:] = f_num_extract(df.iloc[:, 1:])

        # (6)
        df = df.sort_values(by="date")

        return df



class MeteocielDaily(MeteoScrapper):

    UNITS = { "visi": "km",
              "temperature": "°C",
              "humidite": "%",
              "vent": "km/h",
              "rafales": "km/h",
              "pression": "hPa",
              "precip": "mm" }

    # Regex pour récupérer uniquement les float d'une string pour la colonne des précipitations.
    TEMPLATE_PRECIPITATION = r'-?\d+\.?\d*'

    def _build_parameters_generator(self, config):

        waiting_to_add = self.DEFAULT_WAITING

        try:
            waiting_to_add = config["waiting"]
        except KeyError:
            pass

        return (

            JobParametersBuilder().add_city( config["city"] )
                                  .add_code_num( config["code_num"] )
                                  .add_code( config["code"] )
                                  .add_waiting(waiting_to_add)
                                  .add_year(year)
                                  .add_month(month)
                                  .add_day(day)
                                  .buildMeteocielDaillyParameters()

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)

            for day in range(config["day"][0],
                             config["day"][-1] + 1)

            if day <= utils.DAYS[month]
        )

    @staticmethod
    def _scrap_columns_names(table):

        columns_names = [ td.text.lower() for td in table.find("tr")[0].find("td") ]

        columns_names = [ col.replace("ã©", "e").replace(".", "") for col in columns_names ]

        columns_names = [ col.split("\n")[0] if "\n" in col else col for col in columns_names ]

        # La colonne vent est composée de 2 sous colonnes: direction et vitesse.
        # Le tableau compte donc n colonnes mais n-1 noms de colonnes.
        # On rajoute donc un nom pour la colonne de la direction du vent.
        indexe = columns_names.index("vent (rafales)")
        columns_names.insert(indexe, "winddir")

        return columns_names

    @staticmethod
    def _scrap_columns_values(table):
        return [ td.text for tr in table.find("tr")[1:] for td in tr.find("td") ]

    def _rework_data(self,
                     values,
                     columns_names,
                     parameters: MeteocielDailyParameters):

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

        df = pd.DataFrame( np.array(values)
                             .reshape(n_rows, n_cols),
                          columns=columns_names )

        # (2)
        vent_rafale = df[["heure", "vent (rafales)"]].copy(deep=True)
        df = df[ [col for col in df.columns if col not in ("vent (rafales)", "winddir", "temps")] ]

        # (3)
        not_numeric = ["date", "heure", "neb"]
        numerics = [x for x in df.columns if x not in not_numeric]

        f_num_extract = np.vectorize(lambda string : np.NaN if string in("---", "")
                                                     else 0 if string in ("aucune", "traces")
                                                     else float(re.findall(self.TEMPLATE_PRECIPITATION, string)[0]))

        f_rework_dates = np.vectorize(lambda heure :      f"{parameters.year_str}-{parameters.month_str}-{parameters.day_str} 0{int(heure)}:00:00" if heure < 10
                                                     else f"{parameters.year_str}-{parameters.month_str}-{parameters.day_str} {int(heure)}:00:00")

        df["date"] = f_num_extract(df["heure"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])

        df[numerics] = f_num_extract(df[numerics])

        df = df[not_numeric + numerics] # juste pour l'ordre des colonne, avoir la date en 1er

        # (4)
        separated = [ x.split("(") for x in vent_rafale["vent (rafales)"].values ]

        for x in [ separated.index(x) for x in separated if len(x) != 2 ]:
            separated[x].append("")

        separated = np.array(separated)
        separated = f_num_extract(separated)
        separated = pd.DataFrame(separated, columns=["vent", "rafales"])
        separated["heure"] = vent_rafale["heure"]

        # (5)
        df = pd.merge(df,
                      separated,
                      on="heure",
                      how="inner")

        df = df.drop(["heure"], axis=1)
        df = df.sort_values(by="date")

        # (6)
        df.columns = [ f"{col}_{self.UNITS[col]}"
                       if col not in ("date", "neb", "humidex", "windchill") else col
                       for col in df.columns ]

        return df
