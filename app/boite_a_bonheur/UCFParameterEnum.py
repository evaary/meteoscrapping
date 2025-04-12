from multiprocessing import cpu_count
from typing import List, Dict


class UCFParameterEnumMember:
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
        return f"<UCFParameterEnumMember {self._json_name} {self._field_name}>"

    def __eq__(self, other):
        if other is None or not isinstance(other, UCFParameterEnumMember):
            return False

        if self._json_name != other._json_name:
            return False

        if self._field_name != other._field_name:
            return False

        return True


class UCFParameter:

    UCF = UCFParameterEnumMember("config.json", "")

    GENERAL_PARAMETERS = UCFParameterEnumMember("parametres_generaux", "")
    PARALLELISM = UCFParameterEnumMember("parallelisme", "_should_download_in_parallel")
    CPUS = UCFParameterEnumMember("cpus", "_cpus")

    OGIMET = UCFParameterEnumMember("ogimet", "_ogimet_ucs")
    IND = UCFParameterEnumMember("ind", "_ind")

    METEOCIEL = UCFParameterEnumMember("meteociel", "_meteociel_ucs")
    CODE = UCFParameterEnumMember("code", "_code")

    WUNDERGROUND = UCFParameterEnumMember("wunderground", "_wunderground_ucs")
    COUNTRY_CODE = UCFParameterEnumMember("code_pays", "_country_code")
    REGION = UCFParameterEnumMember("region", "_region")

    DATES = UCFParameterEnumMember("dates", "_dates")
    CITY = UCFParameterEnumMember("ville", "_city")

    GENERAL_PARAMETERS_FIELDS : List[UCFParameterEnumMember] = [PARALLELISM, CPUS]

    SPECIFIC_FIELDS : Dict[UCFParameterEnumMember, List[UCFParameterEnumMember]] = {WUNDERGROUND: [REGION, COUNTRY_CODE],
                                                                                    METEOCIEL: [CODE],
                                                                                    OGIMET: [IND]}
    COMMON_FIELDS : List[UCFParameterEnumMember]  = [CITY]
    SCRAPPERS : List[UCFParameterEnumMember]  = [METEOCIEL,
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
