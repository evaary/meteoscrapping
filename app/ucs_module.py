import abc
import copy
from abc import ABC
from typing import (Any,
                    Dict,
                    Generator)

from app.boite_a_bonheur.MonthEnum import MonthEnum
from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType
from app.boite_a_bonheur.UCFParameterEnum import UCFParameterEnumMember, UCFParameter
from app.tps_module import (TPBuilder,
                            TaskParameters)
from app.UCFChecker import UCFChecker


class GeneralParametersUC:

    _INSTANCE = None

    def __init__(self):
        self._should_download_in_parallel: bool = UCFParameter.DEFAULT_PARALLELISM
        self._cpus: int = UCFParameter.DEFAULT_CPUS
        raise RuntimeError("GeneralParametersUC : appeler GeneralParametersUC.instance()")

    @property
    def should_download_in_parallel(self):
        return self._should_download_in_parallel

    @property
    def cpus(self):
        return self._cpus

    @classmethod
    def from_json_object(cls, jsono: dict, should_check_parameter: bool = True) -> "GeneralParametersUC":

        if should_check_parameter:
            UCFChecker.check_general_parameters(jsono)

        gpuc = GeneralParametersUC.instance()
        gpuc._should_download_in_parallel = jsono[UCFParameter.PARALLELISM.name]

        user_cpus = jsono[UCFParameter.CPUS.name]
        if(    user_cpus == -1
            or user_cpus > UCFParameter.MAX_CPUS):
            gpuc._cpus = UCFParameter.MAX_CPUS
        elif user_cpus == 1:
            gpuc._should_download_in_parallel = False
            gpuc._cpus = user_cpus
        else:
            gpuc._cpus = user_cpus

        return gpuc

    @classmethod
    def instance(cls) -> "GeneralParametersUC":
        if cls._INSTANCE is None:
            cls._INSTANCE = GeneralParametersUC.__new__(cls)
            cls._INSTANCE._should_download_in_parallel = UCFParameter.DEFAULT_PARALLELISM
            cls._INSTANCE._cpus = UCFParameter.DEFAULT_CPUS

        return cls._INSTANCE

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._should_download_in_parallel} {self._cpus}>"


class ScrapperUC(ABC):

    def __init__(self):
        self._city = ""
        self._scrapper_type = None
        self._years = []
        self._months = []
        self._days = []

    @property
    def city(self):
        return self._city

    @property
    def scrapper_type(self):
        return copy.copy(self._scrapper_type)

    @property
    def years(self):
        return copy.copy(self._years)

    @property
    def months(self):
        return copy.copy(self._months)

    @property
    def days(self):
        return copy.copy(self._days)

    @classmethod
    def from_json(cls, jsono: dict, param_name: UCFParameterEnumMember) -> "ScrapperUC":

        if param_name not in UCFParameter.scrappers_parameters():
            raise ValueError("ScrapperUC.from_ucf : param_name doit être un des exceptions")

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
        if self.scrapper_type in ScrapperType.hourly_scrappers():
            return "<{type} {city} {d_from}/{m_from}/{y_from} -> {d_to}/{m_to}/{y_to}>".format(type=self.scrapper_type,
                                                                                               city=self.city,
                                                                                               d_from=self.days[0],
                                                                                               m_from=self.months[0],
                                                                                               y_from=self.years[0],
                                                                                               d_to=self.days[-1],
                                                                                               m_to=self.months[-1],
                                                                                               y_to=self.years[-1])
        else:
            return "<{type} {city} {m_from}/{y_from} -> {m_to}/{y_to}>".format(type=self.scrapper_type,
                                                                               city=self.city,
                                                                               m_from=self.months[0],
                                                                               y_from=self.years[0],
                                                                               m_to=self.months[-1],
                                                                               y_to=self.years[-1])

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

    _PARAMETERS = {UCFParameter.CITY: "_city",
                   UCFParameter.CODE: "_code",
                   UCFParameter.YEARS: "_years",
                   UCFParameter.MONTHS: "_months",
                   UCFParameter.DAYS: "_days"}

    def __init__(self):
        super().__init__()
        self._code = ""

    @classmethod
    def from_json_object(cls, jsono, should_check_parameter: bool = True):

        if should_check_parameter:
            UCFChecker.check_uc(jsono, UCFParameter.METEOCIEL)

        muc = MeteocielUC()

        muc._city = jsono[UCFParameter.CITY.name]
        muc._code = jsono[UCFParameter.CODE.name]
        muc._years = jsono[UCFParameter.YEARS.name]
        muc._months = jsono[UCFParameter.MONTHS.name]

        try:
            muc._days = jsono[UCFParameter.DAYS.name]
            muc._scrapper_type = ScrapperType.METEOCIEL_HOURLY
        except KeyError:
            muc._scrapper_type = ScrapperType.METEOCIEL_DAILY

        return muc

    def to_tps(self):

        if self.scrapper_type == ScrapperType.METEOCIEL_DAILY:

            return (TPBuilder(self.scrapper_type).with_code(self._code)
                                                 .with_city(self._city)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .build()
                    for year in range(self._years[0],
                                      self._years[-1] + 1)

                    for month in range(self._months[0],
                                       self._months[-1] + 1))

        elif self.scrapper_type == ScrapperType.METEOCIEL_HOURLY:

            return (TPBuilder(self.scrapper_type).with_code(self._code)
                                                 .with_city(self._city)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .with_day(day)
                                                 .build()
                    for year in range(self._years[0],
                                      self._years[-1] + 1)

                    for month in range(self._months[0],
                                       self._months[-1] + 1)

                    for day in range(self._days[0],
                                     self._days[-1] + 1)

                    if day <= MonthEnum.from_id(month).ndays)
        else:
            raise ValueError("MeteocielUC.to_tps : scrapper_type invalide")

    def _get_parameters(self):
        return self._PARAMETERS


class OgimetUC(ScrapperUC):

    _PARAMETERS = {UCFParameter.CITY: "_city",
                   UCFParameter.IND: "_ind",
                   UCFParameter.YEARS: "_years",
                   UCFParameter.MONTHS: "_months",
                   UCFParameter.DAYS: "_days"}

    def __init__(self):
        super().__init__()
        self._ind = ""

    @classmethod
    def from_json_object(cls, jsono, should_check_parameter: bool = True):

        if should_check_parameter:
            UCFChecker.check_uc(jsono, UCFParameter.OGIMET)

        ouc = OgimetUC()

        ouc._city = jsono[UCFParameter.CITY.name]
        ouc._ind = jsono[UCFParameter.IND.name]
        ouc._years = jsono[UCFParameter.YEARS.name]
        ouc._months = jsono[UCFParameter.MONTHS.name]

        try:
            ouc._days = jsono[UCFParameter.DAYS.name]
            ouc._scrapper_type = ScrapperType.OGIMET_HOURLY
        except KeyError:
            ouc._scrapper_type = ScrapperType.OGIMET_DAILY

        return ouc

    def to_tps(self):

        if self.scrapper_type == ScrapperType.OGIMET_DAILY:

            return (TPBuilder(self.scrapper_type).with_ind(self._ind)
                                                 .with_city(self._city)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .build()
                    for year in range(self._years[0],
                                      self._years[-1] + 1)

                    for month in range(self._months[0],
                                       self._months[-1] + 1))

        elif self.scrapper_type == ScrapperType.OGIMET_HOURLY:
            # on peut requêter de façon à obtenir une page qui contient l'ensemble des données
            # pour chaque mois, d'où les boucles sur les années et mois mais pas sur les jours
            return (TPBuilder(self.scrapper_type).with_ind(self._ind)
                                                 .with_city(self._city)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .with_day(self._compute_day(month))
                                                 .with_ndays(self._compute_ndays(month))
                                                 .build()
                    for year in range(self._years[0],
                                      self._years[-1] + 1)

                    for month in range(self._months[0],
                                       self._months[-1] + 1))
        else:
            raise ValueError("OgimetUC.to_tps : scrapper_type invalide")

    def _compute_ndays(self, month: int) -> int:

        if self._scrapper_type != ScrapperType.OGIMET_HOURLY:
            raise ValueError("OgimetUC.compute_ndays : le type de scrapper est invalide")

        ndays = self._days[-1] - self._days[0] + 1
        max_ndays = MonthEnum.from_id(month).ndays
        ndays = max_ndays if ndays > max_ndays else ndays

        return ndays

    def _compute_day(self, month: int) -> int:

        if self._scrapper_type != ScrapperType.OGIMET_HOURLY:
            raise ValueError("OgimetUC.compute_day : le type de scrapper est invalide")

        day = self._days[-1]
        max_day = MonthEnum.from_id(month).ndays
        day = max_day if day > max_day else day

        return day

    def _get_parameters(self):
        return self._PARAMETERS


class WundergroundUC(ScrapperUC):

    _PARAMETERS = {UCFParameter.CITY: "_city",
                   UCFParameter.COUNTRY_CODE: "_country_code",
                   UCFParameter.REGION: "_region",
                   UCFParameter.YEARS: "_years",
                   UCFParameter.MONTHS: "_months",
                   UCFParameter.DAYS: "_days"}

    def __init__(self):
        super().__init__()
        self._region = ""
        self._country_code = ""

    @classmethod
    def from_json_object(cls, jsono, should_check_parameter: bool = True):

        if should_check_parameter:
            UCFChecker.check_uc(jsono, UCFParameter.WUNDERGROUND)

        wuc = WundergroundUC()

        wuc._city = jsono[UCFParameter.CITY.name]
        wuc._country_code = jsono[UCFParameter.COUNTRY_CODE.name]
        wuc._region = jsono[UCFParameter.REGION.name]
        wuc._years = jsono[UCFParameter.YEARS.name]
        wuc._months = jsono[UCFParameter.MONTHS.name]

        try:
            wuc._days = jsono[UCFParameter.DAYS.name]
            wuc._scrapper_type = ScrapperType.WUNDERGROUND_HOURLY
        except KeyError:
            wuc._scrapper_type = ScrapperType.WUNDERGROUND_DAILY

        return wuc

    def to_tps(self):

        if self.scrapper_type == ScrapperType.WUNDERGROUND_DAILY:

            return (TPBuilder(self.scrapper_type).with_country_code(self._country_code)
                                                 .with_region(self._region)
                                                 .with_city(self._city)
                                                 .with_year(year)
                                                 .with_month(month)
                                                 .build()
                    for year in range(self._years[0],
                                      self._years[-1] + 1)

                    for month in range(self._months[0],
                                       self._months[-1] + 1))

        elif self.scrapper_type == ScrapperType.WUNDERGROUND_HOURLY:
            raise NotImplementedError("un jour peut être !")
        else:
            raise ValueError("WundergroundUC.to_tps : scrapper_type invalide")

    def _get_parameters(self):
        return self._PARAMETERS
