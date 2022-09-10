from unittest import TestCase
import pandas as pd
import numpy as np

from app.scrappers.ogimet_scrapper import OgimetMonthly

class WundergroundTester(TestCase):

    SCRAPPER = OgimetMonthly()

    CONFIG = { "ind":"16138", "city":"Ferrara", "year":[2021], "month":[2], "waiting": 3 }

    # valeurs de référence pour janvier 2021
    URL_REF = "http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=16138&ano=2021&mes=3&day=0&hora=0&min=0&ndays=28"

    KEY_REF = "Ferrara_2021_02"

    TODO = (2021, 2)

    # liste des colonnes qui n'ont pas besoin d'être converties dans une nouvelle unité
    # NOT_CONVERTED

    # RESULTATS= pd.DataFrame([[]],
    #
    #     columns=[
    #         "date","temperature_°C_max","temperature_°C_avg","temperature_°C_min",
    #         "dew_point_°C_max","dew_point_°C_avg","dew_point_°C_min",
    #         "humidity_(%)_max","humidity_(%)_avg","humidity_(%)_min",
    #         "wind_speed_(km/h)_max","wind_speed_(km/h)_avg","wind_speed_(km/h)_min",
    #         "pressure_(hPa)_max","pressure_(hPa)_avg","pressure_(hPa)_min",
    #         "precipitation_(mm)_total"
    #     ]
    # )
