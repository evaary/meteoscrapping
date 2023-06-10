import asyncio
import threading as mt
from abc import ABC
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import current_process
from time import perf_counter

import pandas as pd
from requests.exceptions import ConnectionError, RequestException
from requests_html import AsyncHTMLSession

import app.scrappers.exceptions as scrapex
from app.job_parameters import JobParameters
from app.scrappers.exceptions import (HtmlPageException, HtmlTableException,
                                      ReworkException, ScrapException)
from app.scrappers.interfaces import ConfigScrapperInterface, Scrapper


class MeteoScrapper(ABC, Scrapper):

    MAX_THREADS = 100
    # péridode d'affichage de l'avancement en s
    PROGRESS_TIMER_INTERVAL = 5

    def __init__(self):
        # dict des erreur de la forme { "date" : {"url": url, "error": message (str)}, ...}
        self.errors = dict()
        self._lock = mt.Lock()
        # date de départ de lancement des jobs
        self._start = None
        # quantité de jobs traités
        self._done = 0
        # quantité de jobs à traiter
        self._todo = -1
        # % de jobs traités
        self._progress = 0
        # vitesse en % / s
        self._speed = 0

    def _upate(self):
        self._done += 1
        self._progress = round(self._done / self._todo * 100, 0)
        self._speed = round(self._progress / (perf_counter() - self._start), 2)

    def _print_progress(self) -> None:

        print(f"{self.__class__.__name__} ({current_process().pid}) - {self._progress}% ({self._speed}%/s)\n")

        if self.PROGRESS_TIMER_INTERVAL * self._speed * 2 < 100 - self._progress:
            timer = mt.Timer(self.PROGRESS_TIMER_INTERVAL, self._print_progress)
            timer.daemon = True
            timer.start()

    def _process_html_data(self, html_data, parameters) -> pd.DataFrame:

        df = pd.DataFrame()

        if isinstance(html_data, Exception):
            with self._lock:
                self.errors[parameters["key"]] = {"url": parameters["url"], "error": scrapex.HtmlTableException.MESSAGE}
                self._upate()
            return df

        try:
            if "no valid" in html_data.find("thead")[0]\
                                      .find("th")[0]\
                                      .text\
                                      .lower()\
                                      .strip():
                with self._lock:
                    self.errors[parameters["key"]] = {"url": parameters["url"], "error": scrapex.HtmlTableException.MESSAGE}
                    self._upate()
                return df
        except IndexError:
            pass

        try:
            col_names = self._scrap_columns_names(html_data)
            values = self._scrap_columns_values(html_data)
        except (IndexError):
            with self._lock:
                self.errors[parameters["key"]] = {"url": parameters["url"], "error": scrapex.ScrapException.MESSAGE}
                self._upate()
                return df

        try:
            df = self._rework_data(values,
                                   col_names,
                                   parameters)
        except (IndexError):
            with self._lock:
                self.errors[parameters["key"]] = {"url": parameters["url"], "error": scrapex.ReworkException.MESSAGE}
                self._upate()
                return df

        with self._lock:
            self._upate()

        return df

    async def _load_html_async(self, session, parameters: dict):

        try:
            html_page = await session.get(parameters["url"])
            await html_page.html.arender()
        except (ConnectionError,
                RequestException):
            with self._lock:
                self.errors[parameters["key"]] = {"url": parameters["url"], "error": scrapex.HtmlPageException.MESSAGE}

        attr, val = parameters["criteria"]

        # (2)
        try:
            table = [
                tab for tab in html_page.html.find("table")
                if attr in tab.attrs and tab.attrs[attr] == val
            ][0]
        except IndexError:
            with self._lock:
                self.errors[parameters["key"]] = {"url": parameters["url"], "error": scrapex.HtmlTableException.MESSAGE}

        with self._lock:
            self._upate()

        return table

    async def _load_html_data(self, parameters) -> pd.DataFrame:

        results = []
        session = AsyncHTMLSession(workers=self.MAX_THREADS)

        tasks = [asyncio.create_task(self._load_html_async(session, parameter))
                 for parameter in parameters]

        for x in await asyncio.gather(*tasks, return_exceptions=True):
            results.append(x)

        await session.close()

        return results

    def scrap_from_config(self, config):

        # (1)
        self._todo = sum([1 for _ in self._build_parameters_generator(config)])

        parameters = self._build_parameters_generator(config)
        loop = asyncio.get_event_loop()
        dfs = []
        # (3)
        self._print_progress()
        self._start = perf_counter()

        html_data = loop.run_until_complete(self._load_html_data(parameters))
        print(html_data)
        parameters = self._build_parameters_generator(config)

        with ThreadPoolExecutor(max_workers=self.MAX_THREADS) as executor:
            results = executor.map(self._process_html_data, html_data, parameters)

        for df in results:
            dfs.append(df)

        data = pd.concat(dfs)\
                 .sort_values(by="date")

        self._print_progress()

        print(f"end = {perf_counter() - self._start}")

        return data
