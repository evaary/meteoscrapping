from unittest import TestCase
import pandas as pd
import numpy as np

from app.scrappers.meteociel_scrappers import MeteocielMonthly

class MeteocielTester(TestCase):

    SCRAPPER = MeteocielMonthly()

    CONFIG = { "code_num":"2", "code": "7249", "city":"orleans", "year":[2021], "month":[1], "waiting": 3 }

    # valeurs de référence pour janvier 2021
    URL_REF = "https://www.meteociel.com/climatologie/obs_villes.php?code2=7249&mois=1&annee=2021"

    KEY_REF = "orleans_2021_01"

    TODO = (2021, 1)

    RESULTATS = pd.DataFrame(
        [["2021-01-01", 2.1 , -3.6, 0.0 , 3.9],
         ["2021-01-02", 4.0 , -2.2, 0.2 , 6.0],
         ["2021-01-03", 3.2 ,  0.4, 2.0 , 0.0],
         ["2021-01-04", 2.3 ,  0.2, 0.4 , 0.0],
         ["2021-01-05", 2.3 ,  1.6, 0.0 , 0.0],
         ["2021-01-06", 3.1 ,  1.5, 0.0 , 0.0],
         ["2021-01-07", 3.9 , -0.3, 0.0 , 0.9],
         ["2021-01-08", -0.1, -4.2, 0.0 , 3.3],
         ["2021-01-09", 2.8 , -3.3, 0.0 , 2.6],
         ["2021-01-10", 3.9 , -1.3, 0.0 , 5.7],
         ["2021-01-11", 4.4 , -3.7, 0.0 , 2.0],
         ["2021-01-12", 9.2 ,  1.6, 4.4 , 0.0],
         ["2021-01-13", 10.2,  6.4, 1.8 , 0.0],
         ["2021-01-14", 10.5,  7.4, 0.4 , 0.3],
         ["2021-01-15", 3.2 ,  1.8, 0.0 , 0.6],
         ["2021-01-16", 4.7 , -3.8, 5.0 , 0.0],
         ["2021-01-17", 8.0 ,  1.6, 0.4 , 4.9],
         ["2021-01-18", 7.0 , -1.7, 0.0 , 1.6],
         ["2021-01-19", 8.3 ,  3.2, 0.0 , 7.1],
         ["2021-01-20", 12.8,  5.3, 2.4 , 2.6],
         ["2021-01-21", 10.6,  5.8, 26.6, 0.2],
         ["2021-01-22", 6.6 ,  2.4, 0.8 , 1.8],
         ["2021-01-23", 6.5 ,  1.9, 4.2 , 1.9],
         ["2021-01-24", 3.4 , -3.3, 2.6 , 0.2],
         ["2021-01-25", 5.1 , -0.4, 0.0 , 5.6],
         ["2021-01-26", 2.9 , -3.4, 1.6 , 1.2],
         ["2021-01-27", 10.7,  1.8, 2.6 , 0.0],
         ["2021-01-28", 13.8,  8.0, 4.0 , 0.4],
         ["2021-01-29", 12.7,  6.0, 4.6 , 2.2],
         ["2021-01-30", 12.4,  6.3, 0.4 , 1.6],
         ["2021-01-31", 11.0,  7.8, 6.4 , 0.6]],

        columns=[
            "date","temperature_max_°C","temperature_min_°C",
            "precipitations_24h_mm","ensoleillement_h"
        ]
    )

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")
        cls.SCRAPPER.update(cls.CONFIG)

    def test_key(self):
        test = self.SCRAPPER._build_key(self.TODO)
        self.assertEqual(self.KEY_REF, test)

    def test_url(self):
        test = self.SCRAPPER._build_url(self.TODO)
        self.assertEqual(self.URL_REF, test)

    def test_data(self):
        data = next(self.SCRAPPER._generate_data()).set_index("date")
        difference = (data - self.RESULTATS).sum().sum()
        self.assertTrue(difference == 0)
