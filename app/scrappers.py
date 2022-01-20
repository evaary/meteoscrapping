from requests_html import HTMLSession
from abc import ABC, abstractmethod
import numpy as np
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
        # On affiche dans le terminal le job en cours.
        # (2) On reconstitue l'url et on charge la page html correspondante. S'il y a une erreur,
        # on le signale et on passe au tuple suivant.
        # (3) On récupère la table de données html. Si elle n'existe pas, on le signal
        # et on passe au tuple suivant.
        # (4) On convertit le mois (int) en string, on en aura besoin plus tard.
        # (5) On récupère le noms des colonnes et les valeurs de la table de données html.
        # (6) On met les données sous forme de dataframe.
        # Si on ne peut pas, on le signale et on passe à la table suivante.
        
        for todo in self._todos:
            # (1)
            year, month = todo
            # (2)
            url = self._set_url(year, month)
            print(f"\n{self.SCRAPPER} {year} {month} {self._city} - {url}")
            
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
            month = "0" + str(month) if month < 10 else str(month)
            # (5)
            try:
                col_names = self._scrap_columns_names(table)
                values = self._scrap_columns_values(table)
            except Exception:
                error = "error while scrapping data"
                self.errors[f"{self._city}_{year}_{month}"] = {"url": url, "error": error}
                print(f"\t{error}")
                continue
            # (6)
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
    BASE_URL = f"http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind="
    
    def from_config(self, config):
        
        self.errors = {}
        self._url = self.BASE_URL + config["ind"]
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

    def _set_url(self, year, month):

        m = "0" + str(month) if month < 10 else str(month)
        
        return self._url + f"&ano={str(year)}&mes={self.ASSOCIATIONS[m]['num']}&day=0&hora=0&min=0&ndays={self.ASSOCIATIONS[m]['days']}"

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

        self.errors = {}
        self._url = self.BASE_URL + f"{config['country_code']}/{config['city']}/{config['region']}/date"
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

    def _set_url(self, year, month):
        return self._url + f"/{str(year)}-{str(month)}"

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
        # (1) La structure html du tableau est tordue, ce qui conduit à des doublons dans values.
        # Daily Observations compte 7 colonnes principales et 17 sous-colonnes.
        # Elle est donc de dimension (lignes, sous-colonnes).
        # values devrait être de longueur lignes * sous-colonnes.
        # Elle est en réalité de longueur lignes * sous-colonnes + 7.
        # Pour janvier 2020 à bergamo, la 1ère des 7 valeurs additionnelles sera "Jan\n1\n2...",
        # la 2ème valeur sera "Max\nAvg\nMin\n52\n39.9\n32\n...",
        # la nième valeur contient les données de la nième colonne principale,
        # et donc de toutes ses sous-colonnes.
        # On récupère ces 7 valeurs additionnelles qui contiennent le caractère \n.
        
        values = [td.text for td in table.find("tbody")[0].find("td")]
        # (1)
        values = [value for value in values if "\n" in value]

        return values

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

class MeteocielScrapper(BaseScrapper):
    pass
