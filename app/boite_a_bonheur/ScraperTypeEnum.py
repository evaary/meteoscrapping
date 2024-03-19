


class ScrapperType:

    class __ScrapperTypeEnumMember:
        pass

    METEOCIEL = __ScrapperTypeEnumMember()
    METEOCIEL_DAILY = __ScrapperTypeEnumMember()
    METEOCIEL_HOURLY = __ScrapperTypeEnumMember()

    OGIMET = __ScrapperTypeEnumMember()
    OGIMET_DAILY = __ScrapperTypeEnumMember()
    OGIMET_HOURLY = __ScrapperTypeEnumMember()

    WUNDERGROUND = __ScrapperTypeEnumMember()
    WUNDERGROUND_DAILY = __ScrapperTypeEnumMember()
    WUNDERGROUND_HOURLY = __ScrapperTypeEnumMember()

    @classmethod
    def hourly_scrapper_types(cls) -> list[__ScrapperTypeEnumMember]:
        return [cls.METEOCIEL_HOURLY,
                cls.OGIMET_HOURLY,
                cls.WUNDERGROUND_HOURLY]

    @classmethod
    def daily_scrapper_types(cls) -> list[__ScrapperTypeEnumMember]:
        return [cls.METEOCIEL_DAILY,
                cls.OGIMET_DAILY,
                cls.WUNDERGROUND_DAILY]

    @classmethod
    def generic_scrapper_types(cls) -> list[__ScrapperTypeEnumMember]:
        return [cls.METEOCIEL,
                cls.OGIMET,
                cls.WUNDERGROUND]
