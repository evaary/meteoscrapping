from typing import List


class Month:
    def __init__(self,
                 numero: int,
                 ndays: int,
                 name: str):
        self._numero = numero
        self._ndays = ndays
        self._name = name

    @property
    def numero(self):
        return self._numero

    @property
    def ndays(self):
        return self._ndays

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        if other is None or not isinstance(other, Month):
            return False

        return self._numero == other.numero

    def __copy__(self):
        return Month(self._numero, self._ndays, self._name)

    def __repr__(self):
        return self._name


class Months:

    JANVIER = Month(1, 31, "JANVIER")
    FEVRIER = Month(2, 28, "FEVRIER")
    MARS = Month(3, 31, "MARS")
    AVRIL = Month(4, 30, "AVRIL")
    MAI = Month(5, 31, "MAI")
    JUIN = Month(6, 30, "JUIN")
    JUILLET = Month(7, 31, "JUILLET")
    AOUT = Month(8, 31, "AOUT")
    SEPTEMBRE = Month(9, 30, "SEPTEMBRE")
    OCTOBRE = Month(10, 31, "OCTOBRE")
    NOVEMBRE = Month(11, 30, "NOVEMBRE")
    DECEMBRE = Month(12, 31, "DECEMBRE")

    @classmethod
    def values(cls) -> List[Month]:
        return [cls.JANVIER,
                cls.FEVRIER,
                cls.MARS,
                cls.AVRIL,
                cls.MAI,
                cls.JUIN,
                cls.JUILLET,
                cls.AOUT,
                cls.SEPTEMBRE,
                cls.OCTOBRE,
                cls.NOVEMBRE,
                cls.DECEMBRE]

    @classmethod
    def from_id(cls, numero: int) -> Month:
        return [x for x in cls.values() if x.numero == numero][0]

    @staticmethod
    def meteociel_hourly_numero(x: Month) -> int:
        """
        La numérotation des mois sur météociel (données heure par heure) est décalée.
        Cette méthode associe la numérotation usuelle à gauche de la flèche et celle de météociel, à droite.
         1 => 0    4 => 3     7 => 6     10 =>  9
         2 => 1    5 => 4     8 => 7     11 => 10
         3 => 2    6 => 5     9 => 8     12 => 11
        """
        return x.numero - 1

    @staticmethod
    def format_date_time(date_or_time: int) -> str:
        return f"0{date_or_time}" if date_or_time < 10 else str(date_or_time)
