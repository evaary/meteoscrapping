class ScrapperTypeEnumMember:

    def __init__(self, numero: int, name: str):
        self.numero = numero
        self.name = name

    def __eq__(self, other):
        return self.numero == other.numero

    def __hash__(self):
        return hash(self.numero) + hash(self.name)

    def __repr__(self):
        return str(self.name)


class ScrapperType:

    METEOCIEL = ScrapperTypeEnumMember(0, "meteociel")
    METEOCIEL_DAILY = ScrapperTypeEnumMember(1, "meteociel_jour")
    METEOCIEL_HOURLY = ScrapperTypeEnumMember(2, "meteociel_heure")

    OGIMET = ScrapperTypeEnumMember(3, "ogimet")
    OGIMET_DAILY = ScrapperTypeEnumMember(4, "ogimet_jour")
    OGIMET_HOURLY = ScrapperTypeEnumMember(5, "ogimet_heure")

    WUNDERGROUND = ScrapperTypeEnumMember(6, "wunderground")
    WUNDERGROUND_DAILY = ScrapperTypeEnumMember(7, "wunderground_jour")
    WUNDERGROUND_HOURLY = ScrapperTypeEnumMember(9, "wunderground_heure")

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
