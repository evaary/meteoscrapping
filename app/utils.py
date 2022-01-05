from app.data_managers import from_json, to_csv, to_json
from app.scrappers import WundergroundScrapper, OgimetScrapper
import os

class ConfigFilesChecker:

    '''Singleton contrôlant la validité d'un fichier de config.'''

    _instance = None
    
    ALLOWED_SCRAPPERS = ("wunderground", "ogimet")
    
    EXPECTED_KEYS = {
        "wunderground": ["country_code", "city", "region", "waiting", "year", "month"],
        "ogimet": ["ind", "city", "waiting", "year", "month"]
    }

    def __init__(self):
        raise RuntimeError("call ConfigFilesChecker.instance() instead")

    @classmethod
    def instance(cls):

        cls._instance = cls._instance if cls._instance is not None else cls.__new__(cls)
        
        return cls._instance

    @classmethod
    def _check_scrapper_type(cls, config:dict) -> tuple:

        # On vérifie que le type de scrapper est bien renseigné.
        if "scrapper" not in config.keys() or config["scrapper"] not in cls.ALLOWED_SCRAPPERS:
            return False, f"le champ 'scrapper' est absent du fichier de config ou n'est pas dans {cls.ALLOWED_SCRAPPERS}"

        return True, ""

    @classmethod
    def _check_keys(cls, config:dict) -> tuple:
        
        # On contrôle que toutes les clés sont bien présentes dans le fichier.
        test = [ key in config.keys() for key in cls.EXPECTED_KEYS[config["scrapper"]] ]

        if not all(test) :
            return False, f"les champs pour le scrapper {config['scrapper']} doivent contenir {cls.EXPECTED_KEYS[config['scrapper']]}"
        
        test = [ x in config[field].keys()
            for x in ["from", "to"]
            for field in ["year", "month"]
        ]

        # Pour year et month, on vérifie qu'ils contiennent bien leurs 2 clés
        if not all(test):
            return False, "les champs 'year' et 'month' doivent contenir contenir 'from' et 'to'"

        return True, ""

    @staticmethod
    def _check_year_month(config):

        # On vérifie que les valeurs dans year et month sont bien des entiers positifs
        test = [
            
            (isinstance(y, int) and y > 0) and (isinstance(m, int) and m > 0 )
            
            for y,m in zip(
                config["year"].values(),
                config["month"].values()
            )
        ]

        if not all(test):
            return False, "les champs 'from' et 'to' de 'year' et 'month' doivent être des entiers positifs"

        # On vérifie que les dates de départ et de fin sont dans le bon ordre
        for timescale in ["month", "year"]:
            
            mini = config[timescale]["from"]
            maxi = config[timescale]["to"]

            if mini > maxi:
                return False, f"{timescale} : 'from' doit être inférieur à 'to'"
            
            if timescale == "month" and (mini < 1 or maxi > 12):
                return False, "les champs 'from' et 'to' du mois doivent être compris entre 1 et 12"

        return True, ""
    
    @classmethod      
    def check(cls, config):

        for func in [cls._check_scrapper_type, cls._check_keys, cls._check_year_month]:

            is_correct, error = func(config)
            
            if not is_correct:
                return is_correct, error

        return True, ""

class Runner:

    WORKDIR = os.getcwd()

    # Emplacements des répertoires d'intérêt.
    PATHS = {
        "config": os.path.join(WORKDIR, "config"),
        "results": os.path.join(WORKDIR, "results"),
        "errors": os.path.join(WORKDIR, "errors")
    }

    SCRAPPERS = {
        "ogimet": OgimetScrapper,
        "wunderground": WundergroundScrapper
    }

    CHECKER = ConfigFilesChecker.instance()

    JOB_ID = 0

    @classmethod
    def _get_config_files(cls):

        # On établit la liste des fichiers de configuration à traiter.
        # Ils doivent se trouver dans le répertoire config, commencer par config
        # et avoir l'extension .json .
        try:
            config_files = [
                os.path.join(cls.PATHS["config"], filename)
                for filename in os.listdir(cls.PATHS["config"])
                if filename.startswith("config") and filename.endswith(".json")
            ]
        except FileNotFoundError:
            config_files = []
        
        return config_files

    @classmethod
    def _save_data(cls, data, config):

        if len(data) == 0:
            print("no data")
            return
        
        path_res = os.path.join(cls.PATHS["results"], f"{config['city']}_{config['scrapper']}_{cls.JOB_ID}.csv")
        to_csv(data, path_res)    
    
    @classmethod
    def _save_errors(cls, errors, config):
        
        if len(errors) == 0:
            return

        path_err = os.path.join(cls.PATHS["errors"], f"{config['city']}_{config['scrapper']}_{cls.JOB_ID}_errors.json")
        to_json(errors, path_err)

    @classmethod
    def run(cls):
        
        config_files = cls._get_config_files()
        
        if len(config_files) == 0:
            print(f"\n aucun répertoire 'config' trouvé dans {cls.WORKDIR} ou aucun fichier de config dans {cls.PATHS['config']} \n")
            return

        for filename in config_files:

            print("\n" + filename)
            
            cls.JOB_ID += 1
            config = from_json(filename)
            
            is_correct, error = cls.CHECKER.check(config)

            if not is_correct:
                print(error)
                continue
            
            scrapper = cls.SCRAPPERS[config["scrapper"]](config)
            data = scrapper.get_data()
            
            cls._save_data(data, config)
            cls._save_errors(scrapper.errors, config)

            print("\n")
