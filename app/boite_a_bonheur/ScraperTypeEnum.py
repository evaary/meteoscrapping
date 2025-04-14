from typing import List


class ScrapperType:

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
        if other is None or not isinstance(other, ScrapperType):
            return False

        return self.numero == other.numero

    def __hash__(self):
        return hash(self._numero) + hash(self._name)

    def __repr__(self):
        return str(self._name)

    def __copy__(self):
        return ScrapperType(self._numero, self._name)


class ScrapperTypes:

    METEOCIEL_DAILY = ScrapperType(1, "meteociel_jour")
    METEOCIEL_HOURLY = ScrapperType(2, "meteociel_heure")

    OGIMET_DAILY = ScrapperType(4, "ogimet_jour")
    OGIMET_HOURLY = ScrapperType(5, "ogimet_heure")

    WUNDERGROUND_DAILY = ScrapperType(7, "wunderground_jour")
    WUNDERGROUND_HOURLY = ScrapperType(9, "wunderground_heure")

    @classmethod
    def values(cls)-> List[ScrapperType]:
        return [cls.METEOCIEL_HOURLY,
                cls.METEOCIEL_DAILY,
                cls.OGIMET_HOURLY,
                cls.OGIMET_DAILY,
                cls.WUNDERGROUND_HOURLY,
                cls.WUNDERGROUND_DAILY]

    @classmethod
    def hourly_scrappers(cls) -> List[ScrapperType]:
        return [cls.METEOCIEL_HOURLY,
                cls.OGIMET_HOURLY,
                cls.WUNDERGROUND_HOURLY]

    @classmethod
    def daily_scrappers(cls) -> List[ScrapperType]:
        return [cls.METEOCIEL_DAILY,
                cls.OGIMET_DAILY,
                cls.WUNDERGROUND_DAILY]

    @classmethod
    def ogimet_scrappers(cls)-> List[ScrapperType]:
        return [cls.OGIMET_HOURLY,
                cls.OGIMET_DAILY]

    @classmethod
    def meteociel_scrappers(cls)-> List[ScrapperType]:
        return [cls.METEOCIEL_HOURLY,
                cls.METEOCIEL_DAILY]

    @classmethod
    def wunderground_scrappers(cls)-> List[ScrapperType]:
        return [cls.WUNDERGROUND_HOURLY,
                cls.WUNDERGROUND_DAILY]
