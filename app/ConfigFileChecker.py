class ConfigCheckerException(Exception):
    pass


class ConfigFilesChecker:

    '''Singleton contrôlant la validité d'un fichier de config.'''

    EXPECTED_SCRAPPERS = {
        "wunderground": {"country_code", "city", "region", "year", "month"},
        "ogimet": {"ind", "city", "year", "month"},
        "meteociel": {"city", "year", "month", "code_num", "code"},
        "meteociel_daily": {"city", "year", "month", "day", "code_num", "code"}
    }

    ERRORS_MSG = {
        "main_fields": "ERREUR : vérifiez les champ principaux",
        "configs": "ERREUR : vérifiez les paramètres des configs",
        "waiting": "ERREUR : waiting doit être un entier",
        "dates": "ERREUR : year, month et day doivent être des listes de 1 ou 2 entiers positifs ordonnés",
        "month": "ERREUR : month doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 12",
        "day": "ERREUR : day doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 31",
        "other": "ERREUR : les champs autres que year, month et day doivent être des strings"
    }

    _instance = None

    def __init__(self) -> None:
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):

        if cls._instance is not None:
            return cls._instance

        cls._instance = cls.__new__(cls)

        return cls._instance

    def _check_main_fields(self, config: dict) -> None:
        # un fichier de config contient le champs waiting, il est légal, mais n'est pas
        # un scrapper et donc pas présent dans EXPECTED_SCRAPPERS. On le rajoute.
        reference = set(self.EXPECTED_SCRAPPERS.keys()).union({"waiting"})
        is_legal = set(config.keys()) == reference
        # On vérifie que les clés du dict sont correctes.
        if not is_legal:
            raise ConfigCheckerException(self.ERRORS_MSG["main_fields"])

    def _check_keys(self, config: "dict[dict]") -> None:

        for x in config.keys():

            if x == "waiting":
                continue
            # on vérifie que les clés des dictionnaires correspondent aux paramètres attendus pour chaque scrapper
            is_legal = all([ set(dico.keys()) == self.EXPECTED_SCRAPPERS[x] for dico in config[x] ])

            if not is_legal:
                raise ConfigCheckerException(self.ERRORS_MSG["configs"])

    def _check_values(self, config: dict) -> None:

        for scrapper in config.keys():

            if scrapper == "waiting" and not isinstance(config[scrapper], int):
                raise ConfigCheckerException(self.ERRORS_MSG["waiting"])

            if scrapper == "waiting":
                continue

            dicos = config[scrapper]

            for x in ("year", "month", "day"):

                try:

                    is_list = all( [ isinstance(dico[x], list) and len(dico[x]) in (1,2) for dico in dicos ] )
                    if not is_list:
                        raise ConfigCheckerException(self.ERRORS_MSG["dates"])

                    are_positive_ints = all( [ isinstance(y, int) and y > 0 for dico in dicos for y in dico[x] ] )
                    if not are_positive_ints:
                        raise ConfigCheckerException(self.ERRORS_MSG["dates"])

                    are_ordered = all( [ dico[x][0] <= dico[x][-1] for dico in dicos ] )
                    if not are_ordered:
                        raise ConfigCheckerException(self.ERRORS_MSG["dates"])

                except KeyError:
                    continue

            if not all([    dico["month"][0] in range(1,13)
                        and dico["month"][-1] in range(1,13) for dico in dicos]):
                raise ConfigCheckerException(self.ERRORS_MSG["month"])

            try:
                if not all([    dico["day"][0] in range(1,32)
                            and dico["day"][-1] in range(1,32) for dico in dicos]):
                    raise ConfigCheckerException(self.ERRORS_MSG["day"])
            except KeyError:
                pass

            todo = {field for field in self.EXPECTED_SCRAPPERS[scrapper] if field not in ("year", "month", "day")}

            if not all( [ isinstance(dico[field], str) for dico in dicos for field in todo ] ):
                raise ConfigCheckerException(self.ERRORS_MSG["other"])

    def check(self, config: dict) -> None:
        self._check_main_fields(config)
        self._check_keys(config)
        self._check_values(config)
