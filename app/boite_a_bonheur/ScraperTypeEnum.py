class ScrapperTypeEnumMember:

    ENUM_INSTANCES_COUNTER = 0

    def __init__(self):
        self.id = self.ENUM_INSTANCES_COUNTER
        self.ENUM_INSTANCES_COUNTER += 1

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return str(self.id)


class ScrapperType:

    METEOCIEL = ScrapperTypeEnumMember()
    METEOCIEL_DAILY = ScrapperTypeEnumMember()
    METEOCIEL_HOURLY = ScrapperTypeEnumMember()

    OGIMET = ScrapperTypeEnumMember()
    OGIMET_DAILY = ScrapperTypeEnumMember()
    OGIMET_HOURLY = ScrapperTypeEnumMember()

    WUNDERGROUND = ScrapperTypeEnumMember()
    WUNDERGROUND_DAILY = ScrapperTypeEnumMember()
    WUNDERGROUND_HOURLY = ScrapperTypeEnumMember()

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
