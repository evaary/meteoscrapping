class ConfigFilesChecker:

    '''Singleton contrôlant la validité d'un fichier de config.'''
    
    EXPECTED_SCRAPPERS = {
        "wunderground": {"country_code", "city", "region", "year", "month"},
        "ogimet": {"ind", "city", "year", "month"},
        "meteociel": {"city", "year", "month", "code_num", "code"},
        "meteociel_daily": {"city", "year", "month", "day", "code_num", "code"}
    }

    _instance = None
    
    def __init__(self):
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):
        cls._instance = cls.__new__(cls) if cls._instance is None else cls._instance
        return cls._instance
    
    @classmethod
    def _check_scrapper_type(cls, config:dict) -> tuple:
        # un fichier de config contient le champs waiting, il est légal, mais n'est pas
        # un scrapper. On le rajoute.
        reference = set(cls.EXPECTED_SCRAPPERS.keys()).union({"waiting"})
        # On vérifie que les clés du dict sont correctes.
        if not set(config.keys()).issubset(reference):
            return False, f"les champ principaux doivent être {reference}"

        return True, ""

    @classmethod
    def _check_keys(cls, config:dict) -> tuple:
        
        # On contrôle que toutes les clés des configs correspondent à ce qu'on attend.
        for x in config.keys():
            
            if x == "waiting":
                continue
            
            test = [ set(dico.keys()) == cls.EXPECTED_SCRAPPERS[x] for dico in config[x] ]
            
            if not all(test):
                return False, f"une des config {x} pose problème"

        return True, ""

    @classmethod
    def _check_values(cls, config):

        for scrapper in config.keys():

            if scrapper == "waiting":
                continue
            
            dicos = config[scrapper]

            for x in ("year", "month", "day"):
                try:
                    isList = all( [ isinstance(dico[x], list) and len(dico[x]) in (1,2) for dico in dicos] )
                    if not isList:
                        return False, "year et month doivent être des listes de 1 ou 2 entiers positifs ordonnés"  

                    arePositiveInts = all( [ isinstance(y, int) and y > 0 for dico in dicos for y in dico[x] ] )
                    if not arePositiveInts:
                        return False, "year et month doivent être des listes de 1 ou 2 entiers positifs ordonnés"  

                    areOrdered = all( [ dico[x][0] <= dico[x][-1] for dico in dicos ] )
                    if not areOrdered:
                        return False, "year et month doivent être des listes de 1 ou 2 entiers positifs ordonnés"
                except KeyError:
                    continue

            if not all([dico["month"][0] in range(1,13) and dico["month"][-1] in range(1,13) for dico in dicos]):
                return False, "month doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 12"

            try:
                if not all([dico["day"][0] in range(1,32) and dico["day"][-1] in range(1,32) for dico in dicos]):
                    return False, "day doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 31"
            except KeyError:
                pass

            todo = {field for field in cls.EXPECTED_SCRAPPERS[scrapper] if field not in ("year", "month", "day")}
            
            if not all( [ isinstance(dico[field], str) for dico in dicos for field in todo ] ):
                return False, "les champs autres que year, month et day doivent être des strings"

        return True, ""
    
    @classmethod
    def check(cls, config):

        for func in [cls._check_scrapper_type, cls._check_keys, cls._check_values]:

            is_correct, error = func(config)
            
            if not is_correct:
                return is_correct, error

        return True, ""
