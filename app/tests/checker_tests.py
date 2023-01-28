from unittest import TestCase
import copy
from app.ConfigFileChecker import ConfigFilesChecker, ConfigCheckerException

class CheckerTester(TestCase):

    CHECKER = ConfigFilesChecker.instance()

    CONFIG = {
        "waiting": 3,

        "ogimet":[
            { "ind":"16138", "city":"Ferrara", "year":[2021], "month":[2] }
        ],

        "wunderground":[
            { "country_code":"it", "region": "LIBD", "city":"matera", "year":[2021], "month":[1] }
        ],

        "meteociel":[
            { "code_num":"2", "code": "7249", "city":"orleans", "year":[2020], "month":[2] }
        ],

        "meteociel_daily":[
            { "code_num":"2", "code": "7249", "city":"orleans", "year":[2020], "month":[2], "day":[27,31] }
        ]
    }

    def test_missing_main_fields(self):

        todo = copy.deepcopy(self.CONFIG)
        del todo["waiting"]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_main_fields(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["main_fields"])

    def test_unknown_main_fields(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["bouh"] = ["test"]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_main_fields(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["main_fields"])

    def test_wrong_fields_ogimet(self):

        todo = copy.deepcopy(self.CONFIG)
        del todo["ogimet"][0]["ind"]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_keys(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["configs"])

    def test_wrong_fields_wunderground(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["bouh"] = 5

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_keys(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["configs"])

    def test_wrong_fields_meteociel(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel"][0]["bouh"] = 5

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_keys(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["configs"])

    def test_year_not_list(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["ogimet"][0]["year"] = "bouh"

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["dates"])

    def test_month_not_len_1_or_2(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel"][0]["month"] = [1,2,3]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["dates"])

    def test_year_not_ints(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["year"] = [1.1, "bouh"]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["dates"])

    def test_day_not_positive(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel_daily"][0]["day"] = [-1, 17]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["dates"])

    def test_days_not_ordered(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel_daily"][0]["day"] = [2,1]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["dates"])

    def test_outbound_month(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["ogimet"][0]["month"] = [1,17]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["month"])

    def test_outbound_day(self):

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel_daily"][0]["day"] = [1,56]

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["day"])

    def test_not_str_value(self):

        # si une des clés hors year / month d'une config n'a pas pour valeur une string

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel"][0]["city"] = 12

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["other"])

    def test_wrong_waiting_value(self):

        # test lorsque wainting est une str

        todo = copy.deepcopy(self.CONFIG)
        todo["waiting"] = "test"

        with self.assertRaises(ConfigCheckerException) as e:
            self.CHECKER._check_values(todo)

        self.assertEqual(str(e.exception), self.CHECKER.ERRORS_MSG["waiting"])

    def test_correct_config(self):

        try:
            self.CHECKER.check(self.CONFIG)
        except:
            self.fail("exception dans le cas où tout va bien")

