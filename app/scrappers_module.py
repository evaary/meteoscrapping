import asyncio
import re
import numpy as np
import pandas as pd
from abc import (ABC,
                 abstractmethod)
from typing import List
from time import perf_counter
from app.exceptions.scrapping_exceptions import (ScrapException,
                                                 HtmlPageException,
                                                 ProcessException)
from app.ucs_module import ScrapperUC, GeneralParametersUC
from app.tps_module import TaskParameters
from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.boite_a_bonheur.MonthEnum import MonthEnum
from requests_html import (Element,
                           HTMLSession)
from concurrent.futures import ProcessPoolExecutor


class MeteoScrapper(ABC):

    LOOP = asyncio.get_event_loop()

    def __init__(self):
        self._errors = dict()

    @property
    def errors(self):
        return self._errors.copy()

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
        start = perf_counter()
        print()
        if GeneralParametersUC.instance().should_download_in_parallel:
            global_df = self.LOOP.run_until_complete(self._parallel_process_tps(uc))
        else:
            global_df = self._sequential_process_tps(uc)

        try:
            global_df = global_df[["date"] + [x for x in global_df.columns if x != "date"]]
            global_df = global_df.sort_values(by="date")
        except KeyError:
            pass

        end = round(perf_counter() - start, 2)
        print(f"terminé en {end}s")

        return global_df

    async def _parallel_process_tps(self, uc: ScrapperUC):
        executor = ProcessPoolExecutor(max_workers=GeneralParametersUC.instance().cpus)
        futures = [self.LOOP.run_in_executor(executor, self._process_tp, tp)
                   for tp in uc.to_tps()]

        results = await asyncio.gather(*futures, return_exceptions=True)
        dfs = [x for x in results if isinstance(x, pd.DataFrame)]
        exceptions = [x for x in results if isinstance(x, ProcessException)]

        for ex in exceptions:
            self._errors[ex.key] = {"url": ex.url, "msg": ex.msg}

        try:
            global_df = pd.concat(dfs)
        except ValueError:
            global_df = pd.DataFrame()

        return global_df

    def _sequential_process_tps(self, uc: ScrapperUC):
        global_df = pd.DataFrame()
        for tp in uc.to_tps():
            try:
                local_df = self._process_tp(tp)
                global_df = pd.concat([global_df, local_df])
            except ProcessException as pe:
                self._errors[pe.key] = {"url": pe.url, "msg": pe.msg}
                continue

        return global_df

    def _process_tp(self, tp: TaskParameters):
        print(tp.url)
        try:
            html_data = self._load_html(tp)
            col_names = self._scrap_columns_names(html_data)
            values = self._scrap_columns_values(html_data)
            df_tp = self._rework_data(values, col_names, tp)
            df_tp = self._add_missing_rows(df_tp, tp)
        except Exception as ex:
            raise ProcessException(key=tp.key, url=tp.url, msg=str(ex))

        return df_tp

    @staticmethod
    def _load_html(tp: TaskParameters) -> Element:
        """Charge une page html à scrapper et renvoie la table de données trouvée."""
        html_loading_trials = 3
        html_page = None
        with HTMLSession() as session:
            while html_page is None and html_loading_trials > 0:

                if html_loading_trials < 3:
                    print("retrying...")

                try:
                    html_page = session.get(tp.url)
                    html_page.html.render(sleep=tp.waiting,  # .html n'est pas trouvé mais est essentiel
                                          keep_page=True,
                                          scrolldown=1)
                    if html_page.status_code != 200:
                        html_page = None
                except Exception:
                    html_loading_trials -= 1
                    html_page = None
                    tp.update_waiting()

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
        # (1) On initialise un DataFrame totalement vide, des dimensions attendues,
        #     avec les mêmes colonnes que df.
        # (2) On place la date de chacun des dfs en indexe et on retire de missings tous les indexes de df.
        #     Il ne reste que les lignes manquantes.
        #     On ignore le 29 février car il n'est pas anticipé dans _expected_dates et causerait une KeyError.
        # (3) On ajoute ces lignes aux résultats et on remet la date en colonne.

        # (1)
        expected_dates = self._expected_dates(tp)
        missings = pd.DataFrame(np.full((len(expected_dates), df.shape[1]), np.NaN),
                                columns=df.columns)
        missings["date"] = pd.to_datetime(expected_dates)
        # (2)
        df = df.set_index("date")
        missings = missings.set_index("date")
        missings = missings.drop(df[df.index != f"{tp.year}-02-29"].index, axis="rows")
        # (3)
        df = pd.concat([df, missings])
        df = df.reset_index()

        return df

    @abstractmethod
    def _expected_dates(self, tp: TaskParameters) -> List[str]:
        """Renvoie la liste des dates attendues pour le tp courant dans le dataframe,
        pour l'ajout des lignes manquantes."""
        pass


class MeteocielDaily(MeteoScrapper):

    UNWANTED_COLUMNS = ["to_delete", "phenomenes"]
    REGEX_FOR_NUMERICS = r'-?\d+\.?\d*'
    UNITS = {"temperature": "°C",
             "precipitations": "mm",
             "ensoleillement": "h",
             "vent": "km/h",
             "rafales": "km/h",
             "pression": "hPa"}

    def _scrap_columns_names(self, table):
        #   (1) On récupère les noms des colonnes contenus dans la 1ère ligne du tableau.
        #   (2) Certains caractères à accents passent mal (précipitations, phénomènes).
        #     On les remplace, on enlève les "." et on remplace les espaces par des _.
        #   (3) On renomme la colonne jour en date, et la dernière colonne qui n'a pas de nom en to_delete.
        #   (4) On ajoute au nom de la colonne son unité.

        # (1)
        columns_names = [td.text.lower().strip() for td in table.find("tr")[0].find("td")]
        if len(columns_names) == 0:
            raise ScrapException()
        # (2)
        columns_names = [col.replace("ã©", "e")
                            .replace("ã¨", "e")
                            .replace(".", "")
                            .replace(" ", "_")
                            .replace("temp_", "temperature_")
                            .replace("prec_", "precipitations_")
                         for col in columns_names]
        # (3)
        index = columns_names.index("jour")
        columns_names[index] = "date"

        try:
            index = columns_names.index("")
            columns_names[index] = "to_delete"
        except ValueError:
            pass
        # (4)
        cols_units = [col.split('_')[0] for col in columns_names]
        cols_units = ["" if colunit not in self.UNITS.keys()
                      else self.UNITS[colunit]
                      for colunit in cols_units]

        columns_names = [colname if not colunit
                         else f"{colname}_{colunit}"
                         for colname, colunit in zip(columns_names,
                                                     cols_units)]
        return columns_names

    def _scrap_columns_values(self, table):
        # On récupère les valeurs des cellules de toutes les lignes,
        # sauf la 1ère (noms des colonnes) et la dernière (cumul / moyenne mensuel).
        values = [td.text.strip()
                  for tr in table.find("tr")[1:-1]
                  for td in tr.find("td")]
        return values

    def _rework_data(self, values, columns_names, tp):
        #   (1) On créé le tableau de données.
        #   (2) Suppression des colonnes inutiles. On passe par une compréhension pour éviter les KeyError.
        #   (3) Le tableau ne contient que des string composées d'une valeur et d'une unité.
        #       La fonction lambda renvoie la valeur trouvée dans une string, convertie en float si elle existe, ou nan.
        #       On définit aussi une fonction lambda vectorisée qui met la date en forme.
        #   (4) On reconstruit les dates à partir des numéros des jours extraits de la colonne des dates.
        #       On extrait les valeurs des autres colonnes.

        # (1)
        df = pd.DataFrame(np.array(values)
                            .reshape(-1, len(columns_names)),
                          columns=columns_names)
        # (2)
        df = df[[x for x in df.columns if x not in self.UNWANTED_COLUMNS]]
        # (3)
        f_num_extract = np.vectorize(self._extract_numeric_value)
        f_rework_dates = np.vectorize(lambda day: f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(int(day))}")

        # (4)
        df["date"] = f_num_extract(df["date"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])
        df.iloc[:, 1:] = f_num_extract(df.iloc[:, 1:])

        return df

    def _extract_numeric_value(self, str_value: str):
        if str_value in ("---", ""):
            return np.NaN
        elif "aucune" in str_value or "trace" in str_value:
            return 0
        else:
            return float(re.findall(self.REGEX_FOR_NUMERICS, str_value)[0])

    def _expected_dates(self, tp):
        return [f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(x)}"
                for x in range(1, MonthEnum.from_id(tp.month).ndays + 1)]


class MeteocielHourly(MeteoScrapper):

    UNWANTED_COLUMNS = ["temps", "vent_rafales"]
    NOT_NUMERIC = ["date", "neb"]
    REGEX_FOR_NUMERICS = r'-?\d+\.?\d*'
    UNITS = {"visi": "km",
             "temperature": "°C",
             "point_de_rosee": "°C",
             "humi": "%",
             "direction_du_vent": "°",
             "vent": "km/h",
             "rafales": "km/h",
             "pression": "hPa",
             "precip": "mm"}

    def _scrap_columns_names(self, table):
        #   (1) Certains noms sont sur 2 lignes, on peut se passer de la 2ème.
        #   (2) Certains caractères à accents passent mal, on les remplace par leur version sans accent.
        #   (3) La colonne vent est composée de 2 sous colonnes: direction et vitesse.
        #       Le tableau compte donc n colonnes mais n-1 noms de colonnes.
        #       On rajoute donc un nom pour la colonne de la direction du vent.
        columns_names = [td.text for td in table.find("tr")[0].find("td")]
        if len(columns_names) == 0:
            raise ScrapException()
        # (1)
        columns_names = [col.split("\n")[0] if "\n" in col else col for col in columns_names]
        # (2)
        columns_names = [col.lower()
                            .replace("ã©", "e")
                            .replace("ã¨", "e")
                            .replace(".", "")
                            .replace(" ", "_")
                            .replace("(", "")
                            .replace(")", "")
                         for col in columns_names]
        index = columns_names.index("heure")
        columns_names[index] = "date"
        # (3)
        try:
            indexe = columns_names.index("vent_rafales")
            columns_names.insert(indexe, "direction_du_vent")
        except ValueError:
            pass

        return columns_names

    def _scrap_columns_values(self, table):
        # (1)   On enlève la 1ère ligne car elle contient le nom des colonnes
        # (2)   On va récupérer la direction du vent en degré contenue dans les pop-up au survol de l'image
        # (2.1) On récupère le numéro de la colonne de la direction du vent.
        #       Comme il y a 1 colonne de plus que de noms de colonnes, la direction du vent correspond à l'indexe de vent (rafales)
        #
        # (2.2) On récupère le html des images des directions du vent en html, qui contient toutes les infos des pop-up.
        #
        # (2.3) La valeur à récupérer est facile à retrouver en splittant sur ";(",
        #       et en récupérant les 3 premiers caractères du 2ème membre.
        #       On isole ainsi soit un nombre à 3 chiffres, soit un nombre à 2 chiffres + 1 caractère indésirable.
        #       Certaines icônes contiennent le mot "variable" à la place de la valeur en degré, on aura "" comme valeur finale.
        #
        # (2.4) On convertit les str récupérées en valeur numérique, on élimine ainsi les potentiels caractères indésirables,
        #       puis on remet la valeur numérique en str, car à ce stade du processus de scrapping, on ne doit travailler qu'avec des str.
        #
        # (2.5) On a récupéré les directions du vent dans une liste à part de la liste principale des valeurs.
        #       Les directions du vent dans la liste principale sont des str vides.
        #       On calcule donc l'indexe des directions du vent dans la liste principale, et on les remplace par les nouvelles.

        # (1)
        values = [td.text
                  for tr in table.find("tr")[1:]
                  for td in tr.find("td")]
        # (2)
        try:
            # (2.1)
            columns_names = [td.text.lower() for td in table.find("tr")[0].find("td")]
            columns_size = len(columns_names) + 1
            wind_dir_indexe = columns_names.index("vent (rafales)")
            # (2.2)
            wind_dir_cells = [img.html
                              for img in table.find("img")
                              if "Vent moyen :" in img.html]
            # (2.3)
            wind_dir_cells = [string.split(";(")
                              for string in wind_dir_cells]

            wind_dir_cells = ["" if len(str_list) < 2 else str_list[1][:3]
                              for str_list in wind_dir_cells]
            # (2.4)
            wind_dir_cells = [self._extract_numeric_value(str_value)
                              for str_value in wind_dir_cells]

            wind_dir_cells = ["" if x is np.nan else str(x) for x in wind_dir_cells]
            # (2.5)
            indexe_value_map = {columns_size * idx + wind_dir_indexe : val
                                for idx, val in enumerate(wind_dir_cells)}

            for key, val in indexe_value_map.items():
                values[key] = val
        except ValueError:
            pass

        return values

    def _rework_data(self, values, columns_names, tp):
        #   (1) On créé le tableau.
        #   (2) On sépare la colonne vent_rafales en 2
        #       Les valeurs contenues dans "vent (rafales)" sont normalement de la forme :
        #         - x km/h (y km/h)
        #         - x km/h
        #       On splite selon la ( pour avoir les 2 valeurs dans 2 str différentes.
        #       Si le split rend une liste d'1 seule valeur, on met une str vide dans les rafales.
        #       Puis on supprime les colonnes inutiles.
        #   (3) On définit 2 fonctions vectorisées qui serviront à extraire les données numérique et formater les dates.
        #   (4) On convertit les valeurs du format string vers le format qui leur vont.
        #   (5) On ajoute au nom de la colonne son unité.

        # (1)
        df = pd.DataFrame(np.array(values)
                            .reshape(-1, len(columns_names)),
                          columns=columns_names)
        # (2)
        try:
            splitted = df["vent_rafales"].str.split("(")
            idx_vent = list(df.columns).index("vent_rafales")
            df.insert(loc=idx_vent + 1,
                      column="vent",
                      value=[x[0] for x in splitted])
            df.insert(loc=idx_vent + 2,
                      column="rafales",
                      value=["" if len(x) == 1 else x[1] for x in splitted])
            del splitted, idx_vent
        except KeyError:
            pass
        df = df[[col
                 for col in df.columns
                 if col not in self.UNWANTED_COLUMNS]]
        # (3)
        f_num_extract = np.vectorize(self._extract_numeric_value)
        f_rework_dates = np.vectorize(lambda heure: f"{tp.year_as_str}-{tp.month_as_str}-{tp.day_as_str} {MonthEnum.format_date_time(int(heure))}:00:00")

        # (4)
        numerics = [x for x in df.columns if x not in self.NOT_NUMERIC]
        df["date"] = f_num_extract(df["date"])
        df["date"] = f_rework_dates(df["date"])
        df["date"] = pd.to_datetime(df["date"])
        df[numerics] = f_num_extract(df[numerics])

        # (5)
        df.columns = [f"{col}_{self.UNITS[col]}"
                      if col in self.UNITS.keys()
                      else col
                      for col in df.columns]
        return df

    def _extract_numeric_value(self, str_value: str):
        if str_value in ("---", ""):
            return np.NaN
        elif "aucune" in str_value or "traces" in str_value:
            return 0
        else:
            return float(re.findall(self.REGEX_FOR_NUMERICS, str_value)[0])

    def _expected_dates(self, tp):
        return [f"{tp.year_as_str}-{tp.month_as_str}-{tp.day_as_str} {MonthEnum.format_date_time(x)}:00:00"
                for x in range(0, 24)]


class OgimetDaily(MeteoScrapper):
    TEMP_SUBS = ["max", "min", "avg", "max.", "min.", "mvg."]
    WIND_SUBS = ["dir.", "int.", "gust.", "dir", "int", "gust"]
    NOT_NUMERIC = ["date", "wind_km/h_dir"]

    def _scrap_columns_names(self, table):
        #   (1) On récupère les 2 tr du thead de la table de données sur ogimet dans trs.
        #       Le 1er contient les noms principaux des colonnes, le 2ème des compléments.
        #       Max 3 des compléments sont pour la température, max 3 autres pour le vent.
        #   (2) On ajoute chaque nom principal à la liste des noms de colonnes, en lui associant
        #       son complément s'il y a lieu.
        #   (3) On formate les noms et les unités correctement.
        #   (4) La colonne daily_weather_summary compte pour 8, on n'a qu'1 nom sur les 8.
        #       On en rajoute 7.

        # (1)
        trs = table.find("thead")[0].find("tr")
        main_names = [th.text.strip().lower() for th in trs[0].find("th")]
        all_subs = [th.text.strip().lower() for th in trs[1].find("th")]
        actual_temp_subs = [x for x in all_subs if x in self.TEMP_SUBS]
        actual_wind_subs = [x for x in all_subs if x in self.WIND_SUBS]
        columns_names = []

        if len(trs) == 0 or len(main_names) == 0:
            raise ScrapException()

        # (2)
        for main_name in main_names:
            if "temperature" in main_name:
                to_add = [f"{main_name}_{sub}" for sub in actual_temp_subs]
            elif "wind" in main_name:
                to_add = [f"{main_name}_{sub}" for sub in actual_wind_subs]
            else:
                to_add = [main_name]

            columns_names.extend(to_add)
        # (3)
        columns_names = [x.replace("\n", "_")
                          .replace(" ", "_")
                          .replace("(c)", "(°C)")
                          .replace(".", "")
                          .replace("(", "")
                          .replace(")", "")
                         for x in columns_names]
        # (4)
        if "daily_weather_summary" in columns_names:
            columns_names += [f"daily_weather_summary_{i}" for i in range(7)]

        return columns_names

    def _scrap_columns_values(self, table):
        return [td.text for td in table.find("tbody")[0].find("td")]

    @staticmethod
    def _fill_partial_rows(values: "List[str]",
                           n_cols: int,
                           tp: TaskParameters):
        """Complète les lignes auxquelles il manque des valeurs avec des str vides."""
        #   Ogimet gère mal les données manquantes.
        #   Si certaines valeurs manquent en début ou milieu de ligne,
        #   elle sont comblées par "---", et tout va bien, on a des valeurs quand même.
        #
        #   Si les valeurs manquantes sont à la fin, la ligne s'arrête prématurément.
        #   Elle compte moins de valeurs qu'attendu, on ne peut pas reconstruire le tableau.
        #       => https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=08180&ano=2017&mes=7&day=31&hora=23&ndays=31
        #
        #   (1) values contient des lignes incomplètes si sa taille n'est pas un multiple de n_cols.
        #     Si toutes les lignes sont complètes, on a rien à faire.
        #   (2) A chaque tour de boucle, on trouve l'indexe des 2 prochaines dates.
        #   (3) On sélectionne les valeurs entre la 1ère date incluse et la 2ème exclue dans row.
        #       On retire ces valeurs de values.
        #   (4) On complète row avec autant de str que nécessaire pour avoir n_cols valeurs dedans,
        #       et on l'ajoute aux valeurs traitées.

        # (1)
        if len(values) % n_cols == 0:
            return values

        done = []
        while len(values) > 0:
            # (2)
            remaining_dates = [x for x in values if f"{tp.month_as_str}/" in x]
            first_index = values.index(remaining_dates[0])
            second_index = -1 if len(remaining_dates) == 1 else values.index(remaining_dates[1])
            # (3)
            if second_index == -1:
                row = values[first_index:]
                values = []
            else:
                row = values[first_index:second_index]
                values = values[second_index:]
            # (4)
            actual_row_length = len(row)
            row.extend([""] * (n_cols - actual_row_length))
            done.extend(row)

        return done

    def _rework_data(self, values, columns_names, tp):
        #   (1) Création du dataframe.
        #   (2) La colonne date est au format MM/JJ, on la convertit au format AAAA-MM-JJ.
        #   (3) Les valeurs sont au format str, on les convertit en numérique colonne par colonne.
        #   (4) La colonne wind_(km/h)_dir contient des str, on remplace les "---" par "" pour les
        #       valeurs manquantes.
        #   (5) On supprime les colonnes daily_weather_summary si elles existent en conservant les
        #       colonnes qui n'ont pas daily_weather_summary dans leur nom.

        # (1)
        n_cols = len(columns_names)
        values = self._fill_partial_rows(values, n_cols, tp)
        df = pd.DataFrame(np.array(values)
                            .reshape(-1, n_cols),
                          columns=columns_names)
        # (2)
        df["date"] = tp.year_as_str + "/" + df["date"]
        df["date"] = pd.to_datetime(df["date"])
        # (3)
        numeric_cols = [col
                        for col in df.columns
                        if col not in self.NOT_NUMERIC]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        # (4)
        try:
            col = "wind_km/h_dir"
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
    UNWANTED_COLUMNS = ["ww", "w1", "w2", "time"]
    NOT_NUMERIC = ["date", "ddd", "prec_mm"]

    def _scrap_columns_names(self, table):
        # La colonne date est subdivisée en 2, une colonne date et une colonne time.
        # On ajoute la colonne time.
        col_names = [th.text for th in table.find("tr")[0]
                                            .find("th")]
        if len(col_names) == 0:
            raise ScrapException()

        col_names = [colname.lower()
                            .replace("\n", "_")
                            .replace("(c)", "°C")
                            .replace("(mm)", "mm")
                            .replace("(cm)", "cm")
                            .replace("kmh", "km/h")
                            .replace("_hpa", "_hPa")
                            .replace(" ", "_")
                     for colname in col_names]

        specific_index = col_names.index("date")
        col_names.insert(specific_index + 1, "time")

        return col_names

    def _scrap_columns_values(self, table):
        # On supprime la 1ère ligne (noms des colonnes) et la dernière (data du jour précédent le 1er demandé).
        return [td.text
                for tr in table.find("tr")[1:-1]
                for td in tr.find("td")]

    @staticmethod
    def _fill_partial_rows(values: "List[str]",
                           n_cols: int,
                           tp: TaskParameters):
        """Complète les lignes auxquelles il manque des valeurs avec des str vides."""
        #   Ogimet gère mal les données manquantes.
        #   Si certaines valeurs manquent en début ou milieu de ligne,
        #   elle sont comblées par "---", et tout va bien, on a des valeurs quand même.
        #
        #   Si les valeurs manquantes sont à la fin, la ligne s'arrête prématurément.
        #   Elle compte moins de valeurs qu'attendu, on ne peut pas reconstruire le tableau.
        #
        #   (1) values contient des lignes incomplètes si sa taille n'est pas un multiple de n_cols.
        #     Si toutes les lignes sont complètes, on a rien à faire.
        #   (2) A chaque tour de boucle, on trouve l'indexe des 2 prochaines dates.
        #   (3) On sélectionne les valeurs entre la 1ère date incluse et la 2ème exclue dans row.
        #       On retire ces valeurs de values.
        #   (4) On complète row avec autant de str que nécessaire pour avoir n_cols valeurs dedans,
        #       et on l'ajoute aux valeurs traitées.

        # (1)
        if len(values) % n_cols == 0:
            return values

        done = []
        while len(values) > 0:
            # (2)
            remaining_dates = [MonthEnum.format_date_time(tp.day - x) for x in range(0, tp.ndays)]
            remaining_dates = [f"{tp.month_as_str}/{x}/{tp.year_as_str}" for x in remaining_dates]
            remaining_dates = [x for x in values if x in remaining_dates]

            first_index = values.index(remaining_dates[0])
            remaining_dates = remaining_dates[first_index + 1:]
            second_index = -1 if len(remaining_dates) == 1 else values[first_index + 1:].index(remaining_dates[1]) + first_index + 1
            # (3)
            if second_index == -1:
                row = values[first_index:]
                values = []
            else:
                row = values[first_index:second_index]
                values = values[second_index:]
            # (4)
            actual_row_length = len(row)
            row.extend([""] * (n_cols - actual_row_length))
            done.extend(row)

        return done

    def _rework_data(self, values, columns_names, tp):
        #   (1) On créé le dataframe.
        #   (2) La date est divisée en 2 colonnes date et heure, on les rassemble, et on formate correctement.
        #   (3) On retire les colonnes qui ne nous intéressent pas.
        #   (4) Le format des précipitations est bizarre, on choisit de le laisser sous forme de str.
        #       Parfois la cellule contient 2 données, séparée par un retour à la ligne, on les met bout à bout.
        #       => https://www.ogimet.com/cgi-bin/gsynres?ind=07149&ndays=28&ano=2020&mes=2&day=28&hora=23&lang=en&decoded=yes
        #   (5) On convertit les données au format numérique.

        # (1)
        n_cols = len(columns_names)
        values = self._fill_partial_rows(values, n_cols, tp)
        df = pd.DataFrame(np.array(values)
                            .reshape(-1, n_cols),
                          columns=columns_names)
        # (2)
        df["date"] = df["date"] + ":" + df["time"]
        df["date"] = pd.to_datetime(df["date"],
                                    format="%m/%d/%Y:%H:%M")
        # (3)
        df = df[[x for x in df.columns if x not in self.UNWANTED_COLUMNS]]
        # (4)
        try:
            df["prec_mm"] = ["" if "--" in x
                             else "_".join(x.split("\n"))
                             for x in df["prec_mm"].values]
        except KeyError:
            pass
        # (5)
        numeric_columns = [x for x in df.columns if x not in self.NOT_NUMERIC]
        for numeric_column in numeric_columns:
            df[numeric_column] = pd.to_numeric(df[numeric_column],
                                               errors="coerce")
        return df

    def _expected_dates(self, tp):
        days = [f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(tp.day - x)}"
                for x in range(0, tp.ndays)]

        hours = [MonthEnum.format_date_time(x) for x in range(0, 24)]

        return [f"{day} {hour}:00:00" for day in days for hour in hours]


class WundergroundDaily(MeteoScrapper):

    SUB_NAMES = ["max", "avg", "min", "total"]
    UNITS_CONVERSION = {"dew": (lambda x: (x - 32) * 5/9),
                        "wind": (lambda x: x * 1.609344),
                        "pressure": (lambda x: x * 33.86388),
                        "humidity": (lambda x: x),
                        "temperature": (lambda x: (x - 32) * 5/9),
                        "precipitation": (lambda x: x * 25.4)}

    def _scrap_columns_names(self, table):
        columns_names = [td.text for td in table.find("thead")[0].find("td")]

        if len(columns_names) == 0:
            raise ScrapException()

        columns_names = [x.lower()
                          .strip()
                          .replace(" ", "_")
                          .replace("_(°f)", "_°C")
                          .replace("_(%)", "_%")
                          .replace("_(mph)", "_km/h")
                         for x in columns_names]

        index = columns_names.index("time")
        columns_names[index] = "date"

        try:
            index = columns_names.index("pressure_(in)")
            columns_names[index] = "pressure_hPa"
        except ValueError:
            pass

        try:
            index = columns_names.index("precipitation_(in)")
            columns_names[index] = "precipitation_mm"
        except ValueError:
            pass

        return columns_names

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
        return [td.text
                for td in table.find("tbody")[0]
                               .find("td")
                if "\n" in td.text]

    def _rework_data(self, values, columns_names, tp):
        #   (1) values est une liste de str. Chaque str contient toutes les données d'1 colonne principale
        #       séparées par des \n ("x\nx\nx\nx..."). On convertit ces str en liste de données [x,x,x, ...].
        #       values devient une liste de listes.
        #       On définit aussi le nombre de ligne comme étant égal à la longueur de la 1ère liste de values,
        #       qui correspond à la colonne Time.
        #   (2) On initialise la matrice qui constituera le dataframe final avec la 1ère liste (Time)
        #       transformée en vecteur colonne.
        #   (3) Le dataframe aura besoin de noms pour ses colonnes. Le nom final est composé d'un nom
        #       principal et d'un complément, sauf pour la colonne Time.
        #       Les noms principaux sont contenus dans main_names, les compléments correspondent aux 1 ou 3
        #       premières valeurs des listes dans values. Pour chaque liste, on récupère les compléments.
        #       On transforme la liste courante en vecteur colonne ou en matrice à 3 colonnes,
        #       puis on accolle ces colonnes au dataframe principal.
        #   (4) On associe les main_names avec leurs sub_names.
        #   (5) On créé le dataframe final à partir de la matrice et des noms de colonnes. La 1ère ligne,
        #       contenant les compléments, est supprimée.
        #   (6) On formate les dates correctement, au format AAAA-MM-JJ.
        #   (7) Jusqu'ici les valeur du dataframe sont au format str. On les convertit en numérique.
        #   (8) On convertit vers les unités classiques .

        # (1)
        values = [string.split("\n") for string in values]
        # (2)
        df = np.array(values[0])\
               .reshape(-1, 1)
        # (3)
        all_sub_names = [[""]]
        for current_column_values in values[1:]:
            current_column_sub_names = [x.strip().lower()
                                        for x in current_column_values
                                        if x.strip().lower() in self.SUB_NAMES]
            all_sub_names.append(current_column_sub_names)
            current_column_values = np.array(current_column_values)\
                                      .reshape(-1, len(current_column_sub_names))
            df = np.hstack((df, current_column_values))
        # (4)
        columns_names = ["_".join([main, sub]) if sub
                         else main
                         for main, subs in zip(columns_names, all_sub_names)
                         for sub in subs]
        # (5)
        df = pd.DataFrame(df, columns=columns_names)
        df = df.drop([0], axis="index")

        # (6)
        df["date"] = [f"{tp.year_as_str}/{tp.month_as_str}/{MonthEnum.format_date_time(int(day))}"
                      for day in df.date]

        df["date"] = pd.to_datetime(df["date"])

        # (7)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col])
        # (8)
        for variable, convertor in self.UNITS_CONVERSION.items():
            cols_to_convert = [col for col in df.columns if variable in col]
            df[cols_to_convert] = np.round(convertor(df[cols_to_convert]), 1)

        return df

    def _expected_dates(self, tp):
        return [f"{tp.year_as_str}-{tp.month_as_str}-{MonthEnum.format_date_time(x)}"
                for x in range(1, MonthEnum.from_id(tp.month).ndays + 1)]
