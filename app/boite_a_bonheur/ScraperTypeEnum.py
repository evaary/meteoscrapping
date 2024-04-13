from typing import List


class ScrapperTypeEnumMember:

    def __init__(self, numero: int, name: str):
        self._numero = numero
        self._name = name

    @property
    def numero(self):
        return self._numero

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        if other is None or not isinstance(other, ScrapperTypeEnumMember):
            return False

        return self.numero == other.numero

    def __hash__(self):
        return hash(self._numero) + hash(self._name)

    def __repr__(self):
        return str(self._name)

    def __copy__(self):
        return ScrapperTypeEnumMember(self._numero, self._name)


class ScrapperType:

    METEOCIEL_DAILY = ScrapperTypeEnumMember(1, "meteociel_jour")
    METEOCIEL_HOURLY = ScrapperTypeEnumMember(2, "meteociel_heure")

    OGIMET_DAILY = ScrapperTypeEnumMember(4, "ogimet_jour")
    OGIMET_HOURLY = ScrapperTypeEnumMember(5, "ogimet_heure")

    WUNDERGROUND_DAILY = ScrapperTypeEnumMember(7, "wunderground_jour")
    WUNDERGROUND_HOURLY = ScrapperTypeEnumMember(9, "wunderground_heure")

    @classmethod
    def values(cls):
        return [cls.METEOCIEL_HOURLY,
                cls.METEOCIEL_DAILY,
                cls.OGIMET_HOURLY,
                cls.OGIMET_DAILY,
                cls.WUNDERGROUND_HOURLY,
                cls.WUNDERGROUND_DAILY]

    @classmethod
    def hourly_scrappers(cls) -> List[ScrapperTypeEnumMember]:
        return [cls.METEOCIEL_HOURLY,
                cls.OGIMET_HOURLY,
                cls.WUNDERGROUND_HOURLY]

    @classmethod
    def daily_scrappers(cls) -> List[ScrapperTypeEnumMember]:
        return [cls.METEOCIEL_DAILY,
                cls.OGIMET_DAILY,
                cls.WUNDERGROUND_DAILY]

    @classmethod
    def ogimet_scrappers(cls):
        return [cls.OGIMET_HOURLY,
                cls.OGIMET_DAILY]

    @classmethod
    def meteociel_scrappers(cls):
        return [cls.METEOCIEL_HOURLY,
                cls.METEOCIEL_DAILY]

    @classmethod
    def wunderground_scrappers(cls):
        return [cls.WUNDERGROUND_HOURLY,
                cls.WUNDERGROUND_DAILY]
