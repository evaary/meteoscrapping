class UCFParameter:

    class __UCFParameterEnumMember:
        def __init__(self, name: str):
            self.name = name

    UCF = __UCFParameterEnumMember("config.json")
    GENERAL_PARAMETERS = __UCFParameterEnumMember("parametres_generaux")
    WAITING = __UCFParameterEnumMember("delaiJS")
    OGIMET = __UCFParameterEnumMember("ogimet")
    METEOCIEL = __UCFParameterEnumMember("meteociel")
    WUNDERGROUND = __UCFParameterEnumMember("wunderground")
    YEARS = __UCFParameterEnumMember("annees")
    MONTHS = __UCFParameterEnumMember("mois")
    DAYS = __UCFParameterEnumMember("jours")
    CITY = __UCFParameterEnumMember("ville")
    CODE = __UCFParameterEnumMember("code")
    CODE_NUM = __UCFParameterEnumMember("code_num")
    IND = __UCFParameterEnumMember("ind")
    REGION = __UCFParameterEnumMember("region")
    COUNTRY_CODE = __UCFParameterEnumMember("code_pays")

    MAX_WAITING = 5
    MIN_WAITING = 1
    MIN_MONTHS_DAYS_VALUE = 1
    MIN_YEARS_VALUE = 1800
    MAX_DATE_FIELD_SIZE = 2
    MAX_MONTHS_VALUE = 12
    MAX_DAYS_VALUE = 31
