from multiprocessing import cpu_count
from typing import List, Dict


class UCFParameter:
    def __init__(self, json_name: str, field_name: str):
        self._json_name = json_name
        self._field_name = field_name

    @property
    def json_name(self):
        return self._json_name

    @property
    def field_name(self):
        return self._field_name

    def __hash__(self):
        return hash(self._json_name) + hash(self._field_name)

    def __repr__(self):
        return f"<UCFParameter {self._json_name} {self._field_name}>"

    def __eq__(self, other):
        if other is None or not isinstance(other, UCFParameter):
            return False

        if self._json_name != other._json_name:
            return False

        if self._field_name != other._field_name:
            return False

        return True


class UCFParameters:

    UCF = UCFParameter("config.json", "")

    GENERAL_PARAMETERS = UCFParameter("parametres_generaux", "")
    PARALLELISM = UCFParameter("parallelisme", "_should_download_in_parallel")
    CPUS = UCFParameter("cpus", "_cpus")

    OGIMET = UCFParameter("ogimet", "_ogimet_ucs")
    IND = UCFParameter("ind", "_ind")

    METEOCIEL = UCFParameter("meteociel", "_meteociel_ucs")
    CODE = UCFParameter("code", "_code")

    WUNDERGROUND = UCFParameter("wunderground", "_wunderground_ucs")
    COUNTRY_CODE = UCFParameter("code_pays", "_country_code")
    REGION = UCFParameter("region", "_region")

    DATES = UCFParameter("dates", "_dates")
    CITY = UCFParameter("ville", "_city")

    GENERAL_PARAMETERS_FIELDS : List[UCFParameter] = [PARALLELISM, CPUS]

    SPECIFIC_FIELDS : Dict[UCFParameter, List[UCFParameter]] = {WUNDERGROUND: [REGION, COUNTRY_CODE],
                                                                METEOCIEL: [CODE],
                                                                OGIMET: [IND]}
    COMMON_FIELDS : List[UCFParameter]  = [CITY]
    SCRAPPERS : List[UCFParameter]  = [ METEOCIEL,
                                        OGIMET,
                                        WUNDERGROUND]
    # valeurs par défaut
    DEFAULT_WAITING = 2
    DEFAULT_PARALLELISM = True
    MAX_CPUS = cpu_count()
    DEFAULT_CPUS = MAX_CPUS
    MIN_MONTHS_DAYS_VALUE = 1
    MAX_DATE_FIELD_SIZE = 2
    MIN_YEARS = 1800
    MAX_MONTHS = 12
    MAX_DAYS = 31
