from app.data_managers import from_json, to_csv, to_json
from app.scrappers import WundergroundScrapper, OgimetScrapper
import os

class ConfigFilesChecker:

    '''Singleton contrôlant la validité d'un fichier de config.'''

    _instance = None
    
    ALLOWED_SCRAPPERS = {"wunderground", "ogimet"}
    
    EXPECTED_KEYS = {
        "wunderground": {"country_code", "city", "region", "year", "month"},
        "ogimet": {"ind", "city", "year", "month"}
    }

    def __init__(self):
        raise RuntimeError("call ConfigFilesChecker.instance() instead")

    @classmethod
    def instance(cls):

        cls._instance = cls._instance if cls._instance is not None else cls.__new__(cls)
        
        return cls._instance

    @classmethod
    def _check_scrapper_type(cls, config:dict) -> tuple:

        reference = cls.ALLOWED_SCRAPPERS.union({"waiting"})
        # On vérifie que les clés du dict sont correctes.
        if not set(config.keys()).issubset(reference):
            return False, f"les champ principaux doivent être {reference}"        

        return True, ""

    @classmethod
    def _check_keys(cls, config:dict) -> tuple:
        
        # On contrôle que toutes les clés des configs correspondent à ce qu'on attend.
        for x in ("ogimet", "wunderground"):
            
            test = [ set(dico.keys()) == cls.EXPECTED_KEYS[x] for dico in config[x] ]
            
            if not all(test):
                return False, f"une des config {x} pose problème"

        return True, ""

    @classmethod
    def _check_values(cls, config):

        for scrapper in ("ogimet", "wunderground"):
            
            dicos = config[scrapper]

            for x in ("year", "month"):

                isList = all( [ isinstance(dico[x], list) and len(dico[x]) in (1,2) for dico in dicos] )
                if not isList:
                    return False, "year et month doivent être des listes de 1 ou 2 entiers positifs ordonnés"  

                arePositiveInts = all( [ isinstance(y, int) and y > 0 for dico in dicos for y in dico[x] ] )
                if not arePositiveInts:
                    return False, "year et month doivent être des listes de 1 ou 2 entiers positifs ordonnés"  

                areOrdered = all( [ dico[x][0] <= dico[x][-1] for dico in dicos ] )
                if not areOrdered:
                    return False, "year et month doivent être des listes de 1 ou 2 entiers positifs ordonnés"  

            todo = {field for field in cls.EXPECTED_KEYS[scrapper] if field not in ("year", "month")}
            
            if not all( [ isinstance(dico[field], str) for dico in dicos for field in todo ] ):
                return False, "les champs autres que year et month doivent être des strings"

            if not all([dico["month"][0] in range(1,13) and dico["month"][-1] in range(1,13) for dico in dicos]):
                return False, "month doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 12"

        return True, ""
    
    @classmethod      
    def check(cls, config):

        for func in [cls._check_scrapper_type, cls._check_keys, cls._check_values]:

            is_correct, error = func(config)
            
            if not is_correct:
                return is_correct, error

        return True, ""

class Runner:

    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {
        "results": os.path.join(WORKDIR, "results"),
        "errors":  os.path.join(WORKDIR, "errors")
    }

    SCRAPPERS = {
        "ogimet": OgimetScrapper.instance(),
        "wunderground": WundergroundScrapper.instance()
    }

    CHECKER = ConfigFilesChecker.instance()

    JOB_ID = 0

    @classmethod
    def _save_data(cls, data, path):

        if len(data) == 0:
            print("no data")
            return
        
        to_csv(data, path)    
    
    @classmethod
    def _save_errors(cls, errors, path):
        
        if len(errors) == 0:
            return
        
        to_json(errors, path)

    @classmethod
    def run(cls):
        
        try:
            configs = from_json(os.path.join(cls.WORKDIR, "config.json"))
        except FileNotFoundError:
            print("pas de fichier config.json")
            return
        
        is_correct, error = cls.CHECKER.check(configs)

        if not is_correct:
            print(error)
            return        
        
        for scrapper_type in {x for x in configs.keys() if x != "waiting"}:
            
            todos = configs[scrapper_type]
            scrapper = cls.SCRAPPERS[scrapper_type]

            for config in todos:

                cls.JOB_ID += 1

                try:
                    config["waiting"] = configs["waiting"]
                except KeyError:
                    pass

                scrapper = scrapper.from_config(config)
                
                path_data = os.path.join(cls.PATHS["results"], f"{config['city']}_{scrapper_type}_{cls.JOB_ID}.csv")
                path_errors = os.path.join(cls.PATHS["errors"], f"{config['city']}_{scrapper_type}_{cls.JOB_ID}_errors.json")

                data = scrapper.get_data()

                cls._save_data(data, path_data)
                cls._save_errors(scrapper.errors, path_errors)

                print("\n")