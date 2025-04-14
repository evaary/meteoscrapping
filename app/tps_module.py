import abc
import copy
from string import Template

from app.boite_a_bonheur.Criteria import Criteria
from app.boite_a_bonheur.MonthEnum import Months
from app.boite_a_bonheur.ScraperTypeEnum import (ScrapperTypes,
                                                 ScrapperType)
from app.boite_a_bonheur.UCFParameterEnum import UCFParameters


class TPBuilder:

    def __init__(self, param: ScrapperType):

        if param is None:
            raise ValueError(f"TPBuilder : paramètre invalide : {param}")

        self._scrapper_type = param
        self._year = 0
        self._month = 0
        self._day = 0
        self._ndays = 0
        self._year_as_str = ""
        self._month_as_str = ""
        self._day_as_str = ""
        self._city = ""
        self._code = ""
        self._ind = ""
        self._country_code = ""
        self._region = ""

    def with_year(self, param: int) -> "TPBuilder":

        if param < UCFParameters.MIN_YEARS:
            raise ValueError(f"TPBuilder.with_year : paramètre invalide {param}")

        self._year = param
        self._year_as_str = str(param)

        return self

    def with_month(self, param: int) -> "TPBuilder":

        if param not in range(UCFParameters.MIN_MONTHS_DAYS_VALUE,
                              UCFParameters.MAX_MONTHS + 1):
            raise ValueError(f"TPBuilder.with_month : paramètre invalide {param}")

        self._month = param
        self._month_as_str = Months.format_date_time(param)

        return self

    def with_day(self, param: int) -> "TPBuilder":

        Months.from_id(self._month)  # IndexError si month n'est pas valorisée avant

        if self._scrapper_type not in ScrapperTypes.hourly_scrappers():
            raise ValueError(f"TPBuilder.with_day : type de scrapper incompatible ({self._scrapper_type})")

        if param not in range(UCFParameters.MIN_MONTHS_DAYS_VALUE,
                              UCFParameters.MAX_DAYS + 1):
            raise ValueError(f"TPBuilder.with_day : paramètre invalide {param}")

        self._day = param
        self._day_as_str = Months.format_date_time(param)

        return self

    def with_city(self, param: str) -> "TPBuilder":

        if param is None or len(param) == 0:
            raise ValueError(f"TPBuilder.with_city : paramètre invalide {param}")

        self._city = param

        return self

    def with_code(self, param: str) -> "TPBuilder":

        if self._scrapper_type not in ScrapperTypes.meteociel_scrappers():
            raise ValueError(f"TPBuilder.with_code : spécifique meteociel.")

        if param is None or len(param) == 0:
            raise ValueError(f"TPBuilder.with_code : paramètre invalide {param}")

        self._code = param

        return self

    def with_region(self, param: str) -> "TPBuilder":

        if self._scrapper_type not in ScrapperTypes.wunderground_scrappers():
            raise ValueError(f"TPBuilder.with_region : spécifique wunderground.")

        if param is None or len(param) == 0:
            raise ValueError(f"TPBuilder.with_region : paramètre invalide {param}")

        self._region = param

        return self

    def with_country_code(self, param: str) -> "TPBuilder":

        if self._scrapper_type not in ScrapperTypes.wunderground_scrappers():
            raise ValueError(f"TPBuilder.with_country_code : spécifique wunderground.")

        if param is None or len(param) == 0:
            raise ValueError(f"TPBuilder.with_country_code : paramètre invalide {param}")

        self._country_code = param

        return self

    def with_ind(self, param: str) -> "TPBuilder":

        if self._scrapper_type not in ScrapperTypes.ogimet_scrappers():
            raise ValueError(f"TPBuilder.with_ind : spécifique ogimet.")

        if param is None or len(param) == 0:
            raise ValueError(f"TPBuilder.with_ind : paramètre invalide {param}")

        self._ind = param

        return self

    def with_ndays(self, param: int) -> "TPBuilder":

        if self._scrapper_type != ScrapperTypes.OGIMET_HOURLY:
            raise ValueError(f"TPBuilder.with_ndays : spécifique ogimet heure par heure.")

        if param not in range(UCFParameters.MIN_MONTHS_DAYS_VALUE,
                              UCFParameters.MAX_DAYS + 1):
            raise ValueError(f"TPBuilder.with_ndays : paramètre invalide {param}")

        self._ndays = param

        return self

    def build(self) -> "TaskParameters":

        if self._month == 0 or self._year == 0:
            raise ValueError("TPBuilder.build : 'month' et 'year' requis.")

        if self._scrapper_type in ScrapperTypes.hourly_scrappers() and self._day == 0:
            raise ValueError("TPBuilder.build : 'day' requis pour un scrapper heure par heure.")

        if self._scrapper_type in ScrapperTypes.meteociel_scrappers():
            if any([x is None or len(x) == 0 for x in [self._code,
                                                       self._city]]):
                raise ValueError("TPBuilder.build : 'code' et 'city' requis pour Meteociel.")

            return MeteocielTP(self)

        if self._scrapper_type in ScrapperTypes.ogimet_scrappers():
            if any([x is None or len(x) == 0 for x in [self._ind,
                                                       self._city]]):
                raise ValueError("TPBuilder.build : 'ind' et 'city' requis pour Ogimet.")

            if(    self._scrapper_type == ScrapperTypes.OGIMET_HOURLY
               and self._ndays == 0):
                raise ValueError("TPBuilder.build : 'ndays' requis pour Ogimet heure par heure.")

            return OgimetTP(self)

        if self._scrapper_type in ScrapperTypes.wunderground_scrappers():
            if any([x is None or len(x) == 0 for x in [self.region,
                                                       self.country_code,
                                                       self.city]]):
                raise ValueError("TPBuilder.build : 'region', 'country_code' et 'city' requis pour Wunderground.")

            return WundergroundTP(self)

        raise ValueError(f"TPBuilder.build : paramètre invalide {self._scrapper_type}.")

    @property
    def scrapper_type(self) -> ScrapperType:
        return copy.copy(self._scrapper_type)

    @property
    def year(self):
        return self._year

    @property
    def year_as_str(self):
        return self._year_as_str

    @property
    def month(self):
        return self._month

    @property
    def month_as_str(self):
        return self._month_as_str

    @property
    def day(self):
        return self._day

    @property
    def day_as_str(self):
        return self._day_as_str

    @property
    def code(self):
        if self._scrapper_type not in ScrapperTypes.meteociel_scrappers():
            raise ValueError(f"TPBuilder.code : spécifique meteociel.")

        return self._code

    @property
    def ind(self):
        if self._scrapper_type not in ScrapperTypes.ogimet_scrappers():
            raise ValueError(f"TPBuilder.ind : spécifique ogimet.")

        return self._ind

    @property
    def ndays(self):
        if self._scrapper_type != ScrapperTypes.OGIMET_HOURLY:
            raise ValueError(f"TPBuilder.ndays : spécifique ogimet heure par heure.")

        return self._ndays

    @property
    def country_code(self):
        if self._scrapper_type not in ScrapperTypes.wunderground_scrappers():
            raise ValueError(f"TPBuilder.country_code : spécifique wunderground.")

        return self._country_code

    @property
    def region(self):
        if self.scrapper_type not in ScrapperTypes.wunderground_scrappers():
            raise ValueError(f"TPBuilder.region : spécifique wunderground.")

        return self._region

    @property
    def city(self):
        return self._city


class TaskParameters(abc.ABC):

    def __init__(self, builder: TPBuilder):
        self._waiting = UCFParameters.DEFAULT_WAITING
        self._year = builder.year
        self._month = builder.month
        self._day = builder.day
        self._year_as_str = builder.year_as_str
        self._month_as_str = builder.month_as_str
        self._day_as_str = builder.day_as_str
        self._city = builder.city
        self._url = ""
        self._criteria : Criteria = None
        self._scrapper_type : ScrapperType = builder.scrapper_type
        try:
            self._ndays = builder.ndays
        except ValueError:
            self._ndays = 0

        if builder.scrapper_type in ScrapperTypes.hourly_scrappers():
            self._key = f"{self._scrapper_type}_{self._city}_{self._day_as_str}_{self._month_as_str}_{self._year_as_str}"
        else:
            self._key = f"{self._scrapper_type}_{self._city}_{self._month_as_str}_{self._year_as_str}"

    @property
    def scrapper_type(self):
        return self._scrapper_type

    @property
    def year(self):
        return self._year

    @property
    def year_as_str(self):
        return self._year_as_str

    @property
    def month(self):
        return self._month

    @property
    def month_as_str(self):
        return self._month_as_str

    @property
    def day(self):
        if self._scrapper_type not in ScrapperTypes.hourly_scrappers():
            raise ValueError("TaskParameters.day : spécifique scrapper heure par heure")

        return self._day

    @property
    def day_as_str(self):
        if self._scrapper_type not in ScrapperTypes.hourly_scrappers():
            raise ValueError("TaskParameters.day_as_str : spécifique scrapper heure par heure")

        return self._day_as_str

    @property
    def ndays(self):
        if self._scrapper_type != ScrapperTypes.OGIMET_HOURLY:
            raise ValueError(f"TaskParameters.ndays : spécifique ogimet heure par heure.")

        return self._ndays

    @property
    def city(self):
        return self._city

    @property
    def url(self):
        return self._url

    @property
    def criteria(self):
        return copy.copy(self._criteria)

    @property
    def waiting(self):
        return self._waiting

    @property
    def key(self):
        return self._key

    def update_waiting(self):
        self._waiting *= 2

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._url}>"


class MeteocielTP(TaskParameters):

    _CRITERIA_DAILY = Criteria("cellpadding", "2")
    _CRITERIA_HOURLY = Criteria("bgcolor", "#EBFAF7")
    _BASE_URL_DAILY = Template("https://www.meteociel.com/climatologie/obs_villes.php?code=$code&annee=$annee&mois=$mois")
    _BASE_URL_HOURLY = Template("https://www.meteociel.com/temps-reel/obs_villes.php?code2=$code&annee2=$annee&mois2=$mois&jour2=$jour")

    def __init__(self, builder: TPBuilder):

        super().__init__(builder)
        self._code = builder.code

        if builder.scrapper_type == ScrapperTypes.METEOCIEL_DAILY:
            self._url = self._BASE_URL_DAILY.substitute(code=builder.code,
                                                        mois=builder.month,
                                                        annee=builder.year)
            self._criteria = self._CRITERIA_DAILY

        elif builder.scrapper_type == ScrapperTypes.METEOCIEL_HOURLY:
            month_enum_value = Months.from_id(builder.month)
            self._url = self._BASE_URL_HOURLY.substitute(code=builder.code,
                                                         jour=builder.day,
                                                         mois=Months.meteociel_hourly_numero(month_enum_value),
                                                         annee=builder.year)
            self._criteria = self._CRITERIA_HOURLY

        else:
            raise ValueError("MeteocielTP : TPBuilder.scrapper_type invalide")


class OgimetTP(TaskParameters):

    _CRITERIA = Criteria("bgcolor", "#d0d0d0")
    _BASE_URL = Template("https://www.ogimet.com/cgi-bin/gsynres?ind=$ind&ndays=$ndays&ano=$ano&mes=$mes&day=$day&hora=23&lang=en&decoded=$decoded")

    def __init__(self, builder: TPBuilder):

        super().__init__(builder)

        self._ind = builder.ind
        self._criteria = self._CRITERIA

        if builder.scrapper_type == ScrapperTypes.OGIMET_DAILY:
            self._url = self._BASE_URL.substitute(ind=builder.ind,
                                                  ndays=Months.from_id(builder.month).ndays,
                                                  ano=builder.year,
                                                  mes=builder.month,
                                                  day=Months.from_id(builder.month).ndays,
                                                  decoded="no")

        elif builder.scrapper_type == ScrapperTypes.OGIMET_HOURLY:
            self._url = self._BASE_URL.substitute(ind=builder.ind,
                                                  ndays=builder.ndays,
                                                  ano=builder.year,
                                                  mes=builder.month,
                                                  day=builder.day,
                                                  decoded="yes")
        else:
            raise ValueError("OgimetTP : TPBuilder.scrapper_type invalide")


class WundergroundTP(TaskParameters):

    _CRITERIA_DAILY = Criteria("aria-labelledby", "History days")
    _BASE_URL_DAILY = Template("https://www.wunderground.com/history/monthly/$country_code/$city/$region/date/$year-$month")

    def __init__(self, builder: TPBuilder):

        super().__init__(builder)
        self._region = builder.region
        self._country_code = builder.country_code

        if builder.scrapper_type == ScrapperTypes.WUNDERGROUND_DAILY:
            self._url = self._BASE_URL_DAILY.substitute(country_code=builder.country_code,
                                                        city=builder.city,
                                                        region=builder.region,
                                                        year=builder.year,
                                                        month=builder.month)
            self._criteria = self._CRITERIA_DAILY

        elif builder.scrapper_type == ScrapperTypes.WUNDERGROUND_HOURLY:
            raise NotImplementedError("un jour peut être !")

        else:
            raise ValueError("WundergroundTP : TPBuilder.scrapper_type invalide")
