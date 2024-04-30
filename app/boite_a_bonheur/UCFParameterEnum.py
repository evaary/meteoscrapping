from multiprocessing import cpu_count
from typing import List


class UCFParameterEnumMember:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def __hash__(self):
        return hash(self._name)

    def __repr__(self):
        return self._name

    def __eq__(self, other):
        if other is None or not isinstance(other, UCFParameterEnumMember):
            return False
        return self._name == other.name


class UCFParameter:

    UCF = UCFParameterEnumMember("config.json")

    GENERAL_PARAMETERS = UCFParameterEnumMember("parametres_generaux")
    PARALLELISM = UCFParameterEnumMember("parallelisme")
    CPUS = UCFParameterEnumMember("cpus")

    OGIMET = UCFParameterEnumMember("ogimet")
    IND = UCFParameterEnumMember("ind")

    METEOCIEL = UCFParameterEnumMember("meteociel")
    CODE = UCFParameterEnumMember("code")

    WUNDERGROUND = UCFParameterEnumMember("wunderground")
    COUNTRY_CODE = UCFParameterEnumMember("code_pays")
    REGION = UCFParameterEnumMember("region")

    YEARS = UCFParameterEnumMember("annees")
    MONTHS = UCFParameterEnumMember("mois")
    DAYS = UCFParameterEnumMember("jours")
    CITY = UCFParameterEnumMember("ville")

    GENERAL_PARAMETERS_FIELDS = [PARALLELISM, CPUS]

    SPECIFIC_FIELDS = {
        WUNDERGROUND: [REGION, COUNTRY_CODE],
        METEOCIEL: [CODE],
        OGIMET: [IND]
    }

    COMMON_FIELDS = [CITY]
    DATE_FIELDS = [YEARS, MONTHS, DAYS]

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

    @classmethod
    def scrappers_parameters(cls):
        return [cls.METEOCIEL,
                cls.OGIMET,
                cls.WUNDERGROUND]

    @classmethod
    def dates_parameters(cls):
        return [cls.YEARS,
                cls.MONTHS,
                cls.DAYS]

    @classmethod
    def specific_fields_by_scrapper(cls, ucfparameter: UCFParameterEnumMember) -> "List[UCFParameterEnumMember]":
        return cls.SPECIFIC_FIELDS[ucfparameter]
