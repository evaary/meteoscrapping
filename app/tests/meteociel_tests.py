from unittest import TestCase
import pandas as pd
from app.scrappers_module import MeteocielHourly, MeteocielDaily
from app.UserConfigFile import UserConfigFile


class MeteocielDailyTester(TestCase):

    SCRAPPER = MeteocielDaily()
    UCF_PATH = "./app/tests/ucfs/meteociel_daily.json"
    URL_REF = "https://www.meteociel.com/climatologie/obs_villes.php?code=7249&mois=1&annee=2021"

    RESULTATS = pd.DataFrame(
        [["2021-01-01",  2.1, -3.6,  0.0, 3.9],
         ["2021-01-02",  4.0, -2.2,  0.2, 6.0],
         ["2021-01-03",  3.2,  0.4,  2.0, 0.0],
         ["2021-01-04",  2.3,  0.2,  0.4, 0.0],
         ["2021-01-05",  2.3,  1.6,  0.0, 0.0],
         ["2021-01-06",  3.1,  1.5,  0.0, 0.0],
         ["2021-01-07",  3.9, -0.3,  0.0, 0.9],
         ["2021-01-08", -0.1, -4.2,  0.0, 3.3],
         ["2021-01-09",  2.8, -3.3,  0.0, 2.6],
         ["2021-01-10",  3.9, -1.3,  0.0, 5.7],
         ["2021-01-11",  4.4, -3.7,  0.0, 2.0],
         ["2021-01-12",  9.2,  1.6,  4.4, 0.0],
         ["2021-01-13", 10.2,  6.4,  1.8, 0.0],
         ["2021-01-14", 10.5,  7.4,  0.4, 0.3],
         ["2021-01-15",  3.2,  1.8,  0.0, 0.6],
         ["2021-01-16",  4.7, -3.8,  5.0, 0.0],
         ["2021-01-17",  8.0,  1.6,  0.4, 4.9],
         ["2021-01-18",  7.0, -1.7,  0.0, 1.6],
         ["2021-01-19",  8.3,  3.2,  0.0, 7.1],
         ["2021-01-20", 12.8,  5.3,  2.4, 2.6],
         ["2021-01-21", 10.6,  5.8, 26.6, 0.2],
         ["2021-01-22",  6.6,  2.4,  0.8, 1.8],
         ["2021-01-23",  6.5,  1.9,  4.2, 1.9],
         ["2021-01-24",  3.4, -3.3,  2.6, 0.2],
         ["2021-01-25",  5.1, -0.4,  0.0, 5.6],
         ["2021-01-26",  2.9, -3.4,  1.6, 1.2],
         ["2021-01-27", 10.7,  1.8,  2.6, 0.0],
         ["2021-01-28", 13.8,  8.0,  4.0, 0.4],
         ["2021-01-29", 12.7,  6.0,  4.6, 2.2],
         ["2021-01-30", 12.4,  6.3,  0.4, 1.6],
         ["2021-01-31", 11.0,  7.8,  6.4, 0.6]],

        columns=["date",
                 "temperature_max_°C",
                 "temperature_min_°C",
                 "precipitations_24h_mm",
                 "ensoleillement_h"]
    )

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")

    def test_scrap_data(self):
        ucf = UserConfigFile.from_json(self.UCF_PATH)
        uc = ucf.meteociel_ucs[0]
        data = self.SCRAPPER.scrap_uc(uc).set_index("date")

        differences_df = data - self.RESULTATS

        self.assertEqual(differences_df.sum().sum(), 0)
        self.assertEqual(data.shape, self.RESULTATS.shape)


class MeteocielHourlyTester(TestCase):

    SCRAPPER = MeteocielHourly()
    UCF_PATH = "./app/tests/ucfs/meteociel_hourly.json"
    URL_REF = "https://www.meteociel.com/temps-reel/obs_villes.php?code2=7249&jour2=1&mois2=0&annee2=2020"

    RESULTATS = pd.DataFrame(
        [["2020-01-01 23:00:00", "8/8", 0.7, 7.2, 100, 7.2, 7.2,  5.4, 160,  9, 12, 1028.8, 0.0],
         ["2020-01-01 22:00:00", "8/8", 0.7, 7.1, 100, 7.1, 7.1,  5.3, 160,  9, 15, 1028.9, 0.2],
         ["2020-01-01 21:00:00", "8/8", 1.5, 7.0, 100, 7.0, 7.0,  5.2, 160,  9, 16, 1029.1, 0.6],
         ["2020-01-01 20:00:00", "8/8", 2.3, 6.9, 100, 6.9, 6.9,  4.9, 170, 10, 15, 1029.4, 0.0],
         ["2020-01-01 19:00:00", "8/8", 1.1, 6.8, 100, 6.8, 6.8,  4.6, 160, 11, 18, 1029.6, 0.0],
         ["2020-01-01 18:00:00", "8/8", 1.5, 6.8, 100, 6.8, 6.8,  4.6, 150, 11, 17, 1029.5, 0.0],
         ["2020-01-01 17:00:00", "8/8", 1.0, 6.7, 100, 6.7, 6.7,  4.4, 150, 11, 17, 1029.6, 0.0],
         ["2020-01-01 16:00:00", "8/8", 3.2, 6.8, 100, 6.8, 6.8,  4.4, 160, 12, 19, 1029.6, 0.0],
         ["2020-01-01 15:00:00", "8/8", 1.1, 6.4, 100, 6.4, 6.4,  3.9, 150, 12, 20, 1029.6, 0.0],
         ["2020-01-01 14:00:00", "8/8", 2.8, 5.9, 100, 5.9, 5.9,  3.1, 150, 13, 19, 1029.9, 0.0],
         ["2020-01-01 13:00:00", "8/8", 3.0, 5.2, 100, 5.2, 5.2,  1.9, 160, 15, 21, 1030.8, 0.0],
         ["2020-01-01 12:00:00", "8/8", 2.5, 4.6, 100, 4.6, 4.6,  1.4, 160, 14, 22, 1031.6, 0.0],
         ["2020-01-01 11:00:00", "8/8", 1.3, 3.7, 100, 3.7, 3.7,  0.3, 150, 14, 20, 1031.5, 0.0],
         ["2020-01-01 10:00:00", "8/8", 1.5, 3.0, 100, 3.0, 3.0, -0.6, 150, 14, 20, 1031.6, 0.0],
         ["2020-01-01 09:00:00", "8/8", 0.8, 2.5, 100, 2.5, 2.5, -0.6, 150, 11, 20, 1031.5, 0.0],
         ["2020-01-01 08:00:00", "9/8", 0.4, 2.3, 100, 2.3, 2.3, -0.8, 140, 11, 16, 1031.0, 0.0],
         ["2020-01-01 07:00:00", "9/8", 0.4, 2.4, 100, 2.4, 2.4, -0.9, 150, 12, 18, 1030.8, 0.0],
         ["2020-01-01 06:00:00", "8/8", 0.6, 2.5, 100, 2.5, 2.5, -0.4, 140, 10, 14, 1031.0, 0.0],
         ["2020-01-01 05:00:00", "8/8", 0.5, 2.6, 100, 2.6, 2.6,  0.0, 140,  9, 12, 1031.2, 0.0],
         ["2020-01-01 04:00:00", "8/8", 0.9, 2.5, 100, 2.5, 2.5,  0.2, 180,  8, 12, 1031.4, 0.0],
         ["2020-01-01 03:00:00", "8/8", 0.7, 2.3, 100, 2.3, 2.3,  1.5, 140,  4, 11, 1031.6, 0.0],
         ["2020-01-01 02:00:00", "9/8", 0.5, 2.1, 100, 2.1, 2.1,  0.4, 150,  6, 10, 1031.7, 0.0],
         ["2020-01-01 01:00:00", "8/8", 0.5, 1.7, 100, 1.7, 1.7, -0.4, 130,  7, 10, 1031.8, 0.0],
         ["2020-01-01 00:00:00", "8/8", 0.3, 1.4, 100, 1.4, 1.4, -0.4, 130,  6, 10, 1032.1, 0.0]],

        columns=["date", "neb", "visi_km", "temperature_°C", "humi_%", "point_de_rosee_°C", "humidex",
                 "windchill", "direction_du_vent_°", "vent_km/h", "rafales_km/h", "pression_hPa", "precip_mm"]
    )

    @classmethod
    def setUpClass(cls):
        cls.RESULTATS["date"] = pd.to_datetime(cls.RESULTATS["date"])
        cls.RESULTATS = cls.RESULTATS.set_index("date")\
                                     .sort_values(by="date")

    def test_scrap_data(self):
        ucf = UserConfigFile.from_json(self.UCF_PATH)
        uc = ucf.meteociel_ucs[0]
        data = self.SCRAPPER.scrap_uc(uc).set_index("date")

        numeric = [x for x in self.RESULTATS.columns if x != "neb"]
        differences_df = data[numeric] - self.RESULTATS[numeric]

        self.assertEqual(differences_df.sum().sum(), 0)
