from unittest import TestCase

import numpy as np
import pandas as pd

from app.scrappers.ogimet_scrappers import OgimetDaily
from app.ucs.UserConfigFile import UserConfigFile


class OgimetDailyTester(TestCase):

    SCRAPPER = OgimetDaily()
    UCF_PATH = "./app/tests/ucfs/ogimet_daily.json"

    # valeurs de référence pour janvier 2021
    URL_REF = "http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=16138&ano=2021&mes=3&day=0&hora=0&min=0&ndays=28"

    RESULTATS = pd.DataFrame(
        [["2021-02-01",   6.8,   5.6,	 6.4,	  4.2,	86.2,	"WNW",	 8.5,	 996.1, 	7.8, 	   7.8,	    3.8],
         ["2021-02-02",   7.6,   1.0,	 4.7,	  2.7,	83.9,	"CAL",	 0.0,	1000.0, 	4.8, 	   4.2,	    9.2],
         ["2021-02-03",  11.0,   1.4,	 5.2,	  4.0,	87.4,	" NW",	 2.8,	1011.8, 	2.8, 	   3.5,	    4.7],
         ["2021-02-04",   7.6,   2.8,	 5.5,	  4.0,	87.7,	"ENE",	 4.1,	1014.7, 	7.8, 	   7.8,	    1.7],
         ["2021-02-05",   8.3,   5.0,	 6.6,	  4.5,	86.1,	"SSW",	 2.2,	1017.4, 	5.6, 	   6.5,	    3.2],
         ["2021-02-06",   9.8,   4.6,	 7.6,	  5.6,	85.3,	"ESE",	 1.1,	1018.7, 	7.8, 	   7.8,	    1.7],
         ["2021-02-07",   9.2,   7.4,	 8.3,	  6.5,	87.6,	"CAL",	 0.0,	1014.4, 	8.0, 	   8.0,	    2.0],
         ["2021-02-08",  10.0,   7.8,	 9.1,	  7.2,	86.8,	"ENE",	 1.5,	 998.0, 	8.0, 	   8.0,	    1.2],
         ["2021-02-09",  13.2,   5.4,	 8.0,	  3.5,	71.7,	"SSE",	 3.7,	 995.2, 	2.2, 	   3.3,	    8.2],
         ["2021-02-10",  11.0,   7.8,	 8.9,	  7.0,	86.8,	  "W",	 5.6,	 999.2, 	6.6, 	   5.8,	    8.2],
         ["2021-02-11",  11.0,   7.0,	 9.3,	  7.9,	89.4,	 "NE",	 8.2,	 997.7, 	5.4, 	   3.6,	   10.0],
         ["2021-02-12",  11.4,   3.8,	 6.8,	  4.5,	82.0,	"ENE",	 7.8,	1011.5, 	1.8, 	   3.0,	   10.4],
         ["2021-02-13",   5.0,   2.8,	 3.6,	 -2.7,	62.5,	 "NE",	14.8,	1024.1, 	6.4, 	   6.4,	   17.0],
         ["2021-02-14",   2.6,   1.4,	 1.7,   -10.0,	41.7,	 "NE",	22.2,	1029.4, 	2.4, 	   4.5,	   30.0],
         ["2021-02-15",   7.4,  -2.0,	 2.0,	 -9.5,	44.8,	 "NW",	 8.2,	1037.6, 	0.4, 	np.NaN,	   16.0],
         ["2021-02-16",   9.0,  -4.0,	 3.0,	 -9.1,	42.4,	"ESE",	 1.9,	1038.0, 	1.8, 	   3.5,	   44.0],
         ["2021-02-17",  10.8,  -0.2,	 5.0,	 -0.7,	62.4,	"NNW",	 6.5,	1026.9, 	1.8, 	   0.2,	   16.0],
         ["2021-02-18",  11.0,   4.0,	 6.6,	  3.1,	75.7,	"CAL",	 0.0,	1022.0, 	4.6, 	   7.7,	   10.0],
         ["2021-02-19",  12.0,   4.8,	 8.4,	  3.7,	70.0,	  "S",	 3.1,	1023.5, 	3.2, 	   4.0,	    5.6],
         ["2021-02-20",  14.4,   5.8,	 9.6,	  5.6,	74.1,	 "SW",	 2.6,	1024.1, 	4.2, 	   4.2,	    5.6],
         ["2021-02-21",  15.0,   4.8,	 8.9,	  6.0,	78.9,	 "NE",	 2.5,	1025.9, 	4.2, 	   4.2,	    3.0],
         ["2021-02-22",  13.8,   5.4,	 8.9,	  5.8,	77.4,	"ENE",	 1.9,	1027.2, 	4.6, 	   7.7,	    5.0],
         ["2021-02-23",  12.0,   5.4,	 8.9,	  6.6,	84.6,	"NNW",	 3.0,	1031.4, 	4.6, 	   7.7,	    2.9],
         ["2021-02-24",  13.4,   2.8,	 7.7,	  5.3,	79.5,	"NNW",	 3.0,	1035.9, 	0.0, 	np.NaN,	    2.6],
         ["2021-02-25",  17.4,   2.8,	10.7,	  3.2,	58.6,	  "W",	 7.8,	1034.7, 	0.0, 	np.NaN,	    8.2],
         ["2021-02-26",  18.6,   4.8,	10.9,	  3.6,	59.7,	  "W",	 4.1,	1031.6, 	0.0, 	np.NaN,	   10.4],
         ["2021-02-27",  18.2,   3.2,	10.3,	  3.3,	59.6,	 "SW",	 5.6,	1027.3, 	0.0, 	np.NaN,	    9.4],
         ["2021-02-28",  17.0,   3.2,	 9.4,	  5.7,	72.3,	 "SE",	 5.6,	1025.1, 	3.0, 	   0.0,	    5.2]],

        columns=["date",
                 "temperature_(°C)_max", "temperature_(°C)_min", "temperature_(°C)_avg",
                 "td_avg_(°C)", "hr_avg_(%)",
                 "wind_(km/h)_dir", "wind_(km/h)_int",
                 "pres_slev_(hp)",
                 "tot_cl_oct", "low_cl_oct",
                 "vis_km"]
    )

    NUMERICS = RESULTATS.columns.difference(["wind_(km/h)_dir", "date"])

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
