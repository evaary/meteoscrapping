class MonthEnum:

    class __MonthEnumMember:
        def __init__(self, numero: int, ndays: int):
            self.numero = numero
            self.ndays = ndays

    JANVIER = __MonthEnumMember(1, 31)
    FEVRIER = __MonthEnumMember(2, 28)
    MARS = __MonthEnumMember(3, 31)
    AVRIL = __MonthEnumMember(4, 30)
    MAI = __MonthEnumMember(5, 31)
    JUIN = __MonthEnumMember(6, 30)
    JUILLET = __MonthEnumMember(7, 31)
    AOUT = __MonthEnumMember(8, 31)
    SEPTEMBRE = __MonthEnumMember(9, 30)
    OCTOBRE = __MonthEnumMember(10, 30)
    NOVEMBRE = __MonthEnumMember(11, 31)
    DECEMBRE = __MonthEnumMember(12, 31)

    @classmethod
    def values(cls) -> list[__MonthEnumMember]:
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
    def from_id(cls, numero: int) -> __MonthEnumMember:
        return [x for x in cls.values() if x.numero == numero][0]

    @classmethod
    def meteociel_hourly_numero(cls, x: __MonthEnumMember) -> int:
        """
        La numérotation des mois sur météociel (données heure par heure) est décalée.
        Cette méthode associe la numérotation usuelle à gauche de la flèche et celle de météociel, à droite.
         1 => 0    4 => 3     7 => 6     10 =>  9
         2 => 1    5 => 4     8 => 7     11 => 10
         3 => 2    6 => 5     9 => 8     12 => 11
        """
        return x.numero - 1

    @classmethod
    def ogimet_daily_numero(cls, x: __MonthEnumMember) -> int:
        """
        La numérotation des mois sur ogimet (données jour par jour) est décalée.
        Cette méthode associe la numérotation usuelle à gauche de la flèche et celle d'ogimet, à droite.
         1 => 2    4 => 5     7 =>  8     10 => 11
         2 => 3    5 => 6     8 =>  9     11 => 12
         3 => 4    6 => 7     9 => 10     12 =>  1
        """
        return 1 if x == cls.DECEMBRE else x.numero + 1
