import os
from json import JSONDecodeError
from app.boite_a_bonheur.utils import from_json
from app.boite_a_bonheur.UCFParameterEnum import (UCFParameter,
                                                  UCFParameterEnumMember)
from app.ucs.ucf_checker_exceptions import (DateFieldException,
                                            DaysDateException,
                                            MonthsDateException,
                                            NoSuchDateFieldException,
                                            UnavailableScrapperException,
                                            WaitingException,
                                            NoConfigFoundException,
                                            NotAJsonFileException,
                                            NotAJsonObjectException,
                                            NotAJsonListException,
                                            EmptyConfigFileException,
                                            ScrapperUCException,
                                            CommonStrFieldException,
                                            SpecificStrFieldException,
                                            YearsDateException)


class UCFChecker:

    @staticmethod
    def is_valid_str(obj) -> bool:
        return      obj is not None \
                and isinstance(obj, str) \
                and len(obj) != 0

    @staticmethod
    def check_date_field(obj,
                         date_field: UCFParameterEnumMember,
                         scrapper_name: UCFParameterEnumMember) -> None:

        if date_field not in UCFParameter.dates_parameters():
            raise ValueError("UCFChecker.check_date_field : {f} doit être {y}, {m}, ou {d}".format(f=date_field.name,
                                                                                                   y=UCFParameter.YEARS.name,
                                                                                                   m=UCFParameter.MONTHS.name,
                                                                                                   d=UCFParameter.DAYS.name))
        if scrapper_name not in UCFParameter.scrappers_parameters():
            raise ValueError("UCFChecker.check_date_field : {x} doit être {m}, {o}, ou {w}".format(x=scrapper_name.name,
                                                                                                   m=UCFParameter.METEOCIEL.name,
                                                                                                   o=UCFParameter.OGIMET.name,
                                                                                                   w=UCFParameter.WUNDERGROUND.name))
        is_year = date_field == UCFParameter.YEARS
        is_month = date_field == UCFParameter.MONTHS
        is_day = date_field == UCFParameter.DAYS

        if is_day and scrapper_name == UCFParameter.WUNDERGROUND:
            raise UnavailableScrapperException(scrapper_name)

        if not isinstance(obj, list):
            raise NotAJsonListException(date_field)

        if len(obj) not in (1, UCFParameter.MAX_DATE_FIELD_SIZE):
            raise DateFieldException()

        if not all([isinstance(x, int) for x in obj]):
            raise DateFieldException()

        if obj[0] > obj[-1]:
            raise DateFieldException()

        if is_year and obj[0] < UCFParameter.MIN_YEARS:
            raise YearsDateException()

        if is_month and any([x not in range(UCFParameter.MIN_MONTHS_DAYS_VALUE,
                                            UCFParameter.MAX_MONTHS + 1) for x in obj]):
            raise MonthsDateException()

        if is_day and any([x not in range(UCFParameter.MIN_MONTHS_DAYS_VALUE,
                                          UCFParameter.MAX_DAYS + 1) for x in obj]):
            raise DaysDateException()

    @staticmethod
    def check_ucf_existence(path_to_config: str) -> None:

        is_valid =      os.path.exists(path_to_config)\
                    and os.path.isfile(path_to_config)
        if not is_valid:
            raise NoConfigFoundException(path_to_config)

    @staticmethod
    def check_ucf_structure(path_to_config: str) -> dict:

        #   (1) On tente de lire le fichier config
        #   (2) Le fichier config doit contenir un dict
        #   (3) Les paramètres généraux doivent être un dict. Ils sont optionnels.
        #   (4) Les paramètres pour chaque scrapper doivent être des listes.
        #       json_array_parameters associe ces paramètres à leur état de présence (True = présent, par défaut)
        #   (5) Chacun de ces paramètres est optionnel, mais il en faut au moins 1.

        # (1)
        try:
            config_file: dict = from_json(path_to_config)
        except JSONDecodeError:
            raise NotAJsonFileException(path_to_config)
        # (2)
        if not isinstance(config_file, dict):
            raise NotAJsonObjectException(UCFParameter.UCF)
        # (3)
        try:
            if not isinstance(config_file[UCFParameter.GENERAL_PARAMETERS.name], dict):
                raise NotAJsonObjectException(UCFParameter.GENERAL_PARAMETERS)
        except KeyError:
            pass
        # (4)
        json_array_parameters = {UCFParameter.METEOCIEL: True,
                                 UCFParameter.OGIMET: True,
                                 UCFParameter.WUNDERGROUND: True}

        for array_field in json_array_parameters.keys():
            try:
                if not isinstance(config_file[array_field.name], list):
                    raise NotAJsonListException(array_field)
            except KeyError:
                json_array_parameters[array_field] = False
        # (5)
        is_valid = any(json_array_parameters.values())

        if not is_valid:
            raise EmptyConfigFileException(path=path_to_config)

        return config_file

    @staticmethod
    def _check_general_parameters_content(config: dict) -> None:

        #   (1) Les paramètres généraux sont optionnels, mais s'ils existent dans la config,
        #       ils doivent contenir le waiting (temps à attendre pour que s'éxecute le JS de la page à scrapper).
        #   (2) Le waiting doit être un entier ...
        #   (3) ...compris entre le min et le max définis.

        # (1)
        try:
            gen_param = config[UCFParameter.GENERAL_PARAMETERS.name]
        except KeyError:
            return

        try:
            waiting = gen_param[UCFParameter.WAITING.name]
        except KeyError:
            raise WaitingException()
        # (2)
        if not isinstance(waiting, int):
            raise WaitingException()
        # (3)
        if waiting not in range(UCFParameter.MIN_WAITING,
                                UCFParameter.MAX_WAITING + 1):
            raise WaitingException()

    @staticmethod
    def check_scrapper_parameters_content(config: dict) -> None:
        # Chacun des paramètres meteociel, ogimet et wunderground sont optionnels,
        # mais s'ils sont présents, ils doivent contenir des objets JSON non vides.
        # Au moins un des champs présents ne doit pas être vide.

        all_configs = []

        try:
            json_obj_list = config[UCFParameter.METEOCIEL.name]
            if not all([isinstance(x, dict) and len(x) != 0 for x in json_obj_list]):
                raise ScrapperUCException(UCFParameter.METEOCIEL)
            all_configs.extend(json_obj_list)
        except KeyError:
            pass

        try:
            json_obj_list = config[UCFParameter.OGIMET.name]
            if not all([isinstance(x, dict) and len(x) != 0 for x in json_obj_list]):
                raise ScrapperUCException(UCFParameter.OGIMET)
            all_configs.extend(json_obj_list)
        except KeyError:
            pass

        try:
            json_obj_list = config[UCFParameter.WUNDERGROUND.name]
            if not all([isinstance(x, dict) and len(x) != 0 for x in json_obj_list]):
                raise ScrapperUCException(UCFParameter.WUNDERGROUND)
            all_configs.extend(json_obj_list)
        except KeyError:
            pass

        if len(all_configs) == 0:
            raise EmptyConfigFileException()

    @classmethod
    def check_ucs(cls, config: dict) -> None:

        ucs = []
        try:
            ucs = config[UCFParameter.WUNDERGROUND.name]
        except KeyError:
            pass

        for wuc in ucs:
            cls.check_individual_uc(wuc, UCFParameter.WUNDERGROUND)

        ucs = []
        try:
            ucs = config[UCFParameter.METEOCIEL.name]
        except KeyError:
            pass

        for muc in ucs:
            cls.check_individual_uc(muc, UCFParameter.METEOCIEL)

        ucs = []
        try:
            ucs = config[UCFParameter.OGIMET.name]
        except KeyError:
            pass

        for ouc in ucs:
            cls.check_individual_uc(ouc, UCFParameter.OGIMET)

    @classmethod
    def check_individual_uc(cls, uc, scrapper_name: UCFParameterEnumMember):

        if scrapper_name not in UCFParameter.scrappers_parameters():
            raise ValueError(
                "UCFChecker.check_individual_uc : {x} doit être {m}, {o}, ou {w}".format(x=scrapper_name.name,
                                                                                         m=UCFParameter.METEOCIEL.name,
                                                                                         o=UCFParameter.OGIMET.name,
                                                                                         w=UCFParameter.WUNDERGROUND.name))
        if scrapper_name == UCFParameter.WUNDERGROUND:
            specific_str_fields = [UCFParameter.REGION,
                                   UCFParameter.COUNTRY_CODE]

        elif scrapper_name == UCFParameter.METEOCIEL:
            specific_str_fields = [UCFParameter.CODE,
                                   UCFParameter.CODE_NUM]
        else:
            specific_str_fields = [UCFParameter.IND]

        try:
            if not all([cls.is_valid_str(uc[x.name]) for x in specific_str_fields]):
                raise SpecificStrFieldException(scrapper_name)
        except KeyError:
            raise SpecificStrFieldException(scrapper_name)

        common_str_fields = [UCFParameter.CITY]
        try:
            if not all([cls.is_valid_str(uc[x.name]) for x in common_str_fields]):
                raise CommonStrFieldException()
        except KeyError:
            raise CommonStrFieldException()

        date_fields = [UCFParameter.YEARS,
                       UCFParameter.MONTHS,
                       UCFParameter.DAYS]

        for date_field in date_fields:
            try:
                cls.check_date_field(uc[date_field.name],
                                     date_field,
                                     scrapper_name)
            except KeyError:
                if date_field != UCFParameter.DAYS:
                    raise NoSuchDateFieldException()

    @classmethod
    def check(cls, path: str) -> dict:
        cls.check_ucf_existence(path)
        config = cls.check_ucf_structure(path)
        cls._check_general_parameters_content(config)
        cls.check_scrapper_parameters_content(config)
        cls.check_ucs(config)

        return config
