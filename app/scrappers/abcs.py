import threading as mt
from abc import ABC
from multiprocessing import current_process
from time import perf_counter

import pandas as pd

from app.scrappers.exceptions import ProcessException
from app.scrappers.interfaces import Scrapper


class MeteoScrapper(ABC, Scrapper):

    PROGRESS_TIMER_INTERVAL = 10 # en secondes

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

    def _upate(self):

        self._done += 1
        self._progress = round(self._done / self._todo * 100, 0)
        self._speed = round(self._progress / perf_counter() - self._start, 0)



    def _print_progress(self) -> None:

        print(f"{self.__class__.__name__} ({current_process().pid}) - {self._progress}% - {round(perf_counter()  - self._start, 0)}s \n")

        if self.PROGRESS_TIMER_INTERVAL * self._speed * 2 < 100 - self._progress:
            timer = mt.Timer(self.PROGRESS_TIMER_INTERVAL, self._print_progress)
            timer.daemon = True
            timer.start()


    # override
    def scrap_from_config(self, config):

        self._todo = sum([ 1 for _ in self._build_parameters_generator(config) ])
        self._start = perf_counter()

        parameters_generator = self._build_parameters_generator(config)
        global_df = pd.DataFrame()

        self._print_progress()

        for parameters in parameters_generator:

            try:

                html_data = self._load_html(parameters)
                col_names = self._scrap_columns_names(html_data)
                values = self._scrap_columns_values(html_data)
                local_df = self._rework_data( values,
                                              col_names,
                                              parameters )
            except ProcessException as e:

                self.errors[parameters.key] = { "url": parameters.url,
                                                "error": str(e) }
                self._upate()
                continue

            global_df = pd.concat( [global_df, local_df] )
            self._upate()

        global_df.sort_values(by="date")

        self._print_progress()

        return global_df
