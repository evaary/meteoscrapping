from threading import Timer
import re
import numpy as np
import pandas as pd
from abc import (ABC,
                 abstractmethod)
from typing import (List,
                    Tuple)
from time import perf_counter

from app.exceptions.scrapping_exceptions import (ReworkException,
                                                 ScrapException,
                                                 HtmlPageException)
from app.ucs_module import ScrapperUC
from app.tps_module import TaskParameters
from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.boite_a_bonheur.MonthEnum import MonthEnum
from requests_html import (Element,
                           HTMLSession)


class MeteoScrapper(ABC):

    PROGRESS_TIMER_INTERVAL = 10  # en secondes

    def __init__(self):
        self._errors = dict()
        # date de départ de lancement des jobs
        self._start = 0
        # quantité de jobs traités
        self._done = 0
        # quantité de jobs à traiter
        self._todo = 0
        # % de jobs traités
        self._progress = 0

    @property
    def errors(self):
        return self._errors.copy()

    def _update(self) -> None:
        self._done += 1
        self._progress = round(self._done / self._todo * 100, 0)

    def _print_progress(self,  uc: ScrapperUC) -> None:

        print(f"{uc} - {self._progress}% - {round(perf_counter() - self._start, 0)}s \n")

        if self._progress == 100:
            return

        timer = Timer(self.PROGRESS_TIMER_INTERVAL, self._print_progress, [uc])
        timer.daemon = True
        timer.start()

    @staticmethod
    def scrapper_instance(uc: ScrapperUC) -> "MeteoScrapper":
        """Renvoie l'instance de scrapper adapté à l'UC."""
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

    def scrap_uc(self, uc: ScrapperUC) -> pd.DataFrame:
        """Télécharge les données et renvoie les résultats."""
        global_df = pd.DataFrame()

        self._todo = sum([1 for _ in uc.to_tps()])
        self._start = perf_counter()
        self._print_progress(uc)

        for tp in uc.to_tps():
            try:
                html_data = self._load_html(tp)
                col_names = self._scrap_columns_names(html_data)
                values = self._scrap_columns_values(html_data)
                values = self._fill_partial_rows(values, len(col_names), tp)
                local_df = self._rework_data(values, col_names, tp)
                local_df = self._add_missing_rows(local_df, tp)
                global_df = pd.concat([global_df, local_df])

                global_df = global_df[["date"] + [x for x in global_df.columns if x != "date"]]
                global_df = global_df.sort_values(by="date")

            except Exception as e:
                self.errors[tp.key] = {"url": tp.url, "erreur": str(e)}
                continue
            finally:
                self._update()

        self._print_progress(uc)

        return global_df

    @staticmethod
    def _load_html(tp: TaskParameters) -> Element:
        """Charge une page html à scrapper et renvoie la table de données trouvée."""
        html_loading_trials = 3
        html_page = None
        while html_page is None and html_loading_trials > 0:

            if html_loading_trials < 3:
                print("retrying...")

            try:
                with HTMLSession() as session:
                    html_page = session.get(tp.url)
                    html_page.html.render(sleep=tp.waiting,  # .html n'est pas trouvé mais est essentiel
                                          keep_page=True,
                                          scrolldown=1)
                if html_page.status_code != 200:
                    html_page = None
            except Exception:
                html_loading_trials -= 1
                html_page = None

        if html_page is None:
            raise HtmlPageException()

        attr = tp.criteria.css_attribute
        val = tp.criteria.attribute_value
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
    def _scrap_columns_names(self, table: Element) -> List[str]:
        """Renvoie les noms des colonnes de la table."""
        pass

    @abstractmethod
    def _scrap_columns_values(self, table: Element) -> List[str]:
        """Renvoie les données contenues dans la table."""
        pass

    def _fill_partial_rows(self,
                           values: List[str],
                           n_cols: int,
                           tp: TaskParameters) -> List[str]:
        """Complète les lignes auxquelles il manque des valeurs avec des str vides."""

        # (1) values contient des lignes incomplètes si sa taille n'est pas un multiple de n_cols.
        #     Si toutes les lignes sont complètes, on a rien à faire.
        # (2) A chaque tour de boucle, on trouve l'indexe des 2 prochaines dates et
        #     on sélectionne les valeurs entre la 1ère date incluse et la 2ème exclue dans row.
        # (3) On complète row avec autant de str que nécessaire pour avoir n_cols valeurs dedans,
        #     on l'ajoute aux valeurs traitées,
        #     on la retire des valeurs à traiter.

        # (1)
        if     len(values) == 0 \
            or len(values) % n_cols == 0:
            return values

        print("_fill_partial_rows : " + tp.url)

        done = []
        while len(values) > 0:
            # (2)
            first_index, second_index = self._next_dates_indexes(values, tp)
            if second_index == -1:
                row = values[first_index:]
            else:
                row = values[first_index:second_index]
            # (3)
            actual_row_length = len(row)
            row.extend([""] * (n_cols - actual_row_length))
            done.extend(row)
            values = values[actual_row_length:]

        return done

    @abstractmethod
    def _next_dates_indexes(self,
                            values: List[str],
                            tp: TaskParameters) -> Tuple[int, int]:
        """Renvoie le tuple des indexes des 2 prochaines dates de values,
        pour la reconstruction des lignes incomplètes"""
        pass

    @abstractmethod
    def _rework_data(self,
                     values: List[str],
                     columns_names: List[str],
                     tp: TaskParameters) -> pd.DataFrame:
        """Mise en forme du tableau de tableau, conversions des unités si besoin."""
        pass

    def _add_missing_rows(self,
                          df: pd.DataFrame,
                          tp: TaskParameters) -> pd.DataFrame:
        """Complète le dataframe si des lignes manquent."""

        # (1) Si le dataframe contient autant de lignes qu'attendu, on a rien à faire.
        # (2) Sinon, on initialise un DataFrame totalement vide, des dimensions attendues,
        #     avec les mêmes colonnes que df.
        # (3) On place la date de chacun des dfs en indexe et on retire de missings tous les indexes de df.
        #     Il ne reste que les lignes manquantes.
        # (4) On ajoute ces lignes aux résultats et on remet la date en colonne.

        # (1)
        n_rows = df.shape[0]
        expected_dates = self._expected_dates(tp)
        if n_rows == len(expected_dates):
            return df

        print("_fill_partial_rows : " + tp.url)
        # (2)
        missings = pd.DataFrame(np.full((len(expected_dates), df.shape[1]), np.NaN),
                                columns=df.columns)
        missings["date"] = pd.to_datetime(expected_dates)
        # (3)
        df = df.set_index("date")
        missings = missings.set_index("date")
        missings = missings.drop(df.index, axis="rows")
        # (4)
        df = pd.concat([df, missings])
        df = df.reset_index()

        return df

    @abstractmethod
    def _expected_dates(self, tp: TaskParameters) -> List[str]:
        """Renvoie la liste des dates attendues pour le tp courant dans le dataframe,
        pour l'ajout des lignes manquantes."""
        pass


class MeteocielDaily(MeteoScrapper):

    UNITS = {"temperature": "°C",
             "temp": "°C",
             "precipitations": "mm",
             "prec": "mm",
             "ensoleillement": "h",
             "vent": "kmh",
             "rafales": "kmh",
             "pression": "hpa"}

    DAYS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    UNWANTED_COLUMNS = ["to_delete", "phenomenes"]

    # Regex pour récupérer uniquement les float d'une string.
    REGEX_FOR_NUMERICS = r'-?\d+\.?\d*'

    def _scrap_columns_names(self, table):

        # (1) On récupère les noms des colonnes contenus dans la 1ère ligne du tableau.
        # (2) Certains caractères à accents passent mal (précipitations, phénomènes).
        #     On les remplace, on enlève les "." et on remplace les espaces par des _.
        #
        # (3) On renomme la colonne jour en date, et la dernière colonne qui n'a pas de nom en to_delete.
        # (4) On ajoute au nom de la colonne son unité.

        try:
            # (1)
            columns_names = [td.text.lower().strip() for td in table.find("tr")[0].find("td")]
            # (2)
            columns_names = [col.replace("ã©", "e")
                                .replace("ã¨", "e")
                                .replace(".", "")
                                .replace(" ", "_")
                             for col in columns_names]
            # (3)
            columns_names = ["date" if col == "jour" else col for col in columns_names]
            columns_names = ["to_delete" if col == "" else col for col in columns_names]
            # (4)
            cols_units = [col.split('_')[0] for col in columns_names]
            cols_units = ["" if colunit not in self.UNITS.keys()
                          else self.UNITS[colunit]
                          for colunit in cols_units]

            columns_names = [colname if colunit == ""
                             else f"{colname}_{colunit}"
                             for colname, colunit in zip(columns_names,
                                                         cols_units)]
        except (AttributeError,
                IndexError):
            raise ScrapException()

        return columns_names

    def _scrap_columns_values(self, table):
        # On récupère les valeurs des cellules de toutes les lignes,
        # sauf la 1ère (noms des colonnes) et la dernière (cumul / moyenne mensuel).
        try:
            return [td.text.strip()
                    for tr in table.find("tr")[1:-1]
                    for td in tr.find("td")]
        except (AttributeError,
                IndexError):
            raise ScrapException()

    def _next_dates_indexes(self, values, tp):
        dates = [x for x in values if x.split(".")[0] in self.DAYS]
        first_index = values.index(dates[0])
        second_index = -1 if len(dates) == 1 else values.index(dates[1])

        return (first_index, second_index)

    def _rework_data(self, values, columns_names, tp):
        # (1) On créé le tableau de données.
        # (2) Suppression des colonnes inutiles. On passe par une compréhension pour éviter les KeyError.
        # (3) Le tableau ne contient que des string composées d'une valeur et d'une unité.
        #     La fonction lambda renvoie la valeur trouvée dans une string, convertie en float si elle existe, ou nan.
        #     On définit aussi une fonction lambda vectorisée qui met la date en forme.
        # (4) On reconstruit les dates à partir des numéros des jours extraits de la colonne des dates.
        # (5) On extrait les valeurs des autres colonnes.

        # (1)
        try:
            df = pd.DataFrame(np.array(values)
                                .reshape(-1, len(columns_names)),
                              columns=columns_names)
        except ValueError:
            raise ReworkException()
        # (2)
        df = df[[x for x in df.columns if x not in self.UNWANTED_COLUMNS]]
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

        return df

    def _expected_dates(self, tp):
        return [f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(x)}"
                for x in range(1, MonthEnum.from_id(tp.month).ndays + 1)]


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

    def _scrap_columns_names(self, table):
        #   (1) Certains caractères à accents passent mal, on les remplace par leur version sans accent.
        #   (2) Certains noms sont sur 2 lignes, on peut se passer de la 2ème.
        #   (3) On renomme humi en humidite et point de rosee en point_de_rosee
        #   (4) La colonne vent est composée de 2 sous colonnes: direction et vitesse.
        #       Le tableau compte donc n colonnes mais n-1 noms de colonnes.
        #       On rajoute donc un nom pour la colonne de la direction du vent.
        try:
            columns_names = [td.text.lower() for td in table.find("tr")[0].find("td")]
            # (1)
            columns_names = [col.replace("ã©", "e")
                                .replace(".", "")
                             for col in columns_names]
            # (2)
            columns_names = [col.split("\n")[0] if "\n" in col else col for col in columns_names]

        except IndexError:
            raise ScrapException()
        # (3)
        try:
            indexe = columns_names.index("humi")
            columns_names[indexe] = "humidite"
        except ValueError:
            pass
        try:
            indexe = columns_names.index("point de rosee")
            columns_names[indexe] = "point_de_rosee"
        except ValueError:
            pass
        # (4)
        indexe = columns_names.index("vent (rafales)")
        columns_names.insert(indexe, "winddir")

        return columns_names

    def _scrap_columns_values(self, table):
        # On enlève la 1ère ligne car elle contient le nom des colonnes
        try:
            return [td.text
                    for tr in table.find("tr")[1:]
                    for td in tr.find("td")]
        except IndexError:
            raise ScrapException()

    def _next_dates_indexes(self, values, tp):
        dates = [f"{x} h" for x in values if x in range(0, 24)]
        first_index = values.index(dates[0])
        second_index = -1 if len(dates) == 1 else values.index(dates[1])

        return (first_index, second_index)

    def _rework_data(self, values, columns_names, tp):
        #   (1) On créé le tableau.
        #   (2) On met de coté la colonne vent car il faut la séparer en 2.
        #       On supprime les colonnes inutiles.
        #   (3) On convertit les valeurs du format string vers le format qui leur vont.
        #   (4) Séparation de la colonne "vent (rafales)" en 2 colonnes "vent" et "rafales".
        #       Les valeurs contenues dans "vent (rafales)" sont normalement de la forme :
        #         - x km/h (y km/h)
        #         - x km/h
        #       On splite selon la ( pour avoir les 2 valeurs dans 2 str différentes.
        #       Si le split rend une liste d'1 seule valeur, on rajoute une str vide pour bien avoir 2 valeurs.
        #   (5) On réunit les données, on met en forme le tableau.
        #   (6) On ajoute au nom de la colonne son unité.

        # (1)
        try:
            df = pd.DataFrame(np.array(values)
                                .reshape(-1, len(columns_names)),
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

    def _expected_dates(self, tp):
        return [f"{tp.year_as_str}-{tp.month_as_str}-{tp.day_as_str} {MonthEnum.format_date_time(x)}:00:00"
                for x in range(0, 24)]


class OgimetDaily(MeteoScrapper):

    NOT_NUMERIC_COLUMNS = ["date",
                           "wind_(km/h)_dir"]

    def _scrap_columns_names(self, table):
        #   (1) On récupère les 2 tr du thead de la table de données sur ogimet dans trs.
        #       Le 1er contient les noms principaux des colonnes, le 2ème 6 compléments.
        #       Les 3 premiers compléments sont pour la température, les 3 suivants pour le vent.
        #   (2) On initialise une liste de liste, de la même longueur que la liste des noms
        #       principaux. Ces listes contiendront les subnames associés à chaque main name.
        #       Pour température et vent, on a max 3 subnames chacun. Les autres listes sont vides.
        #       On remplit les listes avec les valeurs de subnames associés.
        #   (3) On établit la liste des noms de colonnes en associant les noms prinicpaux
        #       et leurs compléments. On remplace les sauts de lignes et les espaces par des _ .
        #       On passe en minuscules avec lower et on supprime les espaces avec strip.
        #       On reforme l'unité de température.
        #   (4) La colonne daily_weather_summary compte pour 8, on n'a qu'1 nom sur les 8.
        #       On en rajoute 7.
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

    def _scrap_columns_values(self, table):
        try:
            return [td.text for td in table.find("tbody")[0]
                                           .find("td")]
        except IndexError:
            raise ScrapException()

    def _next_dates_indexes(self, values, tp):
        dates = [x for x in values if f"{tp.month_as_str}/" in x]
        first_index = values.index(dates[0])
        second_index = -1 if len(dates) == 1 else values.index(dates[1])

        return (first_index, second_index)

    def _rework_data(self, values, columns_names, tp):
        #   (1) Création du dataframe.
        #   (2) La colonne date est au format MM/JJ, on la convertit au format AAAA-MM-JJ.
        #   (3) Les valeurs sont au format str, on les convertit en numérique colonne par colonne.
        #   (4) La colonne wind_(km/h)_dir contient des str, on remplace les "---" par "" pour les
        #       valeurs manquantes.
        #   (5) On supprime les colonnes daily_weather_summary si elles existent en conservant les
        #       colonnes qui n'ont pas daily_weather_summary dans leur nom.

        # (1)
        try:
            df = pd.DataFrame(np.array(values)
                              .reshape(-1, len(columns_names)),
                              columns=columns_names)
        except ValueError:
            raise ReworkException()
        # (2)
        df["date"] = tp.year_as_str + "/" + df["date"]
        df["date"] = pd.to_datetime(df["date"])
        # (3)
        numeric_cols = [col
                        for col in df.columns
                        if col not in self.NOT_NUMERIC_COLUMNS]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        # (4)
        try:
            col = "wind_(km/h)_dir"
            indexes = df[df[col].str.contains("-")].index
            df.loc[indexes, col] = ""
        except KeyError:
            pass
        # (5)
        df = df[[col
                 for col in df.columns
                 if "daily_weather_summary" not in col]]
        return df

    def _expected_dates(self, tp):
        return [f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(x)}"
                for x in range(1, MonthEnum.from_id(tp.month).ndays + 1)]


class OgimetHourly(MeteoScrapper):

    REGEX_FOR_DATES = r'\d+/\d+/\d+'

    def _scrap_columns_names(self, table):
        try:
            col_names = [th.text for th in table.find("tr")[0]
                                                .find("th")]
        except IndexError:
            raise ScrapException()

        col_names = ["_".join(colname.split("\n")) for colname in col_names]
        col_names = [colname.lower()
                            .replace("(c)", "°C")
                            .replace("(mm)", "mm")
                            .replace(" ", "_")
                     for colname in col_names]

        specific_index = col_names.index("date")
        col_names.insert(specific_index + 1, "time")

        return col_names

    def _scrap_columns_values(self, table):
        # On supprime la 1ère ligne (noms des colonnes) et la dernière (data du jour précédent le 1er demandé).
        values = [td.text
                  for tr in table.find("tr")[1:-1]
                  for td in tr.find("td")]

        return values

    def _next_dates_indexes(self, values, tp):
        days = [MonthEnum.format_date_time(tp.day - x) for x in range(0, tp.ndays)]
        days = [f"{tp.month_as_str}/{x}/{tp.year_as_str}" for x in days]
        dates = [x for x in values if x in days]

        first_index = values.index(dates[0])
        # on retire la 1ère valeur trouvée dans values étant donné qu'on cherche potentiellement
        # la 2ème occurrence d'une même date. On rajoite 1 au 2ème indexe pour compenser.
        second_index = -1 if len(dates) == 1 else values[first_index + 1:].index(dates[1]) + 1

        return (first_index, second_index)

    def _rework_data(self, values, columns_names, tp):
        #   (1) On créé le dataframe.
        #   (2) Les colonnes ww, w1 et w2 ne nous intéresse pas.
        #   (3) la date est divisée en 2 colonnes date et heure, on les rassemble, et on formate correctement.
        #   (4) Le format des précipitations est bizarre, on choisit de le laisser sous forme de str.
        #       Parfois la cellule contient 2 données, séparée par un retour à la ligne, on les met bout à bout.
        #       => https://www.ogimet.com/cgi-bin/gsynres?ind=07149&ndays=31&ano=2020&mes=2&day=31&hora=23&lang=en&decoded=yes
        #   (5) On convertit les données au format numérique.

        # (1)
        try:
            df = pd.DataFrame(np.array(values)
                              .reshape(-1, len(columns_names)),
                              columns=columns_names)
        except ValueError:
            raise ReworkException()
        # (2)
        df = df[[x for x in df.columns if x not in ["ww", "w1", "w2"]]]
        # (3)
        try:
            df["datetime"] = df["date"] + ":" + df["time"]
        except:  # exception inconnue levée parfois
            df["datetime"] = []

        df = df.drop(["date", "time"], axis="columns")\
               .rename(columns={"datetime": "date"})

        df["date"] = pd.to_datetime(df["date"],
                                    format="%m/%d/%Y:%H:%M")
        # (4)
        df["prec_mm"] = ["" if "--" in x
                         else "_".join(x.split("\n"))
                         for x in df["prec_mm"].values]
        # (5)
        numeric_columns = [x for x in df.columns if x not in ["date", "ddd", "prec_mm"]]
        for numeric_column in numeric_columns:
            df[numeric_column] = pd.to_numeric(df[numeric_column],
                                               errors="coerce")
        return df

    def _expected_dates(self, tp):
        days = [f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(tp.day - x)}"
                for x in range(0, tp.ndays)]

        hours = [MonthEnum.format_date_time(x) for x in range(0, 24)]

        return [f"{day} {hour}:00:00"
                for day in days
                for hour in hours]


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

    def _scrap_columns_names(self, table):
        try:
            return [td.text for td in table.find("thead")[0]
                                           .find("td")]
        except IndexError:
            raise ScrapException()

    def _scrap_columns_values(self, table):
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
        try:
            return [td.text
                    for td in table.find("tbody")[0]
                                   .find("td")
                    if "\n" in td.text]
        except (AttributeError,
                IndexError):
            raise ScrapException()

    def _next_dates_indexes(self, values, tp):
        # Il est impossible de renvoyer les indexes car on ne peut pas différencier les dates
        # des autres valeurs.
        raise NotImplementedError("WundergroundDaily : _next_dates_indexes n'est pas implémentée")

    def _rework_data(self, values, columns_names, tp):
        #   (1) values est une liste de str. Chaque str contient toutes les données d'1 colonne principale
        #       séparées par des \n ("x\nx\nx\nx..."). On convertit ces str en liste de données [x,x,x, ...].
        #       values devient une liste de listes.
        #       On définit aussi le nombre de ligne comme étant égal à la longueur de la 1ère liste de values,
        #       qui correspond à la colonne Time.
        #   (2) On initialise la matrice qui constituera le dataframe final avec la 1ère liste (Time)
        #       transformée en vecteur colonne.
        #   (3) Le dataframe aura besoin de noms pour ses colonnes. Le nom final est composé d'un nom
        #       principal et d'un complément, sauf pour les colonnes Time et Précipitations.
        #       Les noms principaux sont contenus dans main_names, les compléments correspondent aux 1 ou 3
        #       premières valeurs des listes dans values. Pour chaque liste, on détermine le nombre de colonnes
        #       qu'elle contient, et on récupère les compléments (si elle compte pour 3 colonnes, on prend les 3
        #       premières valeurs). On transforme la liste courante en vecteur colonne ou en matrice à 3 colonnes,
        #       puis on accolle ces colonnes au dataframe principal.
        #   (4) Les main_names ne vont pas, les unités précisées ne vont pas, il y a des majuscules et des espaces.
        #       On veut tout en minsucule, avec des _ et dans les bonnes unités.
        #       On remplace les main_names par leurs nouvelles valeurs : si la clé du dict UNITS_CONVERSION est présente
        #       dans le main_name, on remplace et on passe au main_name suivant.
        #       Ensuite, on associe les main_names avec leurs sub_names.
        #       Enfin, le nom de la colonne des dates est actuellement Time. On le remplace par date.
        #   (5) On créé le dataframe final à partir de la matrice et des noms de colonnes. La 1ère ligne,
        #       contenant les compléments, est supprimée.
        #   (6) La colonne date ne contient que les numéros du jour du mois (1 à 31, ou moins). On remplace
        #       par la date au format AAAA-MM-JJ et on trie.
        #   (7) Jusqu'ici les valeur du dataframe sont au format str. On les convertit en numérique.
        #   (8) On convertit vers les unités classiques .

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

    def _expected_dates(self, tp):
        return [f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(x)}"
                for x in range(1, MonthEnum.from_id(tp.month).ndays + 1)]
