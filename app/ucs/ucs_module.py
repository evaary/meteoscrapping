import abc
from abc import ABC
from typing import (Any,
                    Dict,
                    Generator)

from app.boite_a_bonheur.MonthsEnum import MonthEnum
from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.boite_a_bonheur.UCFParameterEnum import UCFParameterEnumMember, UCFParameter
from app.tps.tps_module import (TPBuilder,
                                TaskParameters)
from app.ucs.UCFChecker import UCFChecker


class GeneralParametersUC:

    __INSTANCE = None

    def __init__(self):
        self.waiting = UCFParameter.MIN_WAITING
        raise Exception("GeneralParametersUC : utiliser GeneralParametersUC.get_instance")

    @classmethod
    def get_instance(cls) -> "GeneralParametersUC":

        if cls.__INSTANCE is None:
            cls.__INSTANCE = cls.__new__(cls)
            cls.__INSTANCE.waiting = UCFParameter.MIN_WAITING

        return cls.__INSTANCE

    @classmethod
    def from_json_object(cls, jsono) -> "GeneralParametersUC":

        __INSTANCE = cls.get_instance()
        try:
            __INSTANCE.waiting = jsono[UCFParameter.WAITING.name]
        except KeyError:
            pass

        return __INSTANCE


class ScrapperUC(ABC):

    def __init__(self):
        self.city = ""
        self.scrapper_type = None
        self.years = []
        self.months = []
        self.days = []

    @classmethod
    def from_json_object(cls, jsono, param_name: UCFParameterEnumMember) -> "ScrapperUC":

        if param_name not in UCFParameter.scrappers_parameters():
            raise ValueError("ScrapperUC.from_ucf : param_name doit être un des scrappers")

        if param_name == UCFParameter.WUNDERGROUND:
            suc = WundergroundUC.from_json_object(jsono, False)

        elif param_name == UCFParameter.METEOCIEL:
            suc = MeteocielUC.from_json_object(jsono, False)

        else:
            suc = OgimetUC.from_json_object(jsono, False)

        return suc

    @abc.abstractmethod
    def to_tps(self) -> Generator[TaskParameters, Any, None]:
        pass

    @abc.abstractmethod
    def _get_parameters(self) -> Dict[UCFParameterEnumMember, str]:
        pass

    def __repr__(self):
        return f"{self.city} {self.years} {self.months} {self.days} {self.scrapper_type}"

    def __hash__(self):
        x = 7
        for param in self._get_parameters().values():

            field_value = self.__dict__[param]
            if isinstance(field_value, list):
                for list_value in field_value:
                    x = 79 * x + hash(list_value)
            else:
                x = 79 * x + hash(field_value)

        return x

    def __eq__(self, other):

        if other is None:
            return False

        if not isinstance(other, self.__class__):
            return False

        for param in self._get_parameters().values():
            try:
                if self.__dict__[param] != other.__dict__[param]:
                    return False
            except KeyError:
                return False

        if self.scrapper_type != other.scrapper_type:
            return False

        return True


class MeteocielUC(ScrapperUC):

    __PARAMETERS = {UCFParameter.CITY: "city",
                    UCFParameter.CODE: "code",
                    UCFParameter.CODE_NUM: "code_num",
                    UCFParameter.YEARS: "years",
                    UCFParameter.MONTHS: "months",
                    UCFParameter.DAYS: "days"}

    def __init__(self):
        super().__init__()
        self.code = ""
        self.code_num = ""

    @classmethod
    def from_json_object(cls, jsono, should_check_parameter: bool = True):

        if should_check_parameter:
            UCFChecker.check_individual_uc(jsono, UCFParameter.METEOCIEL)

        muc = MeteocielUC()

        muc.city = jsono[UCFParameter.CITY.name]
        muc.code = jsono[UCFParameter.CODE.name]
        muc.code_num = jsono[UCFParameter.CODE_NUM.name]
        muc.years = jsono[UCFParameter.YEARS.name]
        muc.months = jsono[UCFParameter.MONTHS.name]

        try:
            muc.days = jsono[UCFParameter.DAYS.name]
            muc.scrapper_type = ScrapperType.METEOCIEL_HOURLY
        except KeyError:
            muc.scrapper_type = ScrapperType.METEOCIEL_DAILY

        return muc

    # override
    def to_tps(self):

        if self.scrapper_type == ScrapperType.METEOCIEL_DAILY:

            return (TPBuilder(self.scrapper_type).with_code(self.code)
                                                 .with_code_num(self.code_num)
                                                 .with_city(self.city)
                                                 .with_waiting(GeneralParametersUC.get_instance().waiting)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .build()
                    for year in range(self.years[0],
                                      self.years[-1] + 1)

                    for month in range(self.months[0],
                                       self.months[-1] + 1))

        elif self.scrapper_type == ScrapperType.METEOCIEL_HOURLY:

            return (TPBuilder(self.scrapper_type).with_code(self.code)
                                                 .with_code_num(self.code_num)
                                                 .with_city(self.city)
                                                 .with_waiting(GeneralParametersUC.get_instance().waiting)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .with_day(day)
                                                 .build()
                    for year in range(self.years[0],
                                      self.years[-1] + 1)

                    for month in range(self.months[0],
                                       self.months[-1] + 1)

                    for day in range(self.days[0],
                                     self.days[-1] + 1)

                    if day <= MonthEnum.from_id(month).ndays)
        else:
            raise ValueError("MeteocielUC.to_tps : scrapper_type invalide")

    # override
    def _get_parameters(self):
        return self.__PARAMETERS

    def __repr__(self):
        msg = super().__repr__()
        return f"<{self.__class__.__name__} {self.code} {self.code_num} {msg}>"


class OgimetUC(ScrapperUC):

    __PARAMETERS = {UCFParameter.CITY: "city",
                    UCFParameter.IND: "ind",
                    UCFParameter.YEARS: "years",
                    UCFParameter.MONTHS: "months",
                    UCFParameter.DAYS: "days"}

    def __init__(self):
        super().__init__()
        self.ind = ""

    @classmethod
    def from_json_object(cls, jsono, should_check_parameter: bool = True):

        if should_check_parameter:
            UCFChecker.check_individual_uc(jsono, UCFParameter.OGIMET)

        ouc = OgimetUC()

        ouc.city = jsono[UCFParameter.CITY.name]
        ouc.ind = jsono[UCFParameter.IND.name]
        ouc.years = jsono[UCFParameter.YEARS.name]
        ouc.months = jsono[UCFParameter.MONTHS.name]

        try:
            ouc.days = jsono[UCFParameter.DAYS.name]
            ouc.scrapper_type = ScrapperType.OGIMET_HOURLY
        except KeyError:
            ouc.scrapper_type = ScrapperType.OGIMET_DAILY

        return ouc

    # override
    def to_tps(self):

        if self.scrapper_type == ScrapperType.OGIMET_DAILY:

            return (TPBuilder(self.scrapper_type).with_ind(self.ind)
                                                 .with_city(self.city)
                                                 .with_waiting(GeneralParametersUC.get_instance().waiting)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .build()
                    for year in range(self.years[0],
                                      self.years[-1] + 1)

                    for month in range(self.months[0],
                                       self.months[-1] + 1))

        elif self.scrapper_type == ScrapperType.OGIMET_HOURLY:

            return (TPBuilder(self.scrapper_type).with_ind(self.ind)
                                                 .with_city(self.city)
                                                 .with_waiting(GeneralParametersUC.get_instance().waiting)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .with_day(day)
                                                 .build()
                    for year in range(self.years[0],
                                      self.years[-1] + 1)

                    for month in range(self.months[0],
                                       self.months[-1] + 1)

                    for day in range(self.days[0],
                                     self.days[-1] + 1)

                    if day <= MonthEnum.from_id(month).ndays)
        else:
            raise ValueError("OgimetUC.to_tps : scrapper_type invalide")

    # override
    def _get_parameters(self):
        return self.__PARAMETERS

    def __repr__(self):
        msg = super().__repr__()
        return f"<{self.__class__.__name__} {self.ind} {msg}>"


class WundergroundUC(ScrapperUC):

    __PARAMETERS = {UCFParameter.CITY: "city",
                    UCFParameter.COUNTRY_CODE: "country_code",
                    UCFParameter.REGION: "region",
                    UCFParameter.YEARS: "years",
                    UCFParameter.MONTHS: "months",
                    UCFParameter.DAYS: "days"}

    def __init__(self):
        super().__init__()
        self.region = ""
        self.country_code = ""

    @classmethod
    def from_json_object(cls, jsono, should_check_parameter: bool = True):

        if should_check_parameter:
            UCFChecker.check_individual_uc(jsono, UCFParameter.WUNDERGROUND)

        wuc = WundergroundUC()

        wuc.city = jsono[UCFParameter.CITY.name]
        wuc.country_code = jsono[UCFParameter.COUNTRY_CODE.name]
        wuc.region = jsono[UCFParameter.REGION.name]
        wuc.years = jsono[UCFParameter.YEARS.name]
        wuc.months = jsono[UCFParameter.MONTHS.name]

        try:
            wuc.days = jsono[UCFParameter.DAYS.name]
            wuc.scrapper_type = ScrapperType.WUNDERGROUND_HOURLY
        except KeyError:
            wuc.scrapper_type = ScrapperType.WUNDERGROUND_DAILY

        return wuc

    # override
    def to_tps(self):

        if self.scrapper_type == ScrapperType.WUNDERGROUND_DAILY:

            return (TPBuilder(self.scrapper_type).with_country_code(self.country_code)
                                                 .with_region(self.region)
                                                 .with_city(self.city)
                                                 .with_waiting(GeneralParametersUC.get_instance().waiting)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .build()
                    for year in range(self.years[0],
                                      self.years[-1] + 1)

                    for month in range(self.months[0],
                                       self.months[-1] + 1))

        elif self.scrapper_type == ScrapperType.WUNDERGROUND_HOURLY:

            return (TPBuilder(self.scrapper_type).with_country_code(self.country_code)
                                                 .with_region(self.region)
                                                 .with_city(self.city)
                                                 .with_waiting(GeneralParametersUC.get_instance().waiting)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .with_day(day)
                                                 .build()
                    for year in range(self.years[0],
                                      self.years[-1] + 1)

                    for month in range(self.months[0],
                                       self.months[-1] + 1)

                    for day in range(self.days[0],
                                     self.days[-1] + 1)

                    if day <= MonthEnum.from_id(month).ndays)
        else:
            raise ValueError("WundergroundUC.to_tps : scrapper_type invalide")

    # override
    def _get_parameters(self):
        return self.__PARAMETERS

    def __repr__(self):
        msg = super().__repr__()
        return f"<{self.__class__.__name__} {self.country_code} {self.region} {msg}>"
