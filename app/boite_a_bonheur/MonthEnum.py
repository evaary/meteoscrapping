class MonthEnumMember:
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
        if other is None or not isinstance(other, MonthEnumMember):
            return False

        return self._numero == other.numero

    def __copy__(self):
        return MonthEnumMember(self._numero, self._ndays)

    def __repr__(self):
        return self._name


class MonthEnum:

    JANVIER = MonthEnumMember(1, 31, "JANVIER")
    FEVRIER = MonthEnumMember(2, 28, "FEVRIER")
    MARS = MonthEnumMember(3, 31, "MARS")
    AVRIL = MonthEnumMember(4, 30, "AVRIL")
    MAI = MonthEnumMember(5, 31, "MAI")
    JUIN = MonthEnumMember(6, 30, "JUIN")
    JUILLET = MonthEnumMember(7, 31, "JUILLET")
    AOUT = MonthEnumMember(8, 31, "AOUT")
    SEPTEMBRE = MonthEnumMember(9, 30, "SEPTEMBRE")
    OCTOBRE = MonthEnumMember(10, 31, "OCTOBRE")
    NOVEMBRE = MonthEnumMember(11, 30, "NOVEMBRE")
    DECEMBRE = MonthEnumMember(12, 31, "DECEMBRE")

    @classmethod
    def values(cls) -> list[MonthEnumMember]:
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
    def from_id(cls, numero: int) -> MonthEnumMember:
        return [x for x in cls.values() if x.numero == numero][0]

    @staticmethod
    def meteociel_hourly_numero(x: MonthEnumMember) -> int:
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
