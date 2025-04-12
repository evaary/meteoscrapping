from unittest import TestCase

from app.UserConfigFile import UserConfigFile
from app.boite_a_bonheur.MonthEnum import MonthEnum


class TPsTester(TestCase):

    UCF = UserConfigFile.from_json("./app/tests/ucfs/correct.json")

    def test_nomcase_ogimetd_one_month(self):

        tps = [uc
               for uc in self.UCF.ogimet_ucs
               if uc.city == "Ferrara" and len(uc.dates) == 1][0].to_tps()

        tp_fev_2021 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_fev_2021.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16138&ndays=28&ano=2021&mes=2&day=28&hora=23&lang=en&decoded=no')

    def test_nomcase_ogimetd_months(self):

        tps = [uc
               for uc in self.UCF.ogimet_ucs
               if uc.city == "Ferrara" and len(uc.dates) == 2][0].to_tps()

        tp_jan_2021 = next(tps)
        tp_fev_2021 = next(tps)
        tp_mar_2021 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_jan_2021.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16138&ndays=31&ano=2021&mes=1&day=31&hora=23&lang=en&decoded=no')
        self.assertEqual(tp_fev_2021.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16138&ndays=28&ano=2021&mes=2&day=28&hora=23&lang=en&decoded=no')
        self.assertEqual(tp_mar_2021.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16138&ndays=31&ano=2021&mes=3&day=31&hora=23&lang=en&decoded=no')

    def test_nomcase_ogimeth_one_day(self):

        tps = [uc
               for uc in self.UCF.ogimet_ucs
               if uc.city == "Caserta" and len(uc.dates) == 1][0].to_tps()

        tp_17_jan_2020 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_17_jan_2020.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16288&ndays=1&ano=2020&mes=1&day=17&hora=23&lang=en&decoded=yes')

    def test_nomcase_ogimeth_full_months(self):

        tps = [uc
               for uc in self.UCF.ogimet_ucs
               if(      uc.city == "Caserta"
                   and  len(uc.dates) == 2
                   and  uc.dates[0].startswith("1/"))][0].to_tps()

        tp_mar_2020 = next(tps)
        tp_avr_2020 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_mar_2020.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16288&ndays=31&ano=2020&mes=3&day=31&hora=23&lang=en&decoded=yes')
        self.assertEqual(tp_avr_2020.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16288&ndays=30&ano=2020&mes=4&day=30&hora=23&lang=en&decoded=yes')

    def test_nomcase_ogimeth_partial_months(self):

        tps = [uc
               for uc in self.UCF.ogimet_ucs
               if(      uc.city == "Caserta"
                   and  len(uc.dates) == 2
                   and  uc.dates[0].startswith("15/"))][0].to_tps()

        tp_mar_2020 = next(tps)
        tp_avr_2020 = next(tps)
        tp_mai_2020 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_mar_2020.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16288&ndays=17&ano=2020&mes=3&day=31&hora=23&lang=en&decoded=yes')
        self.assertEqual(tp_avr_2020.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16288&ndays=30&ano=2020&mes=4&day=30&hora=23&lang=en&decoded=yes')
        self.assertEqual(tp_mai_2020.url,
                         'https://www.ogimet.com/cgi-bin/gsynres?ind=16288&ndays=15&ano=2020&mes=5&day=15&hora=23&lang=en&decoded=yes')


    def test_nomcase_wundd_one_month(self):

        tps = [uc
               for uc in self.UCF.wunderground_ucs
               if len(uc.dates) == 1][0].to_tps()

        tp_jan_2020 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_jan_2020.url,
                         'https://www.wunderground.com/history/monthly/it/matera/LIBD/date/2020-1')

    def test_nomcase_wundd_months(self):

        tps = [uc
               for uc in self.UCF.wunderground_ucs
               if len(uc.dates) == 2][0].to_tps()

        tp_jan_2020 = next(tps)
        tp_fev_2020 = next(tps)
        tp_mar_2020 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_jan_2020.url,
                         'https://www.wunderground.com/history/monthly/it/matera/LIBD/date/2020-1')
        self.assertEqual(tp_fev_2020.url,
                         'https://www.wunderground.com/history/monthly/it/matera/LIBD/date/2020-2')
        self.assertEqual(tp_mar_2020.url,
                         'https://www.wunderground.com/history/monthly/it/matera/LIBD/date/2020-3')


    def test_nomcase_metcield_one_month(self):

        tps = [uc
               for uc in self.UCF.meteociel_ucs
               if uc.city == "orleans" and len(uc.dates) == 1][0].to_tps()

        tp_fev_2021 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_fev_2021.url,
                         'https://www.meteociel.com/climatologie/obs_villes.php?code=7249&annee=2021&mois=2')

    def test_nomcase_metcield_months(self):

        tps = [uc
               for uc in self.UCF.meteociel_ucs
               if uc.city == "orleans" and len(uc.dates) == 2][0].to_tps()

        tp_jan_2021 = next(tps)
        tp_fev_2021 = next(tps)
        tp_mar_2021 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_jan_2021.url,
                         'https://www.meteociel.com/climatologie/obs_villes.php?code=7249&annee=2021&mois=1')
        self.assertEqual(tp_fev_2021.url,
                         'https://www.meteociel.com/climatologie/obs_villes.php?code=7249&annee=2021&mois=2')
        self.assertEqual(tp_mar_2021.url,
                         'https://www.meteociel.com/climatologie/obs_villes.php?code=7249&annee=2021&mois=3')

    def test_nomcase_metcielh_one_day(self):

        tps = [uc
               for uc in self.UCF.meteociel_ucs
               if uc.city == "bourges" and len(uc.dates) == 1][0].to_tps()

        tp_15_fev_2021 = next(tps)

        with self.assertRaises(StopIteration):
            next(tps)

        self.assertEqual(tp_15_fev_2021.url,
                         'https://www.meteociel.com/temps-reel/obs_villes.php?code2=7255&annee2=2021&mois2=1&jour2=15')

    def test_nomcase_metcielh_full_months(self):

        tps = [uc
               for uc in self.UCF.meteociel_ucs
               if(      uc.city == "bourges"
                   and  len(uc.dates) == 2
                   and  uc.dates[0].startswith("1/"))][0].to_tps()

        urls = [tp.url for tp in tps]
        tests_jan_2021 = [url for url in urls if "mois2=0" in url]
        tests_fev_2021 = [url for url in urls if "mois2=1" in url]

        refs_jan_2021 = [f"https://www.meteociel.com/temps-reel/obs_villes.php?code2=7255&annee2=2021&mois2=0&jour2={x}"
                        for x in range(1, MonthEnum.from_id(1).ndays + 1)]

        refs_fev_2021 = [f"https://www.meteociel.com/temps-reel/obs_villes.php?code2=7255&annee2=2021&mois2=1&jour2={x}"
                        for x in range(1, MonthEnum.from_id(2).ndays + 1)]

        diffs_jan_2021 = set(refs_jan_2021).difference(set(tests_jan_2021))
        diffs_fev_2021 = set(refs_fev_2021).difference(set(tests_fev_2021))

        self.assertEqual(len(diffs_jan_2021), 0)
        self.assertEqual(len(diffs_fev_2021), 0)

    def test_nomcase_metcielh_partial_months(self):

        tps = [uc
               for uc in self.UCF.meteociel_ucs
               if(      uc.city == "bourges"
                   and  len(uc.dates) == 2
                   and  uc.dates[0].startswith("15/"))][0].to_tps()

        urls = [tp.url for tp in tps]
        tests_mar_2021 = [url for url in urls if "mois2=2" in url]
        tests_avr_2021 = [url for url in urls if "mois2=3" in url]
        tests_mai_2021 = [url for url in urls if "mois2=4" in url]

        refs_mar_2021 = [f"https://www.meteociel.com/temps-reel/obs_villes.php?code2=7255&annee2=2021&mois2=2&jour2={x}"
                        for x in range(15, MonthEnum.from_id(3).ndays + 1)]

        refs_avr_2021 = [f"https://www.meteociel.com/temps-reel/obs_villes.php?code2=7255&annee2=2021&mois2=3&jour2={x}"
                        for x in range(1, MonthEnum.from_id(4).ndays + 1)]

        refs_mai_2021 = [f"https://www.meteociel.com/temps-reel/obs_villes.php?code2=7255&annee2=2021&mois2=4&jour2={x}"
                        for x in range(1, 16)]

        diffs_mar_2021 = set(refs_mar_2021).difference(set(tests_mar_2021))
        diffs_avr_2021 = set(refs_avr_2021).difference(set(tests_avr_2021))
        diffs_mai_2021 = set(refs_mai_2021).difference(set(tests_mai_2021))

        self.assertEqual(len(diffs_mar_2021), 0)
        self.assertEqual(len(diffs_avr_2021), 0)
        self.assertEqual(len(diffs_mai_2021), 0)
