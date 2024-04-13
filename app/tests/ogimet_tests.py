from unittest import TestCase

import numpy as np
import pandas as pd

from app.scrappers_module import (OgimetDaily, OgimetHourly)
from app.UserConfigFile import UserConfigFile


class OgimetDailyTester(TestCase):

    SCRAPPER = OgimetDaily()
    UCF_PATH = "./app/tests/ucfs/ogimet_daily.json"
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
                 "temperature_°C_max", "temperature_°C_min", "temperature_°C_avg",
                 "td_avg_°C", "hr_avg_%",
                 "wind_km/h_dir", "wind_km/h_int",
                 "pres_slev_hp", "prec_mm",
                 "tot_cl_oct", "low_cl_oct",
                 "vis_km"]
    )

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")

    def test_scrap_data(self):
        ucf = UserConfigFile.from_json(self.UCF_PATH)
        uc = ucf.ogimet_ucs[0]
        data = self.SCRAPPER.scrap_uc(uc).set_index("date")

        numerics = self.RESULTATS\
                       .columns\
                       .difference(["wind_km/h_dir", "date", "prec_mm"])

        differences_df = data[numerics] - self.RESULTATS[numerics]

        self.assertEqual(differences_df.sum().sum(), 0)


class OgimetHourlyTester(TestCase):

    SCRAPPER = OgimetHourly()
    UCF_PATH = "./app/tests/ucfs/ogimet_hourly.json"
    URL_REF = "https://www.ogimet.com/cgi-bin/gsynres?ind=07149&lang=en&decoded=yes&ndays=1&ano=2023&mes=02&day=01&hora=23"

    RESULTATS = pd.DataFrame(
        [["2023-02-01 00:00:00", 6.7, 4.9, 88, np.NaN, np.NaN, "WSW", 10.8, 18.0, 1017.3, 1028.5, -0.4,         "Tr/6h",    8.0, 8,    0.3, np.NaN, 15.0],
         ["2023-02-01 01:00:00", 6.5, 4.8, 89, np.NaN, np.NaN,  "SW", 10.8, 18.0, 1017.0, 1028.2, -0.7,        "0.0/1h",    8.0, 8,    0.3, np.NaN, 14.0],
         ["2023-02-01 02:00:00", 6.1, 4.7, 91, np.NaN, np.NaN, "WSW",  7.2, 18.0, 1017.4, 1028.6,  0.1,        "0.0/1h",    8.0, 8,    0.3, np.NaN, 11.0],
         ["2023-02-01 03:00:00", 6.6, 4.9, 89, np.NaN, np.NaN, "WSW",  7.2, 14.4, 1017.2, 1028.4, -0.1,        "0.0/3h",    8.0, 8,    0.6, np.NaN, 18.0],
         ["2023-02-01 04:00:00", 7.3, 2.6, 72, np.NaN, np.NaN, "WNW", 18.0, 28.8, 1017.4, 1028.6,  0.4,        "0.0/1h",    8.0, 8,    1.0, np.NaN, 28.0],
         ["2023-02-01 05:00:00", 6.9, 2.4, 73, np.NaN, np.NaN,   "W", 14.4, 25.2, 1017.3, 1028.5, -0.1,        "0.0/1h",    7.0, 7,    1.0, np.NaN, 27.0],
         ["2023-02-01 06:00:00", 5.9, 2.2, 77,    7.6,    5.9,   "W", 10.8, 18.0, 1017.8, 1029.0,  0.6, "Tr/24h_Tr/12h", np.NaN, 3, np.NaN,    1.6, 19.0],
         ["2023-02-01 07:00:00", 5.6, 2.2, 79, np.NaN, np.NaN, "WSW",  7.2, 18.0, 1017.9, 1029.1,  0.5,        "0.0/1h",    6.0, 6,    1.0, np.NaN, 20.0],
         ["2023-02-01 08:00:00", 5.6, 2.2, 79, np.NaN, np.NaN,   "W",  7.2, 14.4, 1018.7, 1029.9,  1.4,        "0.0/1h",    5.0, 5,    1.0, np.NaN, 20.0],
         ["2023-02-01 09:00:00", 7.2, 2.9, 74, np.NaN, np.NaN, "WSW", 10.8, 18.0, 1018.3, 1029.5,  0.5,        "0.0/3h",    6.0, 6,    1.0, np.NaN, 20.0],
         ["2023-02-01 10:00:00", 7.7, 2.4, 69, np.NaN, np.NaN,   "W", 14.4, 28.8, 1019.1, 1030.3,  1.2,        "0.0/1h",    7.0, 7,    1.0, np.NaN, 15.0],
         ["2023-02-01 11:00:00", 8.8, 2.4, 64, np.NaN, np.NaN,   "W", 21.6, 32.4, 1018.9, 1030.0,  0.2,        "0.0/1h",    8.0, 8,    1.0, np.NaN, 21.0],
         ["2023-02-01 12:00:00", 9.5, 3.2, 65, np.NaN, np.NaN,   "W", 25.2, 39.6, 1018.5, 1029.6,  0.2,        "0.0/6h",    7.0, 7,    0.6, np.NaN, 15.0],
         ["2023-02-01 13:00:00", 9.6, 2.2, 60, np.NaN, np.NaN,   "W", 25.2, 36.0, 1018.0, 1029.1, -1.1,        "0.0/1h",    7.0, 7,    0.6, np.NaN, 19.0],
         ["2023-02-01 14:00:00", 9.2, 2.3, 62, np.NaN, np.NaN,   "W", 21.6, 43.2, 1017.6, 1028.7, -1.3,        "0.0/1h",    7.0, 7,    1.0, np.NaN, 15.0],
         ["2023-02-01 15:00:00", 9.2, 2.3, 62, np.NaN, np.NaN,   "W", 21.6, 36.0, 1017.5, 1028.6, -1.0,        "0.0/3h",    7.0, 7,    1.0, np.NaN, 15.0],
         ["2023-02-01 16:00:00", 8.9, 2.2, 63, np.NaN, np.NaN,   "W", 18.0, 32.4, 1017.7, 1028.8, -0.3,        "0.0/1h",    6.0, 6,    1.0, np.NaN, 30.0],
         ["2023-02-01 17:00:00", 8.7, 2.0, 63, np.NaN, np.NaN,   "W", 10.8, 25.2, 1018.1, 1029.2,  0.5,        "0.0/1h",    7.0, 7,    1.0, np.NaN, 15.0],
         ["2023-02-01 18:00:00", 8.4, 2.0, 64,   10.7,    5.5,   "W", 14.4, 21.6, 1018.4, 1029.5,  0.9,       "0.0/12h",    7.0, 6,    1.0, np.NaN, 15.0],
         ["2023-02-01 19:00:00", 7.9, 2.1, 67, np.NaN, np.NaN, "WNW", 10.8, 21.6, 1018.5, 1029.7,  0.8,        "0.0/1h",    7.0, 7,    1.5, np.NaN, 15.0],
         ["2023-02-01 20:00:00", 8.1, 2.1, 66, np.NaN, np.NaN, "WSW", 14.4, 25.2, 1018.7, 1029.8,  0.6,        "0.0/1h",    7.0, 7,    1.5, np.NaN, 15.0],
         ["2023-02-01 21:00:00", 7.4, 2.9, 73, np.NaN, np.NaN,   "W", 10.8, 21.6, 1018.9, 1030.1,  0.5,        "0.0/3h",    7.0, 7,    1.5, np.NaN, 15.0],
         ["2023-02-01 22:00:00", 6.9, 2.8, 75, np.NaN, np.NaN,   "W", 14.4, 21.6, 1018.8, 1030.0,  0.3,        "0.0/1h",    7.0, 7,    1.5, np.NaN, 15.0],
         ["2023-02-01 23:00:00", 6.3, 3.1, 80, np.NaN, np.NaN, "WSW", 10.8, 21.6, 1018.8, 1030.0,  0.1,        "0.0/1h",    7.0, 4,    1.5, np.NaN, 15.0]],

         columns=["date",
                  "t_°C", "td_°C",
                  "hr_%",
                  "tmax_°C", "tmin_°C",
                  "ddd", "ff_km/h", "gust_km/h",
                  "p0_hPa", "p_sea_hPa", "p_tnd",
                  "prec_mm", "n_t", "n_h", "h_km", "inso_d-1", "vis_km"]
    )

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")

    def test_scrap_data(self):
        ucf = UserConfigFile.from_json(self.UCF_PATH)
        uc = ucf.ogimet_ucs[0]
        data = self.SCRAPPER.scrap_uc(uc).set_index("date")

        numerics = [x for x in self.RESULTATS.columns if x not in ["date", "ddd", "prec_mm"]]
        differences_df = data[numerics] - self.RESULTATS[numerics]

        self.assertEqual(differences_df.sum().sum(), 0)
