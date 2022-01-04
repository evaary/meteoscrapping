from datetime import time
import unittest
import copy
from utils import ConfigFilesChecker
# from scrappers import OgimetScrapper, WundergroundScrapper

class ConfigCheckerTester(unittest.TestCase):

    CHECKER = ConfigFilesChecker.instance()

    # version correcte des config ogimet et wunderground
    CONFIG_OGIMET = {
        "scrapper": "ogimet",
        "ind": "16288",
        "city": "Caserta",
        "waiting": 1,
        "year": {
            "from": 2020,
            "to": 2020
        },
        "month": {
            "from": 1,
            "to": 12
        }
    }

    CONFIG_WUNDERGROUND = {
        "scrapper": "wunderground",
        "country_code": "it",
        "city": "matera",
        "region": "LIBD",
        "waiting": 5,
        "year": {
            "from": 2020,
            "to": 2020
        },
        "month": {
            "from": 1,
            "to": 12
        }
    }

    CONFIGS = [CONFIG_OGIMET, CONFIG_WUNDERGROUND]

    def test_missing_scrapper(self):
        
        '''
            test lorsqu'il manque le type de scrapper souhaité pour le job
        '''
        # on supprime le champ scrapper dans chaque configuration
        todos = [
            {key: value for key, value in dico.items() if key != "scrapper"}
            for dico in self.CONFIGS
        ]

        for config in todos:
            
            is_correct, error = self.CHECKER.check(config)
            # on cherche un terme spécifique à l'erreur attendue dans l'erreur retournée
            self.assertIn("'scrapper'", error)
            self.assertFalse(is_correct)
    
    def test_wrong_scrapper_value(self):

        '''
            test lorsqu le type de scrapper souhaité pour le job est présent mais erroné
        '''

        todos = [
            { key : "bouh" if key == "scrapper" else value for config in self.CONFIGS for key, value in config.items() }
        ]

        for config in todos:
            
            is_correct, error = self.CHECKER.check(config)
            self.assertIn("'scrapper'", error)
            self.assertFalse(is_correct)
    
    def test_missing_fields(self):
        
        '''
            test lorsqu'il manque une des clés du dict autre que scrapper
        '''
        # pour chaque clé du dict de config autre que scrapper, on créé un dict
        # identique à l'original, sauf qu'il ne contient pas la clé courante.
        todos = [
            {key: value for key, value in dico.items() if key != key_to_delete}
            for dico in self.CONFIGS
            for key_to_delete in dico.keys() if key_to_delete != "scrapper"
        ]

        for config in todos:
            
            is_correct, error = self.CHECKER.check(config)
            self.assertIn("pour le scrapper", error)
            self.assertFalse(is_correct)

    def test_no_positive_int_year_month(self):
        
        '''
            test lorsque les champs from et to des dicts year et month ne sont pas des entiers positifs
        '''
        to_change = [
            
            (timescale, field, wrong)
            
            for timescale in ["year", "month"]
            for field in ["from", "to"]
            for wrong in [11.1, "bouh"]
        ]
        
        todos = [ [copy.deepcopy(config) for _ in to_change] for config in self.CONFIGS ]

        for ogimet_config, wunderground_config, tup in zip(*todos, to_change):
            
            timescale, field, wrong = tup
            ogimet_config[timescale][field] = wrong
            wunderground_config[timescale][field] = wrong

        todos = [ x for liste in todos for x in liste ]

        for config in todos:
            
            is_correct, error = self.CHECKER.check(config)                    
            self.assertIn("entiers positifs", error)
            self.assertFalse(is_correct)

    def test_min_max_inversion_year_month(self):

        '''
            test lorsque le champ from est supérieur au champ to
        '''

        todos = [ [copy.deepcopy(config) for _ in range(2)] for config in self.CONFIGS ]

        for ogimet_config, wunderground_config, timescale in zip(*todos, ("year", "month")):

            ogimet_config[timescale]["from"] = 10
            ogimet_config[timescale]["to"] = 5
            wunderground_config[timescale]["from"] = 10
            wunderground_config[timescale]["to"] = 5

        todos = [ x for liste in todos for x in liste ]

        for config in todos:

            is_correct, error = self.CHECKER.check(config)                    
            self.assertIn("inférieur", error)
            self.assertFalse(is_correct)

    def test_outbound_month(self):

        '''
            test lorsque le mois n'est pas inférieur à 12 (la valeur 0 est traitée dans test_no_positive_int_year_month)
        '''

        todos = [ [copy.deepcopy(config) for _ in range(1)] for config in self.CONFIGS ]

        for ogimet_config, wunderground_config in zip(*todos):

            ogimet_config["month"]["to"] = 15
            wunderground_config["month"]["to"] = 15

        todos = [ x for liste in todos for x in liste ]

        for config in todos:

            is_correct, error = self.CHECKER.check(config)                    
            self.assertIn("compris", error)
            self.assertFalse(is_correct)

    def test_correct_config(self):

        for config in self.CONFIGS:

            is_correct, _ = self.CHECKER.check(config)

            self.assertTrue(is_correct)

class OgimetScrapperTester(unittest.TestCase):
    pass

class WundergroundScrapperTester(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
