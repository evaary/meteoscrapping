import abc
import copy
from abc import ABC
from typing import (Any,
                    List,
                    Generator)

from app.boite_a_bonheur.MonthEnum import Months
from app.boite_a_bonheur.ScraperTypeEnum import ScrapperType, ScrapperTypeEnumMember
from app.boite_a_bonheur.UCFParameterEnum import UCFParameterEnumMember, UCFParameter
from app.tps_module import (TPBuilder,
                            TaskParameters)


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
    def from_json_object(cls, jsono: dict) -> "GeneralParametersUC":

        gpuc = GeneralParametersUC.instance()
        gpuc._should_download_in_parallel = jsono[UCFParameter.PARALLELISM.json_name]

        user_cpus = jsono[UCFParameter.CPUS.json_name]
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
        self._city : str = ""
        self._scrapper_type : ScrapperTypeEnumMember = None
        self._dates : List[str] = []

    @property
    def city(self) -> str:
        return self._city

    @property
    def scrapper_type(self) -> ScrapperTypeEnumMember:
        return copy.copy(self._scrapper_type)

    @property
    def dates(self):
        return self._dates

    @classmethod
    def from_json(cls,
                  jsono: dict,
                  param_name: UCFParameterEnumMember) -> "ScrapperUC":

        hourly_type : ScrapperTypeEnumMember = None
        daily_type : ScrapperTypeEnumMember = None

        if param_name == UCFParameter.WUNDERGROUND:
            suc = WundergroundUC.from_json_object(jsono)
            daily_type = ScrapperType.WUNDERGROUND_DAILY
            hourly_type = ScrapperType.WUNDERGROUND_HOURLY

        elif param_name == UCFParameter.METEOCIEL:
            suc = MeteocielUC.from_json_object(jsono)
            daily_type = ScrapperType.METEOCIEL_DAILY
            hourly_type = ScrapperType.METEOCIEL_HOURLY

        elif param_name == UCFParameter.OGIMET:
            suc = OgimetUC.from_json_object(jsono)
            daily_type = ScrapperType.OGIMET_DAILY
            hourly_type = ScrapperType.OGIMET_HOURLY

        else:
            raise ValueError("ScrapperUC.from_json : scrapper inconnu")

        suc._city = jsono[UCFParameter.CITY.json_name]
        suc._dates = jsono[UCFParameter.DATES.json_name]

        is_hourly = len(suc.dates[0].split("/")) == 3
        suc._scrapper_type = hourly_type if is_hourly else daily_type

        if is_hourly:
            for index, date in enumerate(suc._dates):
                day, month, year = (int(x) for x in date.split("/"))
                max_day = Months.from_id(month).ndays
                if day > max_day:
                    suc._dates[index] = f"{max_day}/{month}/{year}"

        return suc

    @abc.abstractmethod
    def to_tps(self) -> Generator[TaskParameters, Any, None]:
        pass

    @abc.abstractmethod
    def _get_parameters(self) -> List[UCFParameterEnumMember]:
        pass

    def __repr__(self):
        return "<{type} {city} from {start_date} to {end_date}>".format(type=self.scrapper_type,
                                                                        city=self.city,
                                                                        start_date=self.dates[0],
                                                                        end_date=self.dates[-1])

    def __hash__(self):
        x = 7 # à différencier selon les scrappers
        for param in self._get_parameters():
            field_value = self.__dict__[param.field_name]
            if isinstance(field_value, list):
                x = 79 * x + sum([hash(x) for x in field_value])
            else:
                x = 79 * x + hash(field_value)  # à différencier selon les scrappers

        return x

    def __eq__(self, other):

        if other is None:
            return False

        if not isinstance(other, self.__class__):
            return False

        if self.scrapper_type != other.scrapper_type:
            return False

        for param in self._get_parameters():
            try:
                if self.__dict__[param.field_name] != other.__dict__[param.field_name]:
                    return False
            except KeyError:
                return False

        return True


class MeteocielUC(ScrapperUC):

    _PARAMETERS = [UCFParameter.CITY,
                   UCFParameter.CODE,
                   UCFParameter.DATES]

    def __init__(self):
        super().__init__()
        self._code = ""

    @classmethod
    def from_json_object(cls, jsono):
        muc = MeteocielUC()
        muc._code = jsono[UCFParameter.CODE.json_name]
        return muc

    def to_tps(self):

        should_run = True

        if self.scrapper_type == ScrapperType.METEOCIEL_DAILY:

            current_month, current_year = [int(x) for x in self.dates[0].split("/")]

            while should_run:

                yield TPBuilder(self.scrapper_type).with_code(self._code)\
                                                    .with_city(self._city)\
                                                    .with_year(current_year)\
                                                    .with_month(current_month)\
                                                    .build()

                if f"{current_month}/{current_year}" == self.dates[-1]:
                    should_run = False

                current_month = current_month % UCFParameter.MAX_MONTHS + 1
                if current_month == 1:
                    current_year += 1

        elif self.scrapper_type == ScrapperType.METEOCIEL_HOURLY:

            current_day, current_month, current_year = [int(x) for x in self.dates[0].split("/")]

            while should_run:

                yield TPBuilder(self.scrapper_type).with_code(self._code)\
                                                    .with_city(self._city)\
                                                    .with_year(current_year)\
                                                    .with_month(current_month)\
                                                    .with_day(current_day)\
                                                    .build()

                if f"{current_day}/{current_month}/{current_year}" == self.dates[-1]:
                    should_run = False

                current_day = current_day % Months.from_id(current_month).ndays + 1

                if current_day == 1:
                    current_month = current_month % UCFParameter.MAX_MONTHS + 1

                if current_day == 1 and current_month == 1:
                    current_year += 1
        else:
            raise ValueError("MeteocielUC.to_tps : ScrapperType inconnu")


    def _get_parameters(self):
        return self._PARAMETERS


class OgimetUC(ScrapperUC):

    _PARAMETERS = [UCFParameter.CITY,
                   UCFParameter.IND,
                   UCFParameter.DATES]

    def __init__(self):
        super().__init__()
        self._ind = ""

    @classmethod
    def from_json_object(cls, jsono):
        ouc = OgimetUC()
        ouc._ind = jsono[UCFParameter.IND.json_name]
        return ouc

    def to_tps(self):

        should_run = True # permet de faire agir la boucle while comme une do while

        if self.scrapper_type == ScrapperType.OGIMET_DAILY:

            current_month, current_year = [int(x) for x in self.dates[0].split("/")]

            while should_run:

                yield TPBuilder(self.scrapper_type).with_ind(self._ind)\
                                                    .with_city(self._city)\
                                                    .with_year(current_year)\
                                                    .with_month(current_month)\
                                                    .build()
                if f"{current_month}/{current_year}" == self.dates[-1]:
                    should_run = False

                current_month = current_month % UCFParameter.MAX_MONTHS + 1
                if current_month == 1:
                    current_year += 1

        elif self.scrapper_type == ScrapperType.OGIMET_HOURLY:
            # La requête consiste à demander les n derniers jour à partir du jour j.
            # Pour obtenir les infos d'un mois complet, on se met au 31, on demande les 31 derniers jours.
            # Seuls le 1er mois et le dernier doivent faire l'objet d'un paramétrage de l'URL plus fin.
            #
            # Bizarrement, on ne peut pas requêter une page qui contient le 1er janvier sans perdre toutes les données.
            # Si le 1er janvier est inclus dans la demande de l'utilisateur, on force son exclusion.

            current_day, current_month, current_year = [int(x) for x in self.dates[0].split("/")]
            end_day, end_month, end_year = [int(x) for x in self.dates[-1].split("/")]
            has_single_date = len(self.dates) == 1

            if (current_month, current_year) == (end_month, end_year):
                n_days = end_day - current_day + 1
                current_day = end_day
            else:
                n_days = Months.from_id(current_month).ndays - current_day + 1
                current_day = Months.from_id(current_month).ndays

            while should_run:

                if(     Months.from_id(current_month) == Months.JANVIER
                   and  current_day - n_days == 0
                   and not has_single_date):
                    n_days -= 1

                yield TPBuilder(self.scrapper_type).with_ind(self._ind)\
                                                    .with_city(self._city)\
                                                    .with_year(current_year)\
                                                    .with_month(current_month)\
                                                    .with_day(current_day)\
                                                    .with_ndays(n_days)\
                                                    .build()
                if f"{current_day}/{current_month}/{current_year}" == self.dates[-1]:
                    should_run = False

                current_month = current_month % UCFParameter.MAX_MONTHS + 1
                if current_month == 1:
                    current_year += 1

                if (current_month, current_year) == (end_month, end_year):
                    current_day = min(end_day, Months.from_id(current_month).ndays)
                else:
                    current_day = Months.from_id(current_month).ndays

                n_days = current_day

                if(     current_month == 1
                    and current_day - n_days == 0):
                    n_days -= 1
        else:
            raise ValueError("OgimetUC.to_tps : scrapper_type invalide")

    def _get_parameters(self):
        return self._PARAMETERS


class WundergroundUC(ScrapperUC):

    _PARAMETERS = [UCFParameter.CITY,
                   UCFParameter.COUNTRY_CODE,
                   UCFParameter.REGION,
                   UCFParameter.DATES]

    def __init__(self):
        super().__init__()
        self._region = ""
        self._country_code = ""

    @classmethod
    def from_json_object(cls, jsono):
        wuc = WundergroundUC()
        wuc._country_code = jsono[UCFParameter.COUNTRY_CODE.json_name]
        wuc._region = jsono[UCFParameter.REGION.json_name]
        return wuc

    def to_tps(self):

        should_run = True

        if self.scrapper_type == ScrapperType.WUNDERGROUND_DAILY:

            current_month, current_year = [int(x) for x in self.dates[0].split("/")]

            while should_run:
                yield TPBuilder(self.scrapper_type).with_country_code(self._country_code)\
                                                    .with_region(self._region)\
                                                    .with_city(self._city)\
                                                    .with_year(current_year)\
                                                    .with_month(current_month)\
                                                    .build()
                if f"{current_month}/{current_year}" == self.dates[-1]:
                    should_run = False

                current_month = current_month % UCFParameter.MAX_MONTHS + 1
                if current_month == 1:
                    current_year += 1

        elif self.scrapper_type == ScrapperType.WUNDERGROUND_HOURLY:
            raise NotImplementedError("un jour peut être !")
        else:
            raise ValueError("WundergroundUC.to_tps : scrapper_type invalide")

    def _get_parameters(self):
        return self._PARAMETERS
