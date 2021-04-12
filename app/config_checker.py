'''
Une classe pour vérifier que le fichier de configuration
contient toutes les infos pour faire tourner les scrappers.
Si ce n'est pas le cas, la variable conform devient fausse.
'''
class ConfigFilesChecker:
    def __init__(self, config):
        self._config = config
        # on suppose le fichier de configuration conforme
        self._conform = True

    def _check_keys(self):
        ''' Vérifie la présence de tous les paramètres nécessaires.
        (1) On établit la liste de paramètres nécessaires (expected_keys) en fonction du scrapper.
        (2) On vérifie que chacun d'eux se trouve bien dans la config fournie.
        Si l'un des paramètres manque, on déclare le fichier config non conforme.
        (3) On vérifie que les champs year et month sont des dicts avec les bonnes clés
        '''
        # (1)
        expected_keys = {
            "wunderground": ["scrapper", "country_code", "city", "region", "waiting", "year", "month"],
            "ogimet": ["scrapper", "ind", "city", "waiting", "year", "month"]
        }
        # (2)
        try:
            test = [key in self._config.keys() for key in expected_keys[self._config["scrapper"]]]

            if not all(test) :
                print("missing value in config file")
                self._conform = False
                return

        except KeyError:
            print("wrong scrapper or no scrapper given in config file, must be wunderground or ogimet")
            self._conform = False
            return
        # (3)
        try:
            test = [x in self._config[field].keys()
                for x in ["from_", "to_"]
                for field in ["year", "month"]
            ]

            if not all(test):
                print("year and month must be dicts : {'from_': <int>, 'to_': <int>}")
                self._conform = False
                return
        
        except KeyError:
            print("year and month must be dicts : {'from_': <int>, 'to_': <int>}")
            self._conform = False
            return

    def _check_year_month(self):
        ''' Vérifie que les mois et les années sont cohérents.
        (1) Les années et mois doivent être des nombres > 0.
        (2) L'année / mois initial doit être inférieur ou égal à l'année / mois final, et doivent être des int.
        (3) Les mois doivent être compris entre 1 et 12.
        '''
        # (1)
        try:
            test = [
                y > 0 and m > 0 
                for y,m in zip(
                    self._config["year"].values(),
                    self._config["month"].values()
                )
            ]

            if not all(test):
                print("negative values detected in year and/or months dicts")
                self._conform = False
                return
        except TypeError:
            print("year and/or month dicts values must be numbers in config file")
            self._conform = False
            return

        # (2)
        for timescale in ["month", "year"]:
            mini = self._config[timescale]["from_"]
            maxi = self._config[timescale]["to_"]

            if not isinstance(mini, int) or not isinstance(maxi, int):
                print(f"{timescale} from_ and to_ must be int")
                self._conform = False
                return

            if mini > maxi:
                print(f"wrong {timescale} order")
                self._conform = False
                return
        # (3)
        if timescale == "month" and (mini < 1 or maxi > 12):
            print(f"month must be integers from 1 to 12 included")
            self._conform = False
            return
            
    def check(self):
        self._check_keys()
        self._check_year_month()

        return self._conform