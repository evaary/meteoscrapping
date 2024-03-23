import abc
from string import Template

from app.boite_a_bonheur.Criteria import Criteria
from app.boite_a_bonheur.MonthsEnum import MonthEnum
from app.boite_a_bonheur.ScraperTypeEnum import (ScrapperType,
                                                 ScrapperTypeEnumMember)
from app.boite_a_bonheur.UCFParameterEnum import UCFParameter


class TPBuilder:

    def __init__(self, scrapper_type: ScrapperTypeEnumMember):

        if scrapper_type is None or scrapper_type in ScrapperType.generic_scrapper_types():
            raise ValueError(f"TPBuilder : paramètre invalide : {scrapper_type}")

        self.scrapper_type = scrapper_type
        self.waiting = UCFParameter.MIN_WAITING
        self.year = 0
        self.month = 0
        self.day = 0
        self.year_as_str = ""
        self.month_as_str = ""
        self.day_as_str = ""
        self.city = ""
        self.code = ""
        self.code_num = ""
        self.ind = ""
        self.country_code = ""
        self.region = ""

    def with_year(self, year: int) -> "TPBuilder":

        if year < UCFParameter.MIN_YEARS:
            raise ValueError(f"TPBuilder.year : paramètre invalide {year}")

        self.year = year
        self.year_as_str = str(year)

        return self

    def with_month(self, month: int) -> "TPBuilder":

        if month not in range(UCFParameter.MIN_MONTHS_DAYS_VALUE,
                              UCFParameter.MAX_MONTHS + 1):
            raise ValueError(f"TPBuilder.month : paramètre invalide {month}")

        self.month = month
        self.month_as_str = "0" + str(month) if month < 10 else str(month)

        return self

    def with_day(self, day: int) -> "TPBuilder":

        MonthEnum.from_id(self.month)  # IndexError si month n'est pas valorisée avant

        if day not in range(UCFParameter.MIN_MONTHS_DAYS_VALUE,
                            UCFParameter.MAX_DAYS + 1):
            raise ValueError(f"TPBuilder.day : paramètre invalide {day}")

        self.day = day
        self.day_as_str = "0" + str(day) if day < 10 else str(day)

        return self

    def with_city(self, city: str) -> "TPBuilder":

        if city is None or len(city) == 0:
            raise ValueError(f"TPBuilder.__city : paramètre invalide {city}")

        self.city = city
        return self

    def with_code(self, code: str) -> "TPBuilder":

        if code is None or len(code) == 0:
            raise ValueError(f"TPBuilder.code : paramètre invalide {code}")

        self.code = code
        return self

    def with_code_num(self, code_num: str) -> "TPBuilder":

        if code_num is None or len(code_num) == 0:
            raise ValueError(f"TPBuilder.code_num : paramètre invalide {code_num}")

        self.code_num = code_num
        return self

    def with_region(self, region: str) -> "TPBuilder":

        if region is None or len(region) == 0:
            raise ValueError(f"TPBuilder.region : paramètre invalide {region}")

        self.region = region
        return self

    def with_country_code(self, country_code: str) -> "TPBuilder":

        if country_code is None or len(country_code) == 0:
            raise ValueError(f"TPBuilder.country_code : paramètre invalide {country_code}")

        self.country_code = country_code
        return self

    def with_ind(self, ind: str) -> "TPBuilder":

        if ind is None or len(ind) == 0:
            raise ValueError(f"TPBuilder.ind : paramètre invalide {ind}")

        self.ind = ind
        return self

    def with_waiting(self, waiting: int) -> "TPBuilder":
        if waiting not in range(UCFParameter.MIN_WAITING,
                                UCFParameter.MAX_WAITING + 1):
            raise ValueError(f"TPBuilder.waiting : paramètre invalide {waiting}")
        self.waiting = waiting
        return self

    def build(self) -> "TaskParameters":

        if self.month == 0 or self.year == 0:
            raise ValueError("TPBuilder.build : month et year doivent être valorisés.")

        if self.scrapper_type in ScrapperType.hourly_scrapper_types() and self.day == 0:
            raise ValueError("TPBuilder.build : day doit être valorisé pour un scrapper heure par heure.")

        if self.scrapper_type in [ScrapperType.METEOCIEL_DAILY,
                                  ScrapperType.METEOCIEL_HOURLY]:
            if any([x is None or len(x) == 0 for x in [self.code,
                                                       self.code_num,
                                                       self.city]]):
                raise ValueError("TPBuilder.build : code, code_num et city doivent être valorisés pour un scrapper Meteociel.")

            return MeteocielTP(self)

        if self.scrapper_type in [ScrapperType.OGIMET_DAILY,
                                  ScrapperType.OGIMET_HOURLY]:
            if any([x is None or len(x) == 0 for x in [self.ind,
                                                       self.city]]):
                raise ValueError("TPBuilder.build : ind et city doivent être valorisés pour un scrapper Ogimet.")

            return OgimetTP(self)

        if self.scrapper_type in [ScrapperType.WUNDERGROUND_DAILY,
                                  ScrapperType.WUNDERGROUND_HOURLY]:
            if any([x is None or len(x) == 0 for x in [self.region,
                                                       self.country_code,
                                                       self.city]]):
                raise ValueError("TPBuilder.build : region, country_code et city doivent être valorisés pour un scrapper Wunderground.")

            return WundergroundTP(self)

        raise ValueError(f"TPBuilder.build : paramètre invalide {self.scrapper_type}.")


class TaskParameters(abc.ABC):

    def __init__(self, tpbuilder: TPBuilder):
        self.waiting = tpbuilder.waiting
        self.year = tpbuilder.year
        self.month = tpbuilder.month
        self.day = tpbuilder.day
        self.year_as_str = tpbuilder.year_as_str
        self.month_as_str = tpbuilder.month_as_str
        self.day_as_str = tpbuilder.day_as_str
        self.city = tpbuilder.city
        self.url = ""
        self.criteria = None
        self.key = f"{self.city}_{self.year_as_str}_{self.month_as_str}"
        if tpbuilder.scrapper_type in ScrapperType.hourly_scrapper_types():
            self.key = f"{self.key}_{self.day_as_str}"

    def __repr__(self):
        if self.day == 0:
            return f"{self.city} {self.month_as_str}/{self.year_as_str}"
        else:
            return f"{self.city} {self.day_as_str}/{self.month_as_str}/{self.year_as_str}"


class MeteocielTP(TaskParameters):

    CRITERIA_DAILY = Criteria("cellpadding", "2")
    CRITERIA_HOURLY = Criteria("bgcolor", "#EBFAF7")
    BASE_URL_DAILY = Template("https://www.meteociel.com/climatologie/obs_villes.php?code$code_num=$code&mois=$mois&annee=$annee")
    BASE_URL_HOURLY = Template("https://www.meteociel.com/temps-reel/obs_villes.php?code$code_num=$code&jour2=$jour2&mois2=$mois2&annee2=$annee2")

    def __init__(self, tpbuilder: TPBuilder):

        super().__init__(tpbuilder)
        self.code = tpbuilder.code
        self.code_num = tpbuilder.code_num

        if tpbuilder.scrapper_type == ScrapperType.METEOCIEL_DAILY:
            self.url = self.BASE_URL_DAILY.substitute(code_num=tpbuilder.code_num,
                                                      code=tpbuilder.code,
                                                      mois=tpbuilder.month,
                                                      annee=tpbuilder.year)
            self.criteria = self.CRITERIA_DAILY

        elif tpbuilder.scrapper_type == ScrapperType.METEOCIEL_HOURLY:
            month_enum_value = MonthEnum.from_id(tpbuilder.month)
            self.url = self.BASE_URL_HOURLY.substitute(code_num=tpbuilder.code_num,
                                                       code=tpbuilder.code,
                                                       jour2=tpbuilder.day,
                                                       mois2=MonthEnum.meteociel_hourly_numero(month_enum_value),
                                                       annee2=tpbuilder.year)
            self.criteria = self.CRITERIA_HOURLY

        else:
            raise ValueError("MeteocielTP : tpbuilder.scrapper_type est invalide")

    def __repr__(self):
        return f"<{self.__class__.__name__} {super().__repr__()} {self.code_num} {self.code}"


class OgimetTP(TaskParameters):

    CRITERIA_DAILY = Criteria("bgcolor", "#d0d0d0")
    BASE_URL_DAILY = Template(f"http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=$ind&ano=$ano&mes=$mes&day=0&hora=0&min=0&ndays=$ndays")

    def __init__(self, tpbuilder: TPBuilder):

        super().__init__(tpbuilder)
        self.ind = tpbuilder.ind

        if tpbuilder.scrapper_type == ScrapperType.OGIMET_DAILY:
            month_enum_value = MonthEnum.from_id(tpbuilder.month)
            self.url = self.BASE_URL_DAILY.substitute(ind=tpbuilder.ind,
                                                      ano=tpbuilder.year,
                                                      mes=MonthEnum.ogimet_daily_numero(month_enum_value),
                                                      ndays=month_enum_value.ndays)
            self.criteria = self.CRITERIA_DAILY

        elif tpbuilder.scrapper_type == ScrapperType.OGIMET_HOURLY:
            raise NotImplementedError("un jour peut être !")

        else:
            raise ValueError("OgimetTP : tpbuilder.scrapper_type est invalide")

    def __repr__(self):
        return f"<{self.__class__.__name__} {super().__repr__()} {self.ind}"


class WundergroundTP(TaskParameters):

    CRITERIA_DAILY = Criteria("aria-labelledby", "History days")
    BASE_URL_DAILY = Template("https://www.wunderground.com/history/monthly/$country_code/$city/$region/date/$year-$month")

    def __init__(self, tpbuilder: TPBuilder):

        super().__init__(tpbuilder)
        self.region = tpbuilder.region
        self.country_code = tpbuilder.country_code

        if tpbuilder.scrapper_type == ScrapperType.WUNDERGROUND_DAILY:
            self.url = self.BASE_URL_DAILY.substitute(country_code=tpbuilder.country_code,
                                                      city=tpbuilder.city,
                                                      region=tpbuilder.region,
                                                      year=tpbuilder.year,
                                                      month=tpbuilder.month)
            self.criteria = self.CRITERIA_DAILY

        elif tpbuilder.scrapper_type == ScrapperType.WUNDERGROUND_HOURLY:
            raise NotImplementedError("un jour peut être !")

        else:
            raise ValueError("WundergroundTP : tpbuilder.scrapper_type est invalide")

    def __repr__(self):
        return f"<{self.__class__.__name__} {super().__repr__()} {self.country_code} {self.region}"
