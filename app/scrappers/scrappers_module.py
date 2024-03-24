from threading import Timer
from multiprocessing import current_process
import re
import numpy as np
import pandas as pd
from abc import (ABC,
                 abstractmethod)
from typing import List
from time import perf_counter
from app.scrappers.scrapping_exceptions import (ProcessException,
                                                ReworkException,
                                                ScrapException,
                                                HtmlPageException)
from app.ucs.ucs_module import ScrapperUC
from app.tps.tps_module import TaskParameters
from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.boite_a_bonheur.MonthsEnum import MonthEnum
from requests_html import (Element,
                           HTMLSession)


class MeteoScrapper(ABC):

    PROGRESS_TIMER_INTERVAL = 10  # en secondes

    def __init__(self):

        self.errors = dict()
        # date de départ de lancement des jobs
        self._start = 0
        # quantité de jobs traités
        self._done = 0
        # quantité de jobs à traiter
        self._todo = 0
        # % de jobs traités
        self._progress = 0
        # vitesse en % / s
        self._speed = 0

    def _update(self):
        self._done += 1
        self._progress = round(self._done / self._todo * 100, 0)
        self._speed = round(self._progress / perf_counter() - self._start, 0)

    def _print_progress(self, should_stop=False) -> None:
        print(f"{self.__class__.__name__} ({current_process().pid}) - {self._progress}% - {round(perf_counter() - self._start, 0)}s \n")

        if not should_stop:
            timer = Timer(self.PROGRESS_TIMER_INTERVAL, self._print_progress)
            timer.daemon = True
            timer.start()

    @staticmethod
    def _load_html(tp: TaskParameters):

        try:
            with HTMLSession() as session:
                html_page = session.get(tp.url)
                html_page.html.render(sleep=tp.waiting,
                                      keep_page=True,
                                      scrolldown=1)
            if html_page.status_code != 200:
                raise HtmlPageException()

        except Exception:
            raise HtmlPageException()

        attr = tp.criteria.get_css_attr()
        val = tp.criteria.get_attr_value()
        table: Element = [tab
                          for tab in html_page.html.find("table")
                          if attr in tab.attrs and tab.attrs[attr] == val][0]
        try:
            is_invalid = "no valid" in table.find("thead")[0]\
                                            .find("th")[0]\
                                            .text\
                                            .lower()\
                                            .strip()
            table = None if is_invalid else table

        except IndexError:
            pass

        if table is None:
            raise HtmlPageException()

        return table

    @abstractmethod
    def _scrap_columns_names(self, table: Element) -> "List[str]":
        pass

    @abstractmethod
    def _scrap_columns_values(self, table: Element) -> "List[str]":
        pass

    @abstractmethod
    def _rework_data(self,
                     values: "List[str]",
                     columns_names: "List[str]",
                     tp: TaskParameters) -> pd.DataFrame:
        pass

    def scrap_from_uc(self, uc: ScrapperUC):

        global_df = pd.DataFrame()

        self._todo = sum([1 for _ in uc.to_tps()])
        self._start = perf_counter()
        self._print_progress()

        for tp in uc.to_tps():
            try:
                html_data = self._load_html(tp)
                col_names = self._scrap_columns_names(html_data)
                values = self._scrap_columns_values(html_data)
                local_df = self._rework_data(values,
                                             col_names,
                                             tp)
            except ProcessException as e:

                self.errors[tp.key] = {"url": tp.url,
                                       "error": str(e)}
                self._update()
                continue

            global_df = pd.concat([global_df, local_df])
            self._update()

        global_df.sort_values(by="date")

        self._print_progress(should_stop=True)

        return global_df

    @staticmethod
    def scrapper_instance(uc: ScrapperUC) -> "MeteoScrapper":
        # Association entre le type de scrapper des UCs et la classe scrapper à instancier.
        # Les None ne posent pas de problème car lors de la lecture du fichier config,
        # on contrôle que tous les UCs sont bien pris en charge.
        # TODO : faire de ce truc un attribut de classe
        scrappers = {ScrapperType.WUNDERGROUND_HOURLY: None,
                     ScrapperType.WUNDERGROUND_DAILY: WundergroundDaily,

                     ScrapperType.OGIMET_HOURLY: OgimetHourly,
                     ScrapperType.OGIMET_DAILY: OgimetDaily,

                     ScrapperType.METEOCIEL_HOURLY: MeteocielHourly,
                     ScrapperType.METEOCIEL_DAILY: MeteocielDaily}

        return scrappers[uc.scrapper_type]()


class MeteocielDaily(MeteoScrapper):

    UNITS = {"temperature": "°C",
             "precipitations": "mm",
             "ensoleillement": "h"}

    # Regex pour récupérer uniquement les float d'une string.
    REGEX_FOR_NUMERICS = r'-?\d+\.?\d*'

    # override
    def _scrap_columns_names(self, table):
        """
        Récupération du nom des colonnes.
        """
        """"
        (1) On récupère les noms des colonnes contenus dans la 1ère ligne du tableau.
        (2) Certains caractères à accents passent mal, on les remplace, et on enlève les "." .
        (3) On remplace les espaces par des _, on renomme la colonne jour en date.
        (4) La dernière colonne contient des images et n'a pas de noms. On la supprimera,
            on la nomme to_delete.
        """
        try:
            # (1)
            columns_names = [td.text.lower() for td in table.find("tr")[0].find("td")]
            # (2)
            columns_names = [col.replace("ã©", "e").replace(".", "") for col in columns_names]
            # (3)
            columns_names = ["date" if col == "jour" else "_".join(col.split(" ")) for col in columns_names]
            # (4)
            columns_names = ["to_delete" if col == "" else col for col in columns_names]

        except (AttributeError,
                IndexError):
            raise ScrapException()

        return columns_names

    # override
    def _scrap_columns_values(self, table):
        """
        Récupération des valeurs du tableau.
        """
        """
        On récupère les valeurs des cellules de toutes les lignes,
        sauf la 1ère (noms des colonnes) et la dernière (cumul / moyenne mensuel).
        """
        try:
            return [td.text
                    for tr in table.find("tr")[1:-1]
                    for td in tr.find("td")]
        except (AttributeError,
                IndexError):
            raise ScrapException()

    # override
    def _rework_data(self,
                     values,
                     columns_names,
                     tp):
        """
        Mise en forme du tableau de tableau, conversions des unités si besoin.
        """
        """
        (0) On ajoute au nom de la colonne son unité.
        (1) On définit les dimensions du tableau puis on le créé.
        (2) Si une colonne to_delete existe, on la supprime.
        (3) Le tableau ne contient que des string composées d'une valeur et d'une unité.
            La fonction lambda renvoie la valeur trouvée dans une string, convertie en float si elle existe, ou nan.
            On définit aussi une fonction lambda vectorisée qui met la date en forme.
        (4) On reconstruit les dates à partir des numéros des jours extraits de la colonne des dates.
        (5) On extrait les valeurs des autres colonnes.
        (6) On trie le dataframe selon la date.
        """
        # (0)
        columns_names = [f"{col}_{self.UNITS[col.split('_')[0]]}"
                         if     col not in ("date", "to_delete")
                            and col.split('_')[0] in self.UNITS.keys()
                         else col
                         for col in columns_names]
        # (1)
        n_rows = len(values) // len(columns_names)
        n_cols = len(columns_names)
        df = pd.DataFrame(np.array(values)
                            .reshape(n_rows, n_cols),
                          columns=columns_names)
        # (2)
        try:
            df = df.drop("to_delete", axis=1)
        except KeyError:
            pass
        # (3)
        f_num_extract = np.vectorize(lambda string: np.NaN if string in ("---", "")
                                                    else 0 if string in ("aucune", "traces")
                                                    else float(re.findall(self.REGEX_FOR_NUMERICS, string)[0]))

        f_rework_dates = np.vectorize(lambda day:      f"{tp.year_as_str}-{tp.month_as_str}-0{int(day)}" if day < 10
                                                  else f"{tp.year_as_str}-{tp.month_as_str}-{int(day)}")
        try:
            # (4)
            df["date"] = f_num_extract(df["date"])
            df["date"] = f_rework_dates(df["date"])
            df["date"] = pd.to_datetime(df["date"])
            # (5)
            df.iloc[:, 1:] = f_num_extract(df.iloc[:, 1:])

        except ValueError:
            raise ReworkException()

        # (6)
        df = df.sort_values(by="date")

        return df


class MeteocielHourly(MeteoScrapper):

    UNITS = {"visi": "km",
             "temperature": "°C",
             "point_de_rosee": "°C",
             "humidite": "%",
             "vent": "km/h",
             "rafales": "km/h",
             "pression": "hPa",
             "precip": "mm"}

    # Regex pour récupérer uniquement les float d'une string.
    REGEX_FOR_NUMERICS = r'-?\d+\.?\d*'

    # override
    def _scrap_columns_names(self, table):
        """
        Récupération du nom des colonnes.
        """
        try:
            columns_names = [td.text.lower() for td in table.find("tr")[0].find("td")]
            columns_names = [col.replace("ã©", "e")
                                .replace(".", "")
                             for col in columns_names]
            columns_names = [col.split("\n")[0] if "\n" in col else col for col in columns_names]
            columns_names = [col if col != "humi" else "humidite" for col in columns_names]

            # La colonne vent est composée de 2 sous colonnes: direction et vitesse.
            # Le tableau compte donc n colonnes mais n-1 noms de colonnes.
            # On rajoute donc un nom pour la colonne de la direction du vent.
            indexe = columns_names.index("vent (rafales)")
            columns_names.insert(indexe, "winddir")
            columns_names = [col if "rosee" not in col else col.replace(" ", "_") for col in columns_names]
        except (AttributeError,
                IndexError):
            raise ScrapException()

        return columns_names

    # override
    def _scrap_columns_values(self, table):
        """
        Récupération des valeurs du tableau.
        """
        try:
            return [td.text
                    for tr in table.find("tr")[1:]
                    for td in tr.find("td")]
        except (AttributeError,
                IndexError):
            raise ScrapException()

    @staticmethod
    def _fill_missing_values(values: "list[str]", n_cols: int):
        """
        Des lignes correspondant aux données pour une heure peuvent manquer.
        On complète les données s'il en manque.

        @param
            values : La liste des données récupérées.
            n_cols : le nombre de colonnes du tableau.

        @return
            la liste des valeurs, complétée.
        """
        n_rows = 24
        n_expected = n_rows * n_cols
        n_values = len(values)

        if n_values == n_expected:
            return values

        hours = [f"{x} h" for x in range(0, 24)]
        missing_hours = [x for x in hours if x not in values]

        for hour in missing_hours:
            line_to_add = [hour]
            line_to_add.extend(["" for _ in range(n_cols - 1)])
            values.extend(line_to_add)

        return values

    # override
    def _rework_data(self,
                     values,
                     columns_names,
                     tp):
        """
        Mise en forme du tableau de tableau, conversions des unités si besoin.
        """
        """
        (1) On définit les dimensions du tableau puis on le créé.
        (2) On met de coté la colonne vent car il faut la séparer en 2.
            On supprime les colonnes inutiles.
        (3) On convertit les valeurs du format string vers le format qui leur vont.
        (4) Séparation de la colonne "vent (rafales)" en 2 colonnes "vent" et "rafales".
            Les valeurs contenues dans "vent (rafales)" sont normalement de la forme :
              - x km/h (y km/h)
              - x km/h
            On splite selon la ( pour avoir les 2 valeurs dans 2 str différentes.
            Si le split rend une liste d'1 seule valeur, on rajoute une str vide pour bien avoir 2 valeurs.
        (5) On réunit les données, on met en forme le tableau.
        (6) On ajoute au nom de la colonne son unité.
        """
        # (1)
        n_rows = 24
        n_cols = len(columns_names)
        values = self._fill_missing_values(values, n_cols)

        try:
            df = pd.DataFrame(np.array(values)
                                .reshape(n_rows, n_cols),
                              columns=columns_names)
        except ValueError:
            raise ReworkException()
        # (2)
        vent_rafale = df[["heure", "vent (rafales)"]].copy(deep=True)
        df = df[[col
                 for col in df.columns
                 if col not in ("vent (rafales)", "winddir", "temps")]]
        # (3)
        not_numeric = ["date", "heure", "neb"]
        numerics = [x for x in df.columns if x not in not_numeric]

        f_num_extract = np.vectorize(lambda string: np.NaN if string in ("---", "")
                                                    else 0 if string in ("aucune", "traces")
                                                    else float(re.findall(self.REGEX_FOR_NUMERICS, string)[0]))

        f_rework_dates = np.vectorize(lambda heure:      f"{tp.year_as_str}-{tp.month_as_str}-{tp.day_as_str} 0{int(heure)}:00:00" if heure < 10
                                                    else f"{tp.year_as_str}-{tp.month_as_str}-{tp.day_as_str} {int(heure)}:00:00")
        try:
            df["date"] = f_num_extract(df["heure"])
            df["date"] = f_rework_dates(df["date"])
            df["date"] = pd.to_datetime(df["date"])
            df[numerics] = f_num_extract(df[numerics])
        except ValueError:
            raise ReworkException()

        df = df[not_numeric + numerics]  # juste pour l'ordre des colonne, avoir la date en 1er

        # (4)
        separated = [x.split("(") for x in vent_rafale["vent (rafales)"].values]
        for x in separated:
            if len(x) != 2:
                x.append("")
        try:
            separated = np.array(separated)
            separated = f_num_extract(separated)
            separated = pd.DataFrame(separated, columns=["vent", "rafales"])
            separated["heure"] = vent_rafale["heure"]
        except ValueError:
            raise ReworkException()
        # (5)
        df = pd.merge(df,
                      separated,
                      on="heure",
                      how="inner")

        df = df.drop(["heure"], axis=1)
        df = df.sort_values(by="date")

        # (6)
        df.columns = [f"{col}_{self.UNITS[col]}"
                      if    col not in ("date", "neb", "humidex", "windchill")
                        and col in self.UNITS.keys()
                      else col
                      for col in df.columns]
        return df


class OgimetDaily(MeteoScrapper):

    # override
    def _scrap_columns_names(self, table):
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
    def _scrap_columns_values(self, table):
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


class OgimetHourly(MeteoScrapper):

    def _scrap_columns_names(self, table: Element) -> "List[str]":
        pass

    def _scrap_columns_values(self, table: Element) -> "List[str]":
        pass

    def _rework_data(self, values: "List[str]", columns_names: "List[str]", tp: TaskParameters) -> pd.DataFrame:
        pass


class WundergroundDaily(MeteoScrapper):

    UNITS_CONVERSION = {

        "dew": {"new_name": "dew_point_°C",
                "func": (lambda x: (x - 32) * 5/9)},

        "wind": {"new_name": "wind_speed_(km/h)",
                 "func": (lambda x: x * 1.609344)},

        "pressure": {"new_name": "pressure_(hPa)",
                     "func": (lambda x: x * 33.86388)},

        "humidity": {"new_name": "humidity_(%)",
                     "func": (lambda x: x)},

        "temperature": {"new_name": "temperature_°C",
                        "func": (lambda x: (x - 32) * 5/9)},

        "precipitation": {"new_name": "precipitation_(mm)",
                          "func": (lambda x: x * 25.4)}
    }

    # override
    def _scrap_columns_names(self, table):
        """
        Récupération du nom des colonnes.
        """
        try:
            return [td.text for td in table.find("thead")[0]
                                           .find("td")]
        except (AttributeError,
                IndexError):
            raise ScrapException()

    # override
    def _scrap_columns_values(self, table):
        """
        Récupération des valeurs du tableau.
        """
        """
        La structure html du tableau est tordue, ce qui conduit à des doublons dans values.
        Daily Observations compte 7 colonnes principales et 17 sous-colonnes.
        Elle est donc de dimension (lignes, sous-colonnes).
        values devrait être de longueur lignes * sous-colonnes.
        Elle est en réalité de longueur lignes * sous-colonnes + 7. Il y a 7 valeurs additionnelles.
        Pour janvier 2020 à bergamo, la 1ère des 7 valeurs additionnelles sera "Jan\n1\n2...",
        la 2ème valeur sera "Max\nAvg\nMin\n52\n39.9\n32\n...",
        la nième valeur contient les données de la nième colonne principale,
        et donc de toutes ses sous-colonnes.
        On récupère ces 7 valeurs additionnelles qui contiennent le caractère \n.
        """
        try:
            return [td.text
                    for td in table.find("tbody")[0]
                                   .find("td")
                    if "\n" in td.text]
        except (AttributeError,
                IndexError):
            raise ScrapException()

    # override
    def _rework_data(self,
                     values,
                     columns_names,
                     tp):
        """
        Mise en forme du tableau de tableau, conversions des unités si besoin.
        """
        """
        (1) values est une liste de str. Chaque str contient toutes les données d'1 colonne principale
            séparées par des \n ("x\nx\nx\nx..."). On convertit ces str en liste de données [x,x,x, ...].
            values devient une liste de listes.
            On définit aussi le nombre de ligne comme étant égal à la longueur de la 1ère liste de values,
            qui correspond à la colonne Time.
        (2) On initialise la matrice qui constituera le dataframe final avec la 1ère liste (Time) 
            transformée en vecteur colonne.
        (3) Le dataframe aura besoin de noms pour ses colonnes. Le nom final est composé d'un nom
            principal et d'un complément, sauf pour les colonnes Time et Précipitations.
            Les noms principaux sont contenus dans main_names, les compléments correspondent aux 1 ou 3
            premières valeurs des listes dans values. Pour chaque liste, on détermine le nombre de colonnes
            qu'elle contient, et on récupère les compléments (si elle compte pour 3 colonnes, on prend les 3
            premières valeurs). On transforme la liste courante en vecteur colonne ou en matrice à 3 colonnes,
            puis on accolle ces colonnes au dataframe principal.
        (4) Les main_names ne vont pas, les unités précisées ne vont pas, il y a des majuscules et des espaces.
            On veut tout en minsucule, avec des _ et dans les bonnes unités.
            On remplace les main_names par leurs nouvelles valeurs : si la clé du dict UNITS_CONVERSION est présente
            dans le main_name, on remplace et on passe au main_name suivant.
            Ensuite, on associe les main_names avec leurs sub_names.
            Enfin, le nom de la colonne des dates est actuellement Time. On le remplace par date.
        (5) On créé le dataframe final à partir de la matrice et des noms de colonnes. La 1ère ligne,
            contenant les compléments, est supprimée.
        (6) La colonne date ne contient que les numéros du jour du mois (1 à 31, ou moins). On remplace
            par la date au format AAAA-MM-JJ et on trie.
        (7) Jusqu'ici les valeur du dataframe sont au format str. On les convertit en numérique.
        (8) On convertit vers les unités classiques .
        """
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

                if key in main_name.lower()\
                                   .strip():
                    columns_names[index] = self.UNITS_CONVERSION[key]["new_name"]
                    break

        final_col_names = ["_".join([main, sub.strip().lower()])
                           if sub else main
                           for main, subs in zip(columns_names, sub_names)
                           for sub in subs]
        final_col_names[0] = "date"

        # (5)
        df = pd.DataFrame(df, columns=final_col_names)
        df = df.drop([0], axis="index")

        # (6)
        df["date"] = [f"{tp.year_as_str}/{tp.month_as_str}/0{day}"
                      if int(day) < 10
                      else f"{tp.year_as_str}/{tp.month_as_str}/{day}"
                      for day in df.date]

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
