from unittest import TestCase

import numpy as np
import pandas as pd

from app.boite_a_bonheur.utils import to_csv
from app.scrappers.scrappers_module import (OgimetDaily,
                                            OgimetHourly)
from app.ucs.UserConfigFile import UserConfigFile


class OgimetDailyTester(TestCase):

    SCRAPPER = OgimetDaily()
    UCF_PATH = "./app/tests/ucfs/ogimet_daily.json"

    # valeurs de référence pour janvier 2021
    URL_REF = "http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=16138&ano=2021&mes=2&day=28&hora=23&ndays=28"

    RESULTATS = pd.DataFrame(
        [["2021-02-01",   7.6,  1.0,  4.5,  2.7,  83.9, "CAL",  0.0,  1000.0, np.NaN, 4.8,    4.2,   9.2],
         ["2021-02-02",  11.0,  1.4,  5.0,  4.0,  87.4,  "NW",  2.8,  1011.8, np.NaN, 2.8,    3.5,   4.7],
         ["2021-02-03",   7.6,  2.8,  5.3,  4.0,  87.7, "ENE",  4.1,  1014.7,    0.0, 7.8,    7.8,   1.7],
         ["2021-02-04",   8.3,  5.0,  6.5,  4.5,  86.1, "SSW",  2.2,  1017.4, np.NaN, 5.6,    6.5,   3.2],
         ["2021-02-05",   9.8,  4.6,  7.5,  5.6,  85.3, "ESE",  1.1,  1018.7,    0.0, 7.8,    7.8,   1.7],
         ["2021-02-06",   9.2,  7.4,  8.3,  6.5,  87.6, "CAL",  0.0,  1014.4, np.NaN, 8.0,    8.0,   2.0],
         ["2021-02-07",  10.0,  7.8,  9.0,  7.2,  86.8, "ENE",  1.5,   998.0, np.NaN, 8.0,    8.0,   1.2],
         ["2021-02-08",  13.2,  5.4,  7.9,  3.5,  71.7, "SSE",  3.7,   995.2, np.NaN, 2.2,    3.3,   8.2],
         ["2021-02-09",  11.0,  7.8,  8.8,  7.0,  86.8,   "W",  5.6,   999.2, np.NaN, 6.6,    5.8,   8.2],
         ["2021-02-10",  11.0,  7.0,  9.3,  7.9,  89.4,  "NE",  8.2,   997.7, np.NaN, 5.4,    3.6,  10.0],
         ["2021-02-11",  11.4,  3.8,  6.7,  4.5,  82.0, "ENE",  7.8,  1011.5, np.NaN, 1.8,    3.0,  10.4],
         ["2021-02-12",   5.0,  2.8,  3.6, -2.7,  62.5,  "NE", 14.8,  1024.1, np.NaN, 6.4,    6.4,  17.0],
         ["2021-02-13",   2.6,  1.4,  1.7, -10.0, 41.7,  "NE", 22.2,  1029.4, np.NaN, 2.4,    4.5,  30.0],
         ["2021-02-14",   7.4, -2.0,  1.8, -9.5,  44.8,  "NW",  8.2,  1037.6, np.NaN, 0.4, np.NaN,  16.0],
         ["2021-02-15",   9.0, -4.0,  2.6, -9.1,  42.4, "ESE",  1.9,  1038.0, np.NaN, 1.8,    3.5,  44.0],
         ["2021-02-16",  10.8, -0.2,  4.7, -0.7,  62.4, "NNW",  6.5,  1026.9, np.NaN, 1.8,    0.2,  16.0],
         ["2021-02-17",  11.0,  4.0,  6.6,  3.1,  75.7, "CAL",  0.0,  1022.0, np.NaN, 4.6,    7.7,  10.0],
         ["2021-02-18",  12.0,  4.8,  8.2,  3.7,  70.0,   "S",  3.1,  1023.5, np.NaN, 3.2,    4.0,   5.6],
         ["2021-02-19",  14.4,  5.8,  9.4,  5.6,  74.1,  "SW",  2.6,  1024.1, np.NaN, 4.2,    4.2,   5.6],
         ["2021-02-20",  15.0,  4.8,  8.7,  6.0,  78.9,  "NE",  2.5,  1025.9, np.NaN, 4.2,    4.2,   3.0],
         ["2021-02-21",  13.8,  5.4,  8.7,  5.8,  77.4, "ENE",  1.9,  1027.2, np.NaN, 4.6,    7.7,   5.0],
         ["2021-02-22",  12.0,  5.4,  8.7,  6.6,  84.6, "NNW",  3.0,  1031.4, np.NaN, 4.6,    7.7,   2.9],
         ["2021-02-23",  13.4,  2.8,  7.5,  5.3,  79.5, "NNW",  3.0,  1035.9, np.NaN, 0.0, np.NaN,   2.6],
         ["2021-02-24",  17.4,  2.8, 10.4,  3.2,  58.6,   "W",  7.8,  1034.7, np.NaN, 0.0, np.NaN,   8.2],
         ["2021-02-25",  18.6,  4.8, 10.6,  3.6,  59.7,   "W",  4.1,  1031.6, np.NaN, 0.0, np.NaN,  10.4],
         ["2021-02-26",  18.2,  3.2, 10.0,  3.3,  59.6,  "SW",  5.6,  1027.3, np.NaN, 0.0, np.NaN,   9.4],
         ["2021-02-27",  17.0,  3.2,  9.1,  5.7,  72.3,  "SE",  5.6,  1025.1, np.NaN, 3.0,    0.0,   5.2],
         ["2021-02-28",  13.0,  6.0,  8.9,  0.0,  52.4,  "NE",  8.5,  1032.5, np.NaN, 0.8,    2.0,  16.4]],

        columns=["date",
                 "temperature_(°C)_max", "temperature_(°C)_min", "temperature_(°C)_avg",
                 "td_avg_(°C)", "hr_avg_(%)",
                 "wind_(km/h)_dir", "wind_(km/h)_int",
                 "pres_slev_(hp)", "prec_(mm)",
                 "tot_cl_oct", "low_cl_oct",
                 "vis_km"]
    )

    NUMERICS = RESULTATS.columns.difference(["wind_(km/h)_dir", "date", "prec_(mm)"])

    @classmethod
    def compare_data(cls, data: pd.DataFrame) -> bool:
        return (data[cls.NUMERICS] - cls.RESULTATS[cls.NUMERICS]).sum().sum() == 0

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")

    def test_scrap_data(self):
        ucf = UserConfigFile.from_json(self.UCF_PATH)
        uc = ucf.get_ogimet_ucs()[0]
        data = self.SCRAPPER.scrap_from_uc(uc).set_index("date")
        self.assertTrue(self.compare_data(data))


class OgimetHourlyTester(TestCase):

    SCRAPPER = OgimetHourly()
    UCF_PATH = "./app/tests/ucfs/ogimet_hourly.json"

    URL_REF = "https://www.ogimet.com/cgi-bin/gsynres?ind=07149&lang=en&decoded=yes&ndays=1&ano=2023&mes=02&day=01&hora=00"

    RESULTATS = pd.DataFrame(
        [["02/01/2017 00:00:00", 10.1, 9.5, 96, np.NaN, np.NaN,  "S",  7.2, 14.4, 1004.2, 1015.1, -0.1,  "0.0/6h", 8,      7,    0.1, np.NaN,  1.0],
         ["02/01/2017 01:00:00",  9.8, 9.2, 96, np.NaN, np.NaN,  "S", 10.8, 14.4, 1003.7, 1014.6, -0.6,  "0.0/1h", 8,      7,    0.1, np.NaN,  2.3],
         ["02/01/2017 02:00:00",  9.6, 9.0, 96, np.NaN, np.NaN,  "S",  7.2, 14.4, 1003.4, 1014.3, -0.7,  "0.0/1h", 8,      7,    0.1, np.NaN,  2.7],
         ["02/01/2017 03:00:00",  9.6, 9.0, 96, np.NaN, np.NaN,  "S",  7.2, 14.4, 1003.0, 1013.9, -1.2,  "0.0/3h", 8,      8,    0.1, np.NaN,  5.0],
         ["02/01/2017 04:00:00",  9.4, 8.9, 97, np.NaN, np.NaN,  "S", 14.4, 21.6, 1002.8, 1013.7, -0.9,  "0.0/1h", 8,      8,    0.1, np.NaN,  0.5],
         ["02/01/2017 05:00:00",  9.1, 8.6, 97, np.NaN, np.NaN,  "S", 14.4, 21.6, 1002.5, 1013.4, -0.9,  "0.0/1h", 8,      8,    0.1, np.NaN,  1.0],
         ["02/01/2017 06:00:00",  8.7, 8.2, 97,   11.4,    8.7,  "S",  7.2, 18.0, 1002.4, 1013.3, -0.6, "0.2/24h", 8,      8,    0.1,    0.1,  2.6],
         ["02/01/2017 07:00:00",  8.5, 8.1, 97, np.NaN, np.NaN,  "S", 10.8, 18.0, 1002.3, 1013.2, -0.5,  "0.0/1h", 8,      8,    0.1, np.NaN,  1.8],
         ["02/01/2017 08:00:00",  8.3, 7.9, 97, np.NaN, np.NaN,  "S",  7.2, 14.4, 1002.3, 1013.2, -0.2,  "0.0/1h", 7,      7,    0.1, np.NaN,  4.8],
         ["02/01/2017 09:00:00",  9.5, 8.1, 91, np.NaN, np.NaN,  "S",  7.2, 14.4, 1002.1, 1013.0, -0.3,  "0.0/3h", 7,      7,    1.0, np.NaN, 15.0],
         ["02/01/2017 10:00:00", 11.2, 7.7, 79, np.NaN, np.NaN,  "S", 18.0, 28.8, 1001.7, 1012.5, -0.6,  "0.0/1h", 7,      5,    1.5, np.NaN, 28.0],
         ["02/01/2017 11:00:00", 11.3, 7.6, 78, np.NaN, np.NaN,  "S", 18.0, 28.8, 1001.4, 1012.2, -0.9,  "0.0/1h", 7,      1,    1.5, np.NaN, 20.0],
         ["02/01/2017 12:00:00", 11.7, 8.2, 79, np.NaN, np.NaN,  "S", 14.4, 28.8, 1001.2, 1012.0, -0.9,  "0.0/6h", 8,      3,    0.3, np.NaN, 27.0],
         ["02/01/2017 13:00:00", 11.8, 8.3, 79, np.NaN, np.NaN,  "S", 10.8, 32.4, 1000.4, 1011.2, -1.3,  "0.0/1h", 7,      1,    0.3, np.NaN, 28.0],
         ["02/01/2017 14:00:00", 12.2, 8.1, 76, np.NaN, np.NaN,  "S", 14.4, 25.2,  999.7, 1010.5, -1.7,  "0.0/1h", 7,      1,    0.3, np.NaN, 20.0],
         ["02/01/2017 15:00:00", 12.5, 8.2, 75, np.NaN, np.NaN,  "S", 18.0, 32.4,  999.8, 1010.6, -1.4,  "0.0/3h", 8,      5,    0.3, np.NaN, 20.0],
         ["02/01/2017 16:00:00", 11.9, 7.8, 76, np.NaN, np.NaN,"SSW", 14.4, 36.0,  999.8, 1010.6, -0.6,        "", 8,      7,    0.6, np.NaN, 20.0],
         ["02/01/2017 17:00:00", 11.3, 7.6, 78, np.NaN, np.NaN, "SW", 18.0, 36.0, 1000.1, 1010.9,  0.4,  "0.0/1h", 8,      7,    0.3, np.NaN, 20.0],
         ["02/01/2017 18:00:00", 10.9, 7.9, 82,   12.6,    8.1,"SSW", 18.0, 28.8, 1000.6, 1011.4,  0.8,  "0.0/1h", 8,      7,    0.3, np.NaN, 18.0],
         ["02/01/2017 19:00:00", 10.2, 7.6, 84, np.NaN, np.NaN,"SSW", 10.8, 25.2, 1000.4, 1011.3,  0.6,  "0.0/1h", 8,      7,    0.3, np.NaN, 11.0],
         ["02/01/2017 20:00:00",  9.6, 7.5, 87, np.NaN, np.NaN,  "S",  3.6, 14.4, 1000.2, 1011.1,  0.1,  "0.0/1h", 8,      8,    2.5, np.NaN, 10.0],
         ["02/01/2017 21:00:00",  9.1, 7.2, 88, np.NaN, np.NaN,  "S",  7.2, 10.8, 1000.1, 1011.0, -0.5,  "0.0/3h", 4,      1,    0.6, np.NaN,  9.0],
         ["02/01/2017 22:00:00",  8.9, 7.0, 88, np.NaN, np.NaN,  "S", 10.8, 18.0,  999.9, 1010.8, -0.5,  "0.0/1h", 3,      1,    1.0, np.NaN, 13.0],
         ["02/01/2017 23:00:00",  8.4, 6.5, 88, np.NaN, np.NaN,  "S",  7.2, 14.4,  999.7, 1010.6, -0.5,  "0.0/1h", 2, np.NaN, np.NaN, np.NaN, 11.0]],

         columns=["date",
                  "t_°C", "td_°C",
                  "hr_%",
                  "tmax_°C", "tmin_°C",
                  "ddd", "ff_kmh", "gust_kmh",
                  "p0_hpa", "p_sea_hpa", "p_tnd",
                  "prec_mm", "n_t", "n_h", "h_km", "inso_d-1", "vis_km"]
    )

    NUMERICS = [x for x in RESULTATS.columns if x not in ("date", "ddd", "prec_mm")]

    @classmethod
    def compare_data(cls, data: pd.DataFrame) -> bool:
        return (data[cls.NUMERICS] - cls.RESULTATS[cls.NUMERICS]).sum().sum() == 0

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")

    def test_scrap_data(self):
        ucf = UserConfigFile.from_json(self.UCF_PATH)
        uc = ucf.get_ogimet_ucs()[0]
        data = self.SCRAPPER.scrap_from_uc(uc).set_index("date")
        self.assertTrue(self.compare_data(data))
