class ConfigFilesChecker:

    '''Singleton contrôlant la validité d'un fichier de config.'''
    
    EXPECTED_SCRAPPERS = {
        "wunderground": {"country_code", "city", "region", "year", "month"},
        "ogimet": {"ind", "city", "year", "month"},
        "meteociel": {"city", "year", "month", "code_num", "code"},
        "meteociel_daily": {"city", "year", "month", "day", "code_num", "code"}
    }

    ERRORS = {
        "main_fields": "les champ principaux doivent être ",
        "waiting": "waiting doit être un entier",
        "dates": "year et month doivent être des listes de 1 ou 2 entiers positifs ordonnés",
        "month": "month doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 12",
        "day": "day doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 31",
        "other": "les champs autres que year, month et day doivent être des strings"
    }

    _instance = None
    
    def __init__(self):
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):

        if cls._instance is not None:
            return cls._instance

        cls._instance = cls.__new__(cls)
        cls._instance.is_legal = True
        cls._instance.error = "initial status"

        return cls._instance 
    
    def _check_main_fields(self, config:dict):
        # un fichier de config contient le champs waiting, il est légal, mais n'est pas
        # un scrapper et donc pas présent dans EXPECTED_SCRAPPERS. On le rajoute.
        reference = set(self.EXPECTED_SCRAPPERS.keys()).union({"waiting"})
        test = set(config.keys()) == reference
        # On vérifie que les clés du dict sont correctes.
        if not test:
            self.is_legal = False
            self.error = f"{self.ERRORS['main_fields']} {reference}"

    def _check_keys(self, config:dict):
        
        # On contrôle que toutes les clés des configs correspondent à ce qu'on attend.
        for x in config.keys():
            
            if x == "waiting":
                continue
            
            test = all([ set(dico.keys()) == self.EXPECTED_SCRAPPERS[x] for dico in config[x] ])
            wrong_configs = [ dico for dico in config[x] if set(dico.keys()) != self.EXPECTED_SCRAPPERS[x] ]
            
            if not test:
                self.is_legal = False
                self.error = f"des configs {x} posent problème, {wrong_configs}"

    def _check_values(self, config):

        for scrapper in config.keys():

            if scrapper == "waiting" and not isinstance(config[scrapper], int):
                self.is_legal = False
                self.error = self.ERRORS["waiting"]
                return

            if scrapper == "waiting":
                continue
            
            dicos = config[scrapper]

            for x in ("year", "month", "day"):

                try:

                    is_list = all( [ isinstance(dico[x], list) and len(dico[x]) in (1,2) for dico in dicos] )
                    if not is_list:
                        self.is_legal = False
                        self.error = self.ERRORS["dates"]
                        return 

                    are_positive_ints = all( [ isinstance(y, int) and y > 0 for dico in dicos for y in dico[x] ] )
                    if not are_positive_ints:
                        self.is_legal = False
                        self.error = self.ERRORS["dates"]
                        return

                    are_ordered = all( [ dico[x][0] <= dico[x][-1] for dico in dicos ] )
                    if not are_ordered:
                        self.is_legal = False
                        self.error = self.ERRORS["dates"]
                        return

                except KeyError:
                    continue

            if not all([dico["month"][0] in range(1,13) and dico["month"][-1] in range(1,13) for dico in dicos]):
                self.is_legal = False
                self.error = self.ERRORS["month"]
                return

            try:
                if not all([dico["day"][0] in range(1,32) and dico["day"][-1] in range(1,32) for dico in dicos]):
                    self.is_legal = False
                    self.error = self.ERRORS["day"]
                    return
            except KeyError:
                pass

            todo = {field for field in self.EXPECTED_SCRAPPERS[scrapper] if field not in ("year", "month", "day")}
            
            if not all( [ isinstance(dico[field], str) for dico in dicos for field in todo ] ):
                self.is_legal = False
                self.error = self.ERRORS["other"]
    
    def run(self, config):

        for func in [self._check_main_fields, self._check_keys, self._check_values]:

            func(config)
            
            if not self.is_legal:
                return

    def __repr__(self):
        return f"<ConfigFilesChecker is_legal={self.is_legal} error='{self.error}'"
