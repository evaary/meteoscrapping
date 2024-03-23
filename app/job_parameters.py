from abc import ABC, abstractclassmethod
from string import Template

from app import utils


class JobParametersBuilder:

    MIN_YEAR = 1

    MIN_MONTH = 1
    MAX_MONTH = 12

    MIN_DAY = 1
    MAX_DAY = 31

    MIN_WAITING = 0
    DEFAULT_WAITING = 3

    def __init__(self) -> None:

        # communs à toutes les configs
        self.city = ""
        self.year = 0
        self.month = 0
        self.year_str = str(self.year)
        self.month_str = "0" + str(self.month) if self.month < 10 else str(self.month)
        self.waiting = 0

        # wunderground mensuel
        self.country_code = ""
        self.region = ""

        # ogimet mensuel
        self.ind = ""

        # meteociel mensuel / quotidien
        self.code_num = ""
        self.code = ""

        # meteociel quotidien
        self.day = 0
        self.day_str = "0" + str(self.day) if self.day < 10 else str(self.day)

    def add_city(self, city: str) -> "JobParametersBuilder":

        if not isinstance(city, str):
            raise ValueError("__city doit être une str")

        self.city = city

        return self

    def add_year(self, year: int) -> "JobParametersBuilder":

        if (   not isinstance(year, int)
            or year < self.MIN_YEAR ):

            raise ValueError("year doit être un entier positif")

        self.year = year
        self.year_str = str(year)

        return self

    def add_month(self, month: int) -> "JobParametersBuilder":

        if (   not isinstance(month, int)
            or month < self.MIN_MONTH
            or month > self.MAX_MONTH ):

            raise ValueError(f"month doit être un entier compris entre {self.MIN_MONTH} et {self.MAX_MONTH}")

        self.month = month
        self.month_str = "0" + str(month) if month < 10 else str(month)

        return self

    def add_day(self, day: int) -> "JobParametersBuilder":

        if (   not isinstance(day, int)
            or day < self.MIN_DAY
            or day > self.MAX_DAY):

            raise ValueError(f"day doit être un entier compris entre {self.MIN_DAY} et {self.MAX_DAY}")

        self.day = day
        self.day_str = "0" + str(self.day) if self.day < 10 else str(self.day)

        return self

    def add_country_code(self, country_code: str) -> "JobParametersBuilder":

        if not isinstance(country_code, str):
            raise ValueError("country_code doit être une str")

        self.country_code = country_code

        return self

    def add_region(self, region: str) -> "JobParametersBuilder":

        if not isinstance(region, str):
            raise ValueError("region doit être une str")

        self.region = region

        return self

    def add_ind(self, ind: str) -> "JobParametersBuilder":

        if not isinstance(ind, str):
            raise ValueError("ind doit être une str")

        self.ind = ind

        return self

    def add_code_num(self, code_num: str) -> "JobParametersBuilder":

        if not isinstance(code_num, str):
            raise ValueError("code_num doit être une str")

        self.code_num = code_num

        return self

    def add_code(self, code: str) -> "JobParametersBuilder":

        if not isinstance(code, str):
            raise ValueError("code doit être une str")

        self.code = code

        return self

    def add_waiting(self, waiting : int) -> "JobParametersBuilder":

        if (not isinstance(waiting, int)
            or waiting < self.MIN_WAITING):

            raise ValueError("waiting doit être un entier positif")

        self.waiting = waiting

        return self

    def build_wunderground_monthly_parameters(self) -> "WundergroundMonthlyParameters":
        return WundergroundMonthlyParameters(self)

    def build_ogimet_monthly_parameters(self) -> "OgimetMonthlyParameters":
        return OgimetMonthlyParameters(self)

    def build_meteociel_monthly_parameters(self) -> "MeteocielMonthlyParameters":
        return MeteocielMonthlyParameters(self)

    def build_meteociel_daily_parameters(self) -> "MeteocielDailyParameters":
        return MeteocielDailyParameters(self)

    @classmethod
    def build_wunderground_monthly_parameters_generator_from_config(cls, config) -> "tuple[WundergroundMonthlyParameters]":

        waiting_to_add = cls.DEFAULT_WAITING

        try:
            waiting_to_add = config["waiting"]
        except KeyError:
            pass

        return (

            JobParametersBuilder().add_city( config["__city"] )
                                  .add_country_code( config["country_code"] )
                                  .add_region( config["region"] )
                                  .add_waiting(waiting_to_add)
                                  .add_year(year)
                                  .add_month(month)
                                  .build_wunderground_monthly_parameters()

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)
        )

    @classmethod
    def build_ogimet_monthly_parameters_generator_from_config(cls, config) -> "tuple[OgimetMonthlyParameters]":

        waiting_to_add = cls.DEFAULT_WAITING

        try:
            waiting_to_add = config["waiting"]
        except KeyError:
            pass

        return (

            JobParametersBuilder().add_city( config["__city"] )
                                  .add_ind( config["ind"] )
                                  .add_waiting(waiting_to_add)
                                  .add_year(year)
                                  .add_month(month)
                                  .build_ogimet_monthly_parameters()

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)
        )

    @classmethod
    def build_meteociel_monthly_parameters_generator_from_config(cls, config) -> "tuple[MeteocielMonthlyParameters]":

        waiting_to_add = cls.DEFAULT_WAITING

        try:
            waiting_to_add = config["waiting"]
        except KeyError:
            pass

        return (

            JobParametersBuilder().add_city( config["__city"] )
                                  .add_code_num( config["code_num"] )
                                  .add_code( config["code"] )
                                  .add_waiting(waiting_to_add)
                                  .add_year(year)
                                  .add_month(month)
                                  .build_meteociel_monthly_parameters()

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)
        )

    @classmethod
    def build_meteociel_daily_parameters_generator_from_config(cls, config) -> "tuple[MeteocielDailyParameters]":

        waiting_to_add = cls.DEFAULT_WAITING

        try:
            waiting_to_add = config["waiting"]
        except KeyError:
            pass

        return (

            JobParametersBuilder().add_city( config["__city"] )
                                  .add_code_num( config["code_num"] )
                                  .add_code( config["code"] )
                                  .add_waiting(waiting_to_add)
                                  .add_year(year)
                                  .add_month(month)
                                  .add_day(day)
                                  .build_meteociel_daily_parameters()

            for year in range(config["year"][0],
                              config["year"][-1] + 1)

            for month in range(config["month"][0],
                               config["month"][-1] + 1)

            for day in range(config["day"][0],
                             config["day"][-1] + 1)

            if day <= utils.DAYS[month]
        )



class JobParameters(ABC):

    def __init__(self, builder: JobParametersBuilder) -> None:
        self.city = builder.city
        self.year = builder.year
        self.month = builder.month
        self.year_str = builder.year_str
        self.month_str = builder.month_str
        self.waiting = builder.waiting
        self.url = self._build_url(builder)
        self.criteria = self._get_criteria()
        self.key = self._get_key(builder)

    @abstractclassmethod
    def _build_url(cls, builder: JobParametersBuilder):
        pass

    @abstractclassmethod
    def _get_criteria(cls):
        pass

    @staticmethod
    def _get_key(builder: JobParametersBuilder):
        return f"{builder.city}_{builder.year_str}_{builder.month_str}"



class WundergroundMonthlyParameters(JobParameters):

    BASE_URL = Template("https://www.wunderground.com/history/monthly/$country_code/$city/$region/date/$year-$month")

    # Critère de sélection qui sert à retrouver le tableau de donner dans la page html
    CRITERIA = ("aria-labelledby", "History __days")

    def __init__(self, builder: JobParametersBuilder) -> None:
        super().__init__(builder)
        self.country_code = builder.country_code
        self.region = builder.region

    # override
    @classmethod
    def _build_url(cls, builder: JobParametersBuilder):

        return cls.BASE_URL.substitute( country_code=builder.country_code,
                                        city=builder.city,
                                        region=builder.region,
                                        year=builder.year,
                                        month=builder.month )

    # override
    @classmethod
    def _get_criteria(cls):
        return cls.CRITERIA



class OgimetMonthlyParameters(JobParameters):

    # La numérotation des mois sur ogimet est décalée.
    # Ce dictionnaire associe la numérotation usuelle (clés) et celle d'ogimet (valeurs).
    NUMEROTATIONS = { 1  :  2,
                      2  :  3,
                      3  :  4,
                      4  :  5,
                      5  :  6,
                      6  :  7,
                      7  :  8,
                      8  :  9,
                      9  : 10,
                      10 : 11,
                      11 : 12,
                      12 :  1 }

    BASE_URL = Template(f"http://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=$ind&ano=$ano&mes=$mes&day=0&hora=0&min=0&ndays=$ndays")

    # Critère de sélection qui sert à retrouver le tableau de donneées dans la page html.
    CRITERIA = ("bgcolor", "#d0d0d0")

    def __init__(self, builder: JobParametersBuilder) -> None:
        super().__init__(builder)
        self.ind = builder.ind

    # override
    @classmethod
    def _build_url(cls, builder: JobParametersBuilder):

        return cls.BASE_URL.substitute( ind=builder.ind,
                                        ano=builder.year,
                                        mes=cls.NUMEROTATIONS[builder.month],
                                        ndays=utils.DAYS[builder.month] )

    # override
    @classmethod
    def _get_criteria(cls):
        return cls.CRITERIA



class MeteocielMonthlyParameters(JobParameters):

    BASE_URL = Template("https://www.meteociel.com/climatologie/obs_villes.php?code$code_num=$code&mois=$mois&annee=$annee")

    # Critère de sélection qui sert à retrouver le tableau de donner dans la page html
    CRITERIA = ("cellpadding", "2")

    def __init__(self, builder: JobParametersBuilder) -> None:
        super().__init__(builder)
        self.code_num = builder.code_num
        self.code = builder.code

    # override
    @classmethod
    def _build_url(cls, builder: JobParametersBuilder):

        return cls.BASE_URL.substitute( code_num = builder.code_num,
                                        code = builder.code,
                                        mois = builder.month,
                                        annee = builder.year )

    # override
    @classmethod
    def _get_criteria(cls):
        return cls.CRITERIA



class MeteocielDailyParameters(JobParameters):

    # La numérotation des mois sur météociel par jour est décalée.
    # Ce dictionnaire associe la numérotation usuelle (clés) et celle de météociel (valeurs).
    NUMEROTATIONS = { 1  :  0,
                      2  :  1,
                      3  :  2,
                      4  :  3,
                      5  :  4,
                      6  :  5,
                      7  :  6,
                      8  :  7,
                      9  :  8,
                      10 :  9,
                      11 : 10,
                      12 : 11 }

    BASE_URL = Template("https://www.meteociel.com/temps-reel/obs_villes.php?code$code_num=$code&jour2=$jour2&mois2=$mois2&annee2=$annee2")

    # Critère de sélection qui sert à retrouver le tableau de donner dans la page html
    CRITERIA = ("bgcolor", "#EBFAF7")

    def __init__(self, builder: JobParametersBuilder) -> None:
        super().__init__(builder)
        self.code_num = builder.code_num
        self.code = builder.code
        self.day = builder.day
        self.day_str = builder.day_str

    # override
    @classmethod
    def _build_url(cls, buidler: JobParametersBuilder):

        return cls.BASE_URL.substitute( code_num=buidler.code_num,
                                        code=buidler.code,
                                        jour2=buidler.day,
                                        mois2=cls.NUMEROTATIONS[buidler.month],
                                        annee2=buidler.year )

    # override
    @classmethod
    def _get_criteria(cls):
        return cls.CRITERIA

    # override
    @staticmethod
    def _get_key(builder):
        return f"{builder.city}_{builder.year_str}_{builder.month_str}_{builder.day_str}"
