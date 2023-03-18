from app.checkers.exceptions import (NoDictException,
                                     UnknownKeysException,
                                     UnknownOrMissingParametersException,
                                     WaitingException,
                                     DatesException,
                                     MonthsException,
                                     DaysException,
                                     OtherFieldsException)

class ConfigFilesChecker:

    """Singleton contrôlant la validité d'un fichier de config."""

    EXPECTED_SCRAPPERS = {
        "wunderground": {"country_code", "city", "region", "year", "month"},
        "ogimet": {"ind", "city", "year", "month"},
        "meteociel": {"city", "year", "month", "code_num", "code"},
        "meteociel_daily": {"city", "year", "month", "day", "code_num", "code"}
    }

    MAIN_FIELDS = {"wunderground", "ogimet", "meteociel", "meteociel_daily", "waiting"}

    _instance = None

    def __init__(self) -> None:
        raise RuntimeError(f"use {self.__class__.__name__}.instance() instead")

    @classmethod
    def instance(cls):

        if cls._instance is not None:
            return cls._instance

        cls._instance = cls.__new__(cls)

        return cls._instance

    def _check_data_type(self, config) -> None:
        if not isinstance(config, dict):
            raise NoDictException()

    def _check_main_fields(self, config: dict) -> None:
        is_legal = set(config.keys()).issubset(self.MAIN_FIELDS)
        # On vérifie que les clés du dict sont correctes.
        if not is_legal:
            raise UnknownKeysException()

    def _check_keys(self, config: "dict[dict]") -> None:

        for x in config.keys():

            if x == "waiting":
                continue
            # on vérifie que les clés des dictionnaires correspondent aux paramètres attendus pour chaque scrapper
            is_legal = all([ set(dico.keys()) == self.EXPECTED_SCRAPPERS[x] for dico in config[x] ])

            if not is_legal:
                raise UnknownOrMissingParametersException()

    def _check_values(self, config: dict) -> None:

        # (1) On vérifie que le champs waiting est un entier positif puis on passe aux scrapper
        # (2) On récupère tous les jobs associés à 1 scrapper
        # (3) On vérifie que les champs year, month et day sont des listes d'1 à 2 entiers positifs ordonnés
        # (4) On vérifie que les mois sont dans l'intervalle [1,12]
        # (5) On vérifie que les jours sont l'intervalle [1,31]
        # (6) On vérifie que tous les autres champs sont des str

        for scrapper in config.keys():
            # (1)
            if (    scrapper == "waiting"
                and (not isinstance(config[scrapper], int) or config[scrapper] < 0 ) ):
                raise WaitingException()

            if scrapper == "waiting":
                continue
            # (2)
            dicos = config[scrapper]
            # (3)
            for x in ("year", "month", "day"):

                try:

                    is_list = all( [ isinstance(dico[x], list) and len(dico[x]) in (1,2) for dico in dicos ] )
                    if not is_list:
                        raise DatesException()

                    are_positive_ints = all( [ isinstance(y, int) and y > 0 for dico in dicos for y in dico[x] ] )
                    if not are_positive_ints:
                        raise DatesException()

                    are_ordered = all( [ dico[x][0] <= dico[x][-1] for dico in dicos ] )
                    if not are_ordered:
                        raise DatesException()
                # si la clé "day" n'existe pas dans les jobs
                except KeyError:
                    continue
            # (4)
            if not all([    dico["month"][0] in range(1,13)
                        and dico["month"][-1] in range(1,13) for dico in dicos]):
                raise MonthsException()
            # (5)
            try:
                if not all([    dico["day"][0] in range(1,32)
                            and dico["day"][-1] in range(1,32) for dico in dicos]):
                    raise DaysException()
            # si la clé "day" n'existe pas dans les jobs
            except KeyError:
                pass
            # (6)
            todo = {field for field in self.EXPECTED_SCRAPPERS[scrapper] if field not in ("year", "month", "day")}

            if not all( [ isinstance(dico[field], str) for dico in dicos for field in todo ] ):
                raise OtherFieldsException()

    def check(self, config: dict) -> None:
        self._check_data_type(config)
        self._check_main_fields(config)
        self._check_keys(config)
        self._check_values(config)
