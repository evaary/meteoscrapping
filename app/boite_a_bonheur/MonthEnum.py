class MonthEnumMember:
    def __init__(self, numero: int, ndays: int):
        self._numero = numero
        self._ndays = ndays

    @property
    def numero(self):
        return self._numero

    @property
    def ndays(self):
        return self._ndays

    def __eq__(self, other):
        if other is None or not isinstance(other, MonthEnumMember):
            return False

        return self._numero == other.numero

    def __copy__(self):
        return MonthEnumMember(self._numero, self._ndays)
        
        
class MonthEnum:

    JANVIER = MonthEnumMember(1, 31)
    FEVRIER = MonthEnumMember(2, 28)
    MARS = MonthEnumMember(3, 31)
    AVRIL = MonthEnumMember(4, 30)
    MAI = MonthEnumMember(5, 31)
    JUIN = MonthEnumMember(6, 30)
    JUILLET = MonthEnumMember(7, 31)
    AOUT = MonthEnumMember(8, 31)
    SEPTEMBRE = MonthEnumMember(9, 30)
    OCTOBRE = MonthEnumMember(10, 31)
    NOVEMBRE = MonthEnumMember(11, 30)
    DECEMBRE = MonthEnumMember(12, 31)

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
