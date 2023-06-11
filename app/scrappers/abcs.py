from abc import ABC

import pandas as pd

from app.scrappers.exceptions import ProcessException
from app.scrappers.interfaces import Scrapper


class MeteoScrapper(ABC, Scrapper):

    def __init__(self):
        # dict des erreur de la forme { "date" : {"url": url, "error": message (str)}, ...}
        self.errors = dict()

    def scrap_from_config(self, config):

        parameters_generator = self._build_parameters_generator(config)

        global_df = pd.DataFrame()

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
                continue

            global_df = pd.concat( [global_df, local_df] )

        global_df.sort_values(by="date")

        return global_df
