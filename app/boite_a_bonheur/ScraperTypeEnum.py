class ScrapperTypeEnumMember:

    def __init__(self, numero: int):
        self.numero = numero

    def __eq__(self, other):
        return self.numero == other.numero

    def __hash__(self):
        return hash(self.numero)

    def __repr__(self):
        return str(self.numero)


class ScrapperType:

    METEOCIEL = ScrapperTypeEnumMember(0)
    METEOCIEL_DAILY = ScrapperTypeEnumMember(1)
    METEOCIEL_HOURLY = ScrapperTypeEnumMember(2)

    OGIMET = ScrapperTypeEnumMember(3)
    OGIMET_DAILY = ScrapperTypeEnumMember(4)
    OGIMET_HOURLY = ScrapperTypeEnumMember(5)

    WUNDERGROUND = ScrapperTypeEnumMember(6)
    WUNDERGROUND_DAILY = ScrapperTypeEnumMember(7)
    WUNDERGROUND_HOURLY = ScrapperTypeEnumMember(9)

    @classmethod
    def values(cls):
        return [cls.METEOCIEL,
                cls.METEOCIEL_HOURLY,
                cls.METEOCIEL_DAILY,
                cls.OGIMET,
                cls.OGIMET_HOURLY,
                cls.OGIMET_DAILY,
                cls.WUNDERGROUND,
                cls.WUNDERGROUND_HOURLY,
                cls.WUNDERGROUND_DAILY]

    @classmethod
    def hourly_scrapper_types(cls) -> list[ScrapperTypeEnumMember]:
        return [cls.METEOCIEL_HOURLY,
                cls.OGIMET_HOURLY,
                cls.WUNDERGROUND_HOURLY]

    @classmethod
    def daily_scrapper_types(cls) -> list[ScrapperTypeEnumMember]:
        return [cls.METEOCIEL_DAILY,
                cls.OGIMET_DAILY,
                cls.WUNDERGROUND_DAILY]

    @classmethod
    def generic_scrapper_types(cls) -> list[ScrapperTypeEnumMember]:
        return [cls.METEOCIEL,
                cls.OGIMET,
                cls.WUNDERGROUND]
