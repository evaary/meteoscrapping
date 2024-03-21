class UCFParameterEnumMember:
    def __init__(self, name: str):
        self.name = name


class UCFParameter:

    UCF = UCFParameterEnumMember("config.json")
    GENERAL_PARAMETERS = UCFParameterEnumMember("parametres_generaux")
    WAITING = UCFParameterEnumMember("delaiJS")
    OGIMET = UCFParameterEnumMember("ogimet")
    METEOCIEL = UCFParameterEnumMember("meteociel")
    WUNDERGROUND = UCFParameterEnumMember("wunderground")
    YEARS = UCFParameterEnumMember("annees")
    MONTHS = UCFParameterEnumMember("mois")
    DAYS = UCFParameterEnumMember("jours")
    CITY = UCFParameterEnumMember("ville")
    CODE = UCFParameterEnumMember("code")
    CODE_NUM = UCFParameterEnumMember("code_num")
    IND = UCFParameterEnumMember("ind")
    REGION = UCFParameterEnumMember("region")
    COUNTRY_CODE = UCFParameterEnumMember("code_pays")

    MAX_WAITING = 5
    MIN_WAITING = 1
    MIN_MONTHS_DAYS_VALUE = 1
    MIN_YEARS_VALUE = 1800
    MAX_DATE_FIELD_SIZE = 2
    MAX_MONTHS_VALUE = 12
    MAX_DAYS_VALUE = 31

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
