import numpy as np
import pandas as pd
from app.scrappers.abcs import BaseScrapper

class OgimetScrapper(BaseScrapper):
    
    ''' scrapper pour le site ogimet'''
    # La numérotation des mois sur ogimet est décalée.
    # Ce dictionnaire fait le lien entre la numérotation
    # usuelle (clés) et celle de ogimet (num). On définit aussi le nombre
    # de jours et donc de lignes attendues dans le dataframe.
    ASSOCIATIONS = {
        "01": {"num":  2, "days": 31},
        "02": {"num":  3, "days": 28},
        "03": {"num":  4, "days": 31},
        "04": {"num":  5, "days": 30},
        "05": {"num":  6, "days": 31},
        "06": {"num":  7, "days": 30},
        "07": {"num":  8, "days": 31},
        "08": {"num":  9, "days": 31},
        "09": {"num": 10, "days": 30},
        "11": {"num": 12, "days": 30},
        "10": {"num": 11, "days": 31},
        "12": {"num":  1, "days": 31},
    }
    # Critère de sélection qui servira à récupérer le tableau voulu
    CRITERIA = ("bgcolor", "#d0d0d0")
    SCRAPPER = "ogimet"
    BASE_URL = f"http://www.ogimet.com/cgi-bin/gsynres?lang=en&"
    
    def from_config(self, config):
        
        super().from_config(config)
        self._url = self.BASE_URL + f"ind={config['ind']}&"

        return self

    def _set_url(self, year, month):
        return self._url + f"ano={year}&mes={self.ASSOCIATIONS[month]['num']}&day=0&hora=0&min=0&ndays={self.ASSOCIATIONS[month]['days']}"

    @staticmethod
    def _scrap_columns_names(table):
        
        '''_scrap_columns_names : récupère le nom des colonnes du futur dataframe
            args: table (requests_html.Element)
            return: col_names (list)
        '''
        # (1) On récupère les 2 tr du thead de la table de données sur ogimet dans trs.
        # Le 1er contient les noms principaux des colonnes, le 2ème 6 compléments.
        # Les 3 premiers compléments sont pour la température, les 3 suivants pour le vent.
        # (2) On initialise une liste de liste, de la même longueur que la liste des noms
        # principaux. Ces listes contiendront les subnames associés à chaque main name.
        # Pour température et vent, on a max 3 subnames chacun. Les autres listes sont vides.
        # On remplit les listes avec les valeurs de subnames associés.
        # (3) On établit la liste des noms de colonnes en associant les noms prinicpaux
        # et leurs compléments. On remplace les sauts de lignes et les espaces par des _ .
        # On passe en minuscules avec lower et on supprime les espaces avec strip.
        # On reforme l'unité de température
        # (4) la colonne daily_weather_summary compte pour 8, on n'a qu'1 nom sur les 8.
        # On en rajoute 7.
        
        # (1)
        trs = table.find("thead")[0].find("tr")
        main_names = [th.text for th in trs[0].find("th")]
        sub_values = [th.text for th in trs[1].find("th")]
        # (2)
        sub_names = [ [""] for _ in range(len(main_names)) ]

        try:
            T_index = main_names.index([x for x in main_names if "Temperature" in x][0])
            sub_names[T_index] = [x for x in sub_values if x in ["Max", "Min", "Avg", "Max.", "Min.", "Avg."]]
        except IndexError:
            pass

        try:
            W_index = main_names.index([x for x in main_names if "Wind" in x][0])
            sub_names[W_index] = [x for x in sub_values if x in ["Dir.", "Int.", "Gust.", "Dir", "Int", "Gust"]]
        except IndexError:
            pass
        # (3)
        col_names = [
            f"{main.strip()} {sub.strip()}"\
            .strip()\
            .lower()\
            .replace("\n", "_")\
            .replace(" ", "_")\
            .replace("(c)", "(°C)")\
            .replace(".", "")

            for main, subs in zip(main_names, sub_names)
            for sub in subs
        ]
        # (4)
        if "daily_weather_summary" in col_names:
            col_names += [f"daily_weather_summary_{i}" for i in range(7)]

        return col_names

    @staticmethod
    def _scrap_columns_values(table):
        
        '''
        _scrap_columns_values: récupère les valeurs de chaque cellule td de la table html.
            args: table (request-html.Element)
            return: (list)
        '''
        return [td.text for td in table.find("tbody")[0].find("td")]

    @staticmethod
    def _fill_missing_values(values, n_cols, n_filled, month):
        
        '''_fill_missing_values : Ogimet gère mal les trous dans les données.
        Si certaines valeurs manquent en début ou milieu de ligne,
        elle sont comblées par "---", et tout va bien, on a des valeurs quand même.
        Si les valeurs manquantes sont à la fin, la ligne s'arrête prématurément.
        Elle compte moins de valeurs que de colonnes, on ne peut pas reconstruire le tableau.
        Cette fonction comble les manques dans les lignes en ajoutant des "" à la fin.
            args: values (list), n_rows (int), n_cols (int), n_filled (int), month (string)
            return: done (list)
        '''
        # (1) done contient les valeurs traitées, todo les valeurs à traiter.
        # (2) Tant que done n'est pas complet, on sélectionne soit l'équivalent
        # d'1 ligne dans todo, soit todo en entier s'il reste moins de n_cols valeurs.
        # (3) On compte le nombre de dates présentes dans la ligne. S'il y en a plus d'1,
        # la ligne est en fait un mélange de 2 lignes. On ne récupère que les valeurs
        # allant de la 1ère date incluse à la 2ème exclue.
        # (4) Si besoin, on complète la ligne jusqu'à avoir n_cols valeurs dedans.
        # (5) On ajoute la ligne désormais complète aux valeurs traitées, on la retire des
        # valeurs à traiter.
        
        # (1)
        done = []
        todo = values.copy()
        
        while len(done) != n_filled :            
            # (2)
            row = todo[:n_cols]
            # (3)
            dates = [x for x in row if f"{month}/" in x]

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

    @classmethod
    def _rework_data(cls, values, col_names, year, month):
        
        '''_rework_data : mise en forme du dataframe à partir des valeurs récoltées
            args: values (list), col_names (list), year (int), month (str)
            return : df (pandas.DataFrame)
        '''
        # (1) Dimensions du futur tableau de données et nombre de valeurs collectées. S'il manque des
        # données dans la liste des valeurs récupérées, on la complète pour avoir 1 valeur par cellule
        # dans le futur dataframe.
        # (2) La liste des valeurs récupérées est de dimension 1,x. On la convertit en matrice de 
        # dimensions n_rows, n_cols puis en dataframe.
        # (3) La colonne date est au format MM/JJ, on la convertit au format AAAA-MM-JJ et on trie.
        # (4) Les valeurs sont au format str, on les convertit en numérique colonne par colonne.
        # (5) La colonne wind_(km/h)_dir contient des str, on remplace les "---" par "" pour les
        # valeurs manquantes.
        # (6) On supprime les colonnes daily_weather_summary si elles existent en conservant les
        # colonnes qui n'ont pas daily_weather_summary dans leur nom.
        
        # (1)
        n_cols = len(col_names)
        n_rows = cls.ASSOCIATIONS[month]["days"]
        n_filled = n_rows * n_cols
        n_values = len(values)
        
        if n_values != n_filled:
            values = cls._fill_missing_values(values, n_cols, n_filled, month)
        # (2)
        values = np.array(values).reshape(-1, n_cols)
        df = pd.DataFrame(values, columns=col_names)
        # (3)
        df["date"] = str(year) + "/" + df["date"]
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(by="date")
        # (4)
        numeric_cols = [col for col in df.columns if col not in ["date", "wind_(km/h)_dir"]]
        
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
        cols = [col for col in df.columns if "daily_weather_summary" not in col]
        df = df[cols]
        
        return df