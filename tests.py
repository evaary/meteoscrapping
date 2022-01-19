import unittest
import copy
from app.utils import ConfigFilesChecker

class ConfigCheckerTester(unittest.TestCase):

    CHECKER = ConfigFilesChecker.instance()

    # version correcte des config ogimet et wunderground
    CONFIG = {

        "waiting": 1,

        "ogimet":[

            {
                "ind": "16138",
                "city": "Ferrara",
                "year": [2014, 2021],
                "month": [1,12]
            },

            {
                "ind": "16288",
                "city": "Caserta",
                "year": [2020, 2020],
                "month": [1,1]
            }

        ],

        "wunderground":[

            {
                "country_code": "it",
                "city": "matera",
                "region": "LIBD",
                "year": [2020, 2020],
                "month": [1,1]
            }
            
        ]
    }

    def test_wrong_scrapper(self):
        
        '''test lorsqu'un scrapper inconnu est présent'''
        
        todo = copy.deepcopy(self.CONFIG)
        todo["bouh"] = ["test"]
            
        is_correct, error = self.CHECKER.check(todo)
        # on cherche un terme spécifique à l'erreur attendue dans l'erreur retournée
        self.assertIn("principaux", error)
        self.assertFalse(is_correct)
        
    def test_wrong_fields_ogimet(self):
        
        '''test lorsque les clés d'un dict ne correspondent pas à celles attendues'''
        
        todo = copy.deepcopy(self.CONFIG)
        del todo["ogimet"][0]["ind"]
            
        is_correct, error = self.CHECKER.check(todo)
        self.assertIn("ogimet", error)
        self.assertFalse(is_correct)

    def test_wrong_fields_wunderground(self):
        
        '''test lorsque les clés d'un dict ne correspondent pas à celles attendues'''
        
        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["bouh"] = 5
            
        is_correct, error = self.CHECKER.check(todo)
        self.assertIn("wunderground", error)
        self.assertFalse(is_correct)

    def test_year_month_not_list(self):
        
        '''test lorsque les year et month ne sont pas des listes de 2 entiers positifs'''
        
        todo = copy.deepcopy(self.CONFIG)
        todo["ogimet"][0]["year"] = "bouh"

        is_correct, error = self.CHECKER.check(todo)
        self.assertIn("listes", error)
        self.assertFalse(is_correct)

    def test_year_month_not_len_2(self):
        
        '''test lorsque les year et month ne sont pas des listes de 2 entiers positifs'''
        
        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["month"] = [1,2,3]

        is_correct, error = self.CHECKER.check(todo)
        self.assertIn("2", error)
        self.assertFalse(is_correct)

    def test_year_month_not_ints(self):
        
        '''test lorsque les year et month ne sont pas des listes de 2 entiers positifs'''
        
        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["year"] = [1.1, "bouh"]

        is_correct, error = self.CHECKER.check(todo)
        self.assertIn("entiers", error)
        self.assertFalse(is_correct)

    def test_year_month_not_ordered(self):
        
        '''test lorsque les year et month ne sont pas des listes ordonnées'''
        
        todo = copy.deepcopy(self.CONFIG)
        todo["ogimet"][0]["month"] = [2,1]

        is_correct, error = self.CHECKER.check(todo)
        self.assertIn("ordonnés", error)
        self.assertFalse(is_correct)

    def test_outbound_month(self):

        '''test lorsque le mois n'est pas entre 1 et 12'''

        todo = copy.deepcopy(self.CONFIG)
        todo["ogimet"][1]["month"] = [1,17]
        
        is_correct, error = self.CHECKER.check(todo)                    
        self.assertIn("compris", error)
        self.assertFalse(is_correct)

    def test_not_str_value(self):

        '''si une des clés hors year / month d'une config n'a pas pour valeur une string'''
        
        todo = copy.deepcopy(self.CONFIG)
        todo["wunderground"][0]["city"] = 12

        is_correct, error = self.CHECKER.check(todo)                    
        self.assertIn("autres que", error)
        self.assertFalse(is_correct)

    def test_correct_config(self):

        is_correct, error = self.CHECKER.check(self.CONFIG)

        self.assertTrue(is_correct)
        self.assertEqual(error, "")

if __name__ == "__main__":
    unittest.main()
