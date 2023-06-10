from app.checkers.exceptions import (DatesException, DaysException,
                                     MonthsException, NoDictException,
                                     OtherFieldsException,
                                     UnknownKeysException,
                                     UnknownOrMissingParametersException,
                                     WaitingException)


class ConfigFilesChecker:

    """Singleton contrôlant la validité d'un fichier de config."""

    EXPECTED_SCRAPPERS = { "wunderground": {"country_code",
                                            "city",
                                            "region",
                                            "year",
                                            "month"},

                            "ogimet": { "ind",
                                        "city",
                                        "year",
                                        "month" },

                            "meteociel": {  "city",
                                            "year",
                                            "month",
                                            "code_num",
                                            "code" },

                            "meteociel_daily": {"city",
                                                "year",
                                                "month",
                                                "day",
                                                "code_num",
                                                "code"} }

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
        # un fichier de config contient le champs waiting, il est légal, mais n'est pas
        # un scrapper et donc pas présent dans EXPECTED_SCRAPPERS. On le rajoute.
        reference = set(self.EXPECTED_SCRAPPERS.keys()).union({"waiting"})
        # On vérifie que les clés du dict sont correctes.
        is_legal = set(config.keys()).issubset(reference)
        if not is_legal:
            raise UnknownKeysException()

    def _check_keys(self, config: "dict[dict]") -> None:

        # on vérifie que les clés des dictionnaires correspondent aux paramètres attendus pour chaque scrapper
        is_legal = all( [ set(scrapper_config.keys()) == self.EXPECTED_SCRAPPERS[scrapper]
                          for scrapper in config.keys() if scrapper != "waiting"
                          for scrapper_config in config[scrapper] ] )

        if not is_legal:
                raise UnknownOrMissingParametersException()

    def _check_waiting(self, config) -> None:

        try:
            waiting = config["waiting"]
        except KeyError:
            return

        if (   not isinstance(waiting, int)
            or waiting < 0 ):
            raise WaitingException()

    def _check_years_months_days(self, config) -> None:

        # les champs year, month et day de chaque config de chaque scrapper doivent être des listes d'1 ou 2 entiers positifs ordonnés
        is_legal = all( [ self._is_list_of_max_2_positive_ordered_ints_(scrapper_config[time_unit])

                          for scrapper in config.keys() if scrapper != "waiting"
                          for scrapper_config in config[scrapper]
                          for time_unit in [ key for key in scrapper_config.keys() if key in ("year", "month", "day") ] ] )
        if not is_legal:
            raise DatesException()

    def _check_months(self, config) -> None:

        # les champs month de chaque config de chaque scrapper doivent être de valeur max 12
        is_legal = all( [ max(scrapper_config["month"]) <= 12

                          for scrapper in config.keys() if scrapper != "waiting"
                          for scrapper_config in config[scrapper] ] )
        if not is_legal:
            raise MonthsException()

    def _check_days(self, config) -> None:

        # les champs day de chaque config du scrapper meteociel_daily doivent être de valeur max 31
        try:

            is_legal = all( [ max(scrapper_config["day"]) <= 31
                              for scrapper_config in config["meteociel_daily"] ] )
            if not is_legal:
                raise DaysException()

        except KeyError:
            pass

    def _check_other_fields(self, config: dict) -> None:

        # les champs autres que les dates de chaque config de chaque scrapper doivent être des str
        is_legal = all( [ isinstance(scrapper_config[key], str)

                          for scrapper in config.keys() if scrapper != "waiting"
                          for scrapper_config in config[scrapper]
                          for key in [ key for key in scrapper_config.keys() if key not in ("year", "month", "day") ] ] )
        if not is_legal:
            raise OtherFieldsException()

    def _is_list_of_max_2_positive_ordered_ints_(self, data) -> bool:

        is_legal = True

        if(    not isinstance(data, list)
            or not len(data) in (1,2)
            or not all( [ isinstance(x, int) and x > 0 for x in data ] )
            or data[-1] < data[0] ):

            is_legal = False

        return is_legal

    def check(self, config: dict) -> None:
        self._check_data_type(config)
        self._check_main_fields(config)
        self._check_keys(config)
        self._check_waiting(config)
        self._check_years_months_days(config)
        self._check_months(config)
        self._check_days(config)
        self._check_other_fields(config)
