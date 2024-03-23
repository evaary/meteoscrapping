from typing import List

import numpy as np
import pandas as pd

from app.boite_a_bonheur.MonthsEnum import MonthEnum
from app.scrappers.abcs import MeteoScrapper
from app.scrappers.exceptions import ScrapException
from app.tps.tps_module import TaskParameters


class OgimetDaily(MeteoScrapper):

    # override
    @staticmethod
    def _scrap_columns_names(table):
        """
        Récupération du nom des colonnes.
        """
        """
        (1) On récupère les 2 tr du thead de la table de données sur ogimet dans trs.
            Le 1er contient les noms principaux des colonnes, le 2ème 6 compléments.
            Les 3 premiers compléments sont pour la température, les 3 suivants pour le vent.

        (2) On initialise une liste de liste, de la même longueur que la liste des noms
            principaux. Ces listes contiendront les subnames associés à chaque main name.
            Pour température et vent, on a max 3 subnames chacun. Les autres listes sont vides.
            On remplit les listes avec les valeurs de subnames associés.

        (3) On établit la liste des noms de colonnes en associant les noms prinicpaux
            et leurs compléments. On remplace les sauts de lignes et les espaces par des _ .
            On passe en minuscules avec lower et on supprime les espaces avec strip.
            On reforme l'unité de température.

        (4) La colonne daily_weather_summary compte pour 8, on n'a qu'1 nom sur les 8.
            On en rajoute 7.
        """
        # (1)
        try:
            trs = table.find("thead")[0]\
                       .find("tr")
            main_names = [th.text for th in trs[0].find("th")]
            complements = [th.text for th in trs[1].find("th")]

        except (AttributeError,
                IndexError):
            raise ScrapException()

        # (2)
        sub_names = [[""] for _ in range(len(main_names))]
        try:
            temperature_index = main_names.index([x
                                                  for x in main_names
                                                  if "Temperature" in x][0])
            sub_names[temperature_index] = [x
                                            for x in complements
                                            if x in ["Max", "Min", "Avg", "Max.", "Min.", "Avg."]]
        except IndexError:
            pass
        try:
            wind_index = main_names.index([x
                                           for x in main_names
                                           if "Wind" in x][0])
            sub_names[wind_index] = [x
                                     for x in complements
                                     if x in ["Dir.", "Int.", "Gust.", "Dir", "Int", "Gust"]]
        except IndexError:
            pass
        # (3)
        columns_names = [f"{main.strip()} {sub.strip()}".strip()
                                                        .lower()
                                                        .replace("\n", "_")
                                                        .replace(" ", "_")
                                                        .replace("(c)", "(°C)")
                                                        .replace(".", "")
                         for main, subs in zip(main_names, sub_names)
                         for sub in subs]
        # (4)
        if "daily_weather_summary" in columns_names:
            columns_names += [f"daily_weather_summary_{i}" for i in range(7)]

        return columns_names

    # override
    @staticmethod
    def _scrap_columns_values(table):
        """
        Récupération des valeurs du tableau.
        """
        try:
            return [td.text for td in table.find("tbody")[0]
                                           .find("td")]
        except (AttributeError,
                IndexError):
            raise ScrapException()

    @staticmethod
    def _fill_missing_values(values: "List[str]",
                             n_cols: int,
                             tp: TaskParameters):
        """
        Comble les manques dans les lignes en ajoutant des "" à la fin.
        @params
            values : la liste des valeurs récupérées dans le tableau.
            n_cols : nombre de colonnes du tableau.
            tp : les paramètres du job courant

        @return
            la liste complétée des valeurs du tableau.
        """
        """
        (0) Dimensions du futur tableau de données et nombre de valeurs collectées. S'il manque des
            données dans la liste des valeurs récupérées, on la complètera pour avoir 1 valeur par cellule
            dans le futur dataframe.
            S'il ne manque rien, on renvoie la liste tel quel.
        (1) done contient les valeurs traitées, todo les valeurs à traiter.
        (2) Tant que done n'est pas complet, on sélectionne l'équivalent d'1 ligne dans todo.
        (3) On compte le nombre de dates présentes dans la ligne. S'il y en a plus d'1,
            la ligne est en fait un mélange de 2 lignes. On ne récupère que les valeurs
            allant de la 1ère date incluse à la 2ème exclue.
        (4) Si besoin, on complète la ligne jusqu'à avoir n_cols valeurs dedans.
        (5) On ajoute la ligne désormais complète aux valeurs traitées, on retire des
            valeurs à traiter les valeurs qu'on a retenu, si la ligne était un mélange.
        """
        # (0)
        n_rows = MonthEnum.from_id(tp.month).ndays
        n_expected = n_rows * n_cols
        n_values = len(values)

        if n_values == n_expected:
            return values

        # (1)
        done = []
        todo = values.copy()

        while len(done) != n_expected:
            # (2)
            row = todo[:n_cols]

            # (3)
            dates = [x for x in row if f"{tp.month_as_str}/" in x]

            if len(dates) != 1:
                index = row.index(dates[1])
                row = row[:index]
            # (4)
            actual_length = len(row)
            toadd = n_cols - actual_length
            row += [""] * toadd

            # (5)
            done += row
            todo = todo[actual_length:]

        return done

    # override
    def _rework_data(self,
                     values,
                     columns_names,
                     tp):
        """
        Mise en forme du tbleau de tableau, conversions des unités si besoin.
        """
        """
        (1) Ogimet gère mal les trous dans les données.
            Si certaines valeurs manquent en début ou milieu de ligne,
            elle sont comblées par "---", et tout va bien, on a des valeurs quand même.

            Si les valeurs manquantes sont à la fin, la ligne s'arrête prématurément.
            Elle compte moins de valeurs qu'attendu, on ne peut pas reconstruire le tableau.

            _fill_missing_values comble les manques dans les lignes en ajoutant des "" à la fin.

        (2) La liste des valeurs récupérées est de dimension 1,x. On la convertit en matrice de
            dimensions n_rows, n_cols puis en dataframe.
        (3) La colonne date est au format MM/JJ, on la convertit au format AAAA-MM-JJ et on trie.
        (4) Les valeurs sont au format str, on les convertit en numérique colonne par colonne.
        (5) La colonne wind_(km/h)_dir contient des str, on remplace les "---" par "" pour les
            valeurs manquantes.
        (6) On supprime les colonnes daily_weather_summary si elles existent en conservant les
            colonnes qui n'ont pas daily_weather_summary dans leur nom.
        """
        # (1)
        n_cols = len(columns_names)
        values = self._fill_missing_values(values,
                                           n_cols,
                                           tp)
        # (2)
        df = pd.DataFrame(np.array(values)
                            .reshape(-1, n_cols),
                          columns=columns_names)
        # (3)
        df["date"] = tp.year_as_str + "/" + df["date"]
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(by="date")

        # (4)
        numeric_cols = [col
                        for col in df.columns
                        if col not in ["date", "wind_(km/h)_dir"]]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        # (5)
        try:
            col = "wind_(km/h)_dir"
            indexes = df[df[col].str.contains("-")].index
            df.loc[indexes, col] = ""
        except KeyError:
            pass
        # (6)
        df = df[[col
                 for col in df.columns
                 if "daily_weather_summary" not in col]]
        return df
