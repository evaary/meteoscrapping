from unittest import TestCase
import copy
from app.ConfigFileChecker import ConfigFilesChecker

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

        '''test lorsqu'un champs principal est manquant'''

        todo = copy.deepcopy(self.CONFIG)
        del todo["waiting"]

        self.CHECKER._check_main_fields(todo)
        # on cherche un terme spécifique à l'erreur attendue dans l'erreur retournée
        self.assertIn("principaux", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_unknown_main_fields(self):

        '''test lorsqu'un champs principal inconnu est présent'''

        todo = copy.deepcopy(self.CONFIG)
        todo["bouh"] = ["test"]

        self.CHECKER._check_main_fields(todo)
        self.assertIn("principaux", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_wrong_fields_ogimet(self):

        '''test lorsque les clés d'un dict ne correspondent pas à celles attendues'''

        todo = copy.deepcopy(self.CONFIG)
        del todo["ogimet"][0]["ind"]

        self.CHECKER._check_keys(todo)
        self.assertIn("ogimet", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_wrong_fields_wunderground(self):

        '''test lorsque les clés d'un dict ne correspondent pas à celles attendues'''

        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["bouh"] = 5

        self.CHECKER._check_keys(todo)
        self.assertIn("wunderground", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_wrong_fields_meteociel(self):

        '''test lorsque les clés d'un dict ne correspondent pas à celles attendues'''

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel"][0]["bouh"] = 5

        self.CHECKER._check_keys(todo)
        self.assertIn("meteociel", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_year_month_not_list(self):

        '''test lorsque les year et month ne sont pas des listes de 2 entiers positifs'''

        todo = copy.deepcopy(self.CONFIG)
        todo["ogimet"][0]["year"] = "bouh"

        self.CHECKER._check_values(todo)
        self.assertIn("listes", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_year_month_not_len_1_or_2(self):

        '''test lorsque les year et month ne sont pas des listes de max 2 entiers positifs'''

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel"][0]["month"] = [1,2,3]

        self.CHECKER._check_values(todo)
        self.assertIn("2", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_year_month_not_ints(self):

        '''test lorsque les year et month ne sont pas des listes de 2 entiers positifs'''

        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["year"] = [1.1, "bouh"]

        self.CHECKER._check_values(todo)
        self.assertIn("entiers", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_year_month_not_ordered(self):

        '''test lorsque les year et month ne sont pas des listes ordonnées'''

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel_daily"][0]["day"] = [2,1]

        self.CHECKER._check_values(todo)
        self.assertIn("ordonnés", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_outbound_month(self):

        '''test lorsque le mois n'est pas entre 1 et 12'''

        todo = copy.deepcopy(self.CONFIG)
        todo["ogimet"][0]["month"] = [1,17]

        self.CHECKER._check_values(todo)
        self.assertIn("compris", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_not_str_value(self):

        '''si une des clés hors year / month d'une config n'a pas pour valeur une string'''

        todo = copy.deepcopy(self.CONFIG)
        todo["meteociel"][0]["city"] = 12

        self.CHECKER._check_values(todo)
        self.assertIn("autres que", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_wrong_waiting_value(self):

        '''test lorsque wainting est une str'''

        todo = copy.deepcopy(self.CONFIG)
        todo["waiting"] = "test"

        self.CHECKER._check_values(todo)
        self.assertIn("waiting", self.CHECKER.error)
        self.assertFalse(self.CHECKER.is_legal)

    def test_correct_config(self):
        self.CHECKER.check(self.CONFIG)
        self.assertTrue(self.CHECKER.is_legal)
