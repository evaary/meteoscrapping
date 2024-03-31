from unittest import TestCase

import numpy as np
import pandas as pd

from app.scrappers_module import WundergroundDaily
from app.UserConfigFile import UserConfigFile


class WundergroundDailyTester(TestCase):

    SCRAPPER = WundergroundDaily()
    UCF_PATH = "./app/tests/ucfs/wunderground_daily.json"
    URL_REF = "https://www.wunderground.com/history/monthly/it/matera/LIBD/date/2021-1"

    RESULTATS = pd.DataFrame(
        [["2021-01-01", 14,  7.9,  3,  6,  3.5,  1,  93, 75.5, 48, 19, 12.3, 4, 1010.9, 1009.9, 1008.9, 0.00],
         ["2021-01-02", 15, 10.4,  4, 10,  7.3,  3,  93, 81.7, 67, 41, 17.3, 2, 1008.9, 1007.3, 1005.9, 0.00],
         ["2021-01-03", 14,  8.3,  4,  7,  4.4,  2,  93, 77.8, 55, 48, 12.1, 2, 1008.9, 1008.1, 1006.9, 0.00],
         ["2021-01-04", 13,  8.0,  5,  6,  3.5,  2,  87, 73.8, 54, 19,  9.4, 2, 1007.9, 1006.2, 1003.9, 0.00],
         ["2021-01-05", 14,  8.3,  3,  7,  3.2,  1,  87, 71.9, 51, 22, 11.7, 6, 1008.9, 1007.9, 1006.9, 0.00],
         ["2021-01-06", 15, 10.7,  8,  8,  5.5,  2,  93, 71.4, 48, 24, 10.5, 2, 1010.9, 1009.2, 1007.9, 0.00],
         ["2021-01-07", 11,  9.6,  8, 10,  7.9,  5, 100, 89.8, 76, 11,  5.7, 2, 1010.9, 1009.0, 1004.9, 0.00],
         ["2021-01-08", 10,  8.4,  7, 10,  7.4,  5, 100, 93.5, 82, 17, 12.3, 6, 1007.9, 1005.1, 1003.0, 0.00],
         ["2021-01-09", 10,  7.8,  7,  8,  6.5,  5, 100, 91.7, 81, 17,  9.3, 4, 1010.9, 1009.2, 1007.9, 0.00],
         ["2021-01-10",  9,  7.7,  7,  8,  7.4,  7, 100, 97.8, 93, 19,  8.8, 2, 1009.9, 1006.9, 1002.0, 0.00],
         ["2021-01-11",  9,  7.5,  6,  6,  4.8,  4,  93, 83.6, 71, 19, 11.9, 6, 1010.9, 1009.1, 1004.9, 0.00],
         ["2021-01-12",  9,  7.0,  4,  6,  4.1,  2,  87, 81.6, 76, 19, 13.5, 7, 1009.9, 1008.6, 1007.9, 0.00],
         ["2021-01-13", 11,  7.5,  3,  4,  2.5,  1,  93, 72.4, 50, 24, 11.5, 6, 1010.9, 1008.4, 1006.9, 0.00],
         ["2021-01-14", 16,  9.5,  3,  8,  4.0, -1,  93, 70.3, 48, 28, 13.4, 6, 1010.9, 1006.3, 1002.0, 0.00],
         ["2021-01-15", 10,  7.2,  4,  3,  0.1, -2,  93, 62.8, 46, 15,  9.3, 4, 1009.9, 1009.2, 1007.9, 0.00],
         ["2021-01-16",  7,  6.2,  4,  1, -3.3, -6,  81, 51.7, 42, 24, 18.2, 9, 1014.9, 1012.3, 1009.9, 0.00],
         ["2021-01-17",  7,  4.5,  1,  1, -2.9, -6,  93, 60.7, 42, 19, 10.7, 4, 1013.9, 1011.9, 1009.9, 0.00],
         ["2021-01-18",  7,  4.8,  2,  3, -0.6, -4,  93, 69.8, 49, 19, 12.1, 4, 1020.9, 1016.5, 1010.9, 0.00],
         ["2021-01-19", 11,  6.0,  3,  3,  1.6,  0,  93, 75.2, 47, 19, 10.8, 2, 1022.9, 1021.7, 1020.9, 0.00],
         ["2021-01-20", 15,  9.5,  4,  7,  4.0,  1,  93, 69.7, 48, 17, 13.3, 7, 1021.9, 1020.1, 1017.9, 0.00],
         ["2021-01-21", 17, 11.0,  7,  6,  4.7,  3,  82, 66.8, 45, 24, 14.0, 6, 1017.9, 1016.0, 1013.9, 0.00],
         ["2021-01-22", 17, 13.7, 10, 16,  6.6,  5,  82, 61.1, 	0, 30, 14.3, 4, 1013.9, 1009.4, 1004.9, 0.00],
         ["2021-01-23", 14, 11.5,  5,  9,  5.4,  3,  94, 66.9, 54, 31, 16.4, 4, 1003.0, 1000.5,  999.0, 0.00],
         ["2021-01-24", 15, 11.0,  6,  8,  5.7,  3,  87, 70.3, 55, 30, 16.8, 6, 1001.0,  996.0,	 990.0, 0.00],
         ["2021-01-25", 14, 10.1,  3,  8,  3.7, -1,  87, 66.3, 41, 35, 18.2, 7, 1003.0, 1000.2,  997.0, 0.00],
         ["2021-01-26", 10,  7.6,  6,  8,  1.6, -4,  93, 68.2, 43, 35, 21.5, 7, 1009.9, 1005.0, 1001.0, 0.00],
         ["2021-01-27",  9,  6.0,  4,  2, -0.3, -5,  87, 65.5, 40, 28, 18.9, 9, 1011.9, 1011.4, 1009.9, 0.00],
         ["2021-01-28", 12,  6.6, -1,  2, -2.6, -8,  81, 55.6, 26, 19, 10.2, 4, 1012.9, 1010.9, 1007.9, 0.00],
         ["2021-01-29", 18, 11.6,  4,  9,  6.6,  2,  93, 72.7, 55, 35, 13.9, 4, 1007.9, 1002.9,  996.0, 0.00],
         ["2021-01-30", 17, 12.5,  6,  9,  6.3,  5,  93, 67.8, 45, 28, 10.5, 2, 1002.0,  999.8,	 997.0, 0.00],
         ["2021-01-31", 14, 11.3,  7, 11,  7.5,  4,  94, 78.4, 54, 28, 13.0, 2,  998.0,	 992.8,	 990.0, 0.00]],

        columns=[
            "date",
            "temperature_°C_max", "temperature_°C_avg", "temperature_°C_min",
            "dew_point_°C_max", "dew_point_°C_avg", "dew_point_°C_min",
            "humidity_(%)_max", "humidity_(%)_avg", "humidity_(%)_min",
            "wind_speed_(km/h)_max", "wind_speed_(km/h)_avg", "wind_speed_(km/h)_min",
            "pressure_(hPa)_max", "pressure_(hPa)_avg", "pressure_(hPa)_min",
            "precipitation_(mm)_total"
        ]
    )

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")

    def test_scrap_data(self):
        ucf = UserConfigFile.from_json(self.UCF_PATH)
        uc = ucf.wunderground_ucs[0]
        data = self.SCRAPPER.scrap_uc(uc).set_index("date")

        not_converted = ["humidity_(%)_max", "humidity_(%)_avg", "humidity_(%)_min"]
        converted = [col for col in data.columns if
                     col not in not_converted]

        converted = [col for col in converted if "°C" not in col]

        differences_converted = (data[converted] - self.RESULTATS[converted]) * 100 / self.RESULTATS[converted]
        differences_converted = np.round(differences_converted, 2)  # en % d'écart

        # on exclue les colonnes du vent car les écarts dûs à la conversion peuvent être importants
        differences_converted = differences_converted[[x
                                                       for x in list(differences_converted.columns)
                                                       if "wind" not in x]]

        differences_not_converted = data[not_converted] - self.RESULTATS[not_converted]

        self.assertLessEqual(differences_converted.max(numeric_only=True).max(), 0.5)
        self.assertEqual(differences_not_converted.sum().sum(), 0)
