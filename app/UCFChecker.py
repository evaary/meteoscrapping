import os
from json import JSONDecodeError
from app.boite_a_bonheur.utils import from_json
from app.boite_a_bonheur.UCFParameterEnum import (UCFParameter,
                                                  UCFParameterEnumMember)
from app.exceptions.ucf_checker_exceptions import (DateFieldException,
                                                   DaysDateException,
                                                   MonthsDateException,
                                                   RequiredFieldException,
                                                   UnavailableScrapperException,
                                                   NoConfigFoundException,
                                                   NotAJsonFileException,
                                                   NotAJsonObjectException,
                                                   NotAJsonListException,
                                                   EmptyConfigFileException,
                                                   ScrapperUCException,
                                                   InvalidStrFieldException,
                                                   YearsDateException,
                                                   GeneralParametersFieldException)
from typing import List


class UCFChecker:

    @staticmethod
    def is_valid_str(obj) -> bool:
        return      obj is not None \
                and isinstance(obj, str) \
                and len(obj) != 0

    @staticmethod
    def check_dates_field(uc : dict,
                          scrapper_name: UCFParameterEnumMember) -> None:
        """Détermine si le champ dates est valide ou pas."""
        # (1)   Le champ dates est obligatoire.
        # (2)   Les dates doivent être 1 ou 2 str non vides.
        # (3)   Les dates doivent être au format [j]j/[m]m/aaaa ou [m]m/aaaa, mais pas de mélange.
        # (4)   Les j, m, a doivent être des int.
        # (5)   Wunderground n'est pas disponible en version jour par jour.
        # (6)   Les années doivent valoir au minimum 1800.
        #       Les mois doivent être compris entre 1 et 12.
        #       Les jours doivent être compris entre 1 et le jour max du mois.
        #
        # (7)   Les dates doivent être ordonnées

        if scrapper_name not in UCFParameter.SCRAPPERS:
            raise ValueError("UCFChecker.check_date_field : {x} doit être {m}, {o}, ou {w}".format(x=scrapper_name.json_name,
                                                                                                   m=UCFParameter.METEOCIEL.json_name,
                                                                                                   o=UCFParameter.OGIMET.json_name,
                                                                                                   w=UCFParameter.WUNDERGROUND.json_name))
        # (1)
        try:
            dates: List[str] = uc[UCFParameter.DATES.json_name]
        except KeyError:
            raise RequiredFieldException(scrapper_name, UCFParameter.DATES)
        # (2)
        if not isinstance(dates, list):
            raise NotAJsonListException(UCFParameter.DATES)

        if not(len(dates) <= 2):
            raise DateFieldException()

        if not all([UCFChecker.is_valid_str(x) for x in dates]):
            raise DateFieldException()
        # (3)
        if not all([ len(x.split("/")) in (2,3) for x in dates ]):
            raise DateFieldException()

        dates_sizes = {len(x.split("/")) for x in dates}
        if len(dates_sizes) != 1:
            raise DateFieldException()
        # (4)
        try:
            [ int(x)
             for string in dates
             for x in string.split("/") ]
        except ValueError:
            raise DateFieldException()
        # (5)
        if dates_sizes.pop() == 3 and scrapper_name == UCFParameter.WUNDERGROUND:
            raise UnavailableScrapperException(scrapper_name, "par heure")
        # (6)
        for date in dates:
            *day, month, year = (int(x) for x in date.split("/"))

            if year < UCFParameter.MIN_YEARS:
                raise YearsDateException()

            if month not in range(UCFParameter.MIN_MONTHS_DAYS_VALUE,
                                  UCFParameter.MAX_MONTHS + 1):
                raise MonthsDateException()

            if day and day[0] not in range(UCFParameter.MIN_MONTHS_DAYS_VALUE,
                                           UCFParameter.MAX_DAYS + 1):
                raise DaysDateException()
        # (7)
        if len(dates) == 2:
            *start_day, start_month, start_year = (int(x) for x in dates[0].split("/"))
            *end_day, end_month, end_year = (int(x) for x in dates[1].split("/"))

            if start_year > end_year:
                raise DateFieldException()

            if start_year == end_year and start_month > end_month:
                raise DateFieldException()

            if start_day:
                if(     start_year == end_year
                    and  start_month == end_month
                    and  start_day[0] > end_day[0]):
                    raise DateFieldException()

    @staticmethod
    def check_ucf_existence(path_to_config: str) -> None:
        is_valid =      os.path.exists(path_to_config)\
                    and os.path.isfile(path_to_config)
        if not is_valid:
            raise NoConfigFoundException(path_to_config)

    @staticmethod
    def check_ucf_structure(path_to_config: str) -> dict:
        """Contrôle de la validité du fichier config"""
        #   (1) On tente de lire le fichier config.
        #   (2) Le fichier config doit contenir un dict.
        #   (3) Les paramètres pour chaque scrapper doivent être des listes.
        #       scrapper_presence associe ces paramètres à leur état de présence (True = présent, par défaut)
        #   (4) Chacun de ces paramètres est optionnel, mais il en faut au moins 1.
        #   (5) On teste la présence des paramètres généraux, champs optionnel.

        # (1)
        try:
            config_file: dict = from_json(path_to_config)
        except JSONDecodeError:
            raise NotAJsonFileException(path_to_config)
        # (2)
        if not isinstance(config_file, dict):
            raise NotAJsonObjectException(UCFParameter.UCF)
        # (3)
        scrapper_presence = {UCFParameter.METEOCIEL: True,
                             UCFParameter.OGIMET: True,
                             UCFParameter.WUNDERGROUND: True}

        for array_field in scrapper_presence.keys():
            try:
                if not isinstance(config_file[array_field.json_name], list):
                    raise NotAJsonListException(array_field)
            except KeyError:
                scrapper_presence[array_field] = False
        # (4)
        if not any(scrapper_presence.values()):
            raise EmptyConfigFileException(path_to_config)

        # (5)
        try:
            if not isinstance(config_file[UCFParameter.GENERAL_PARAMETERS.json_name], dict):
                raise NotAJsonObjectException(UCFParameter.GENERAL_PARAMETERS)
        except KeyError:
            pass

        return config_file

    @staticmethod
    def check_general_parameters(config: dict):

        try:
            gpuc = config[UCFParameter.GENERAL_PARAMETERS.json_name]
        except KeyError:
            return

        try:
            should_download_in_parallel = gpuc[UCFParameter.PARALLELISM.json_name]
            if not isinstance(should_download_in_parallel, bool):
                raise GeneralParametersFieldException(UCFParameter.PARALLELISM)
        except KeyError:
            raise RequiredFieldException(UCFParameter.GENERAL_PARAMETERS,
                                         UCFParameter.PARALLELISM)

        try:
            max_cpus = int(gpuc[UCFParameter.CPUS.json_name])
            if max_cpus < -1 or max_cpus == 0:
                raise GeneralParametersFieldException(UCFParameter.CPUS)
        except KeyError:
            raise RequiredFieldException(UCFParameter.GENERAL_PARAMETERS,
                                         UCFParameter.CPUS)
        except ValueError:
            raise GeneralParametersFieldException(UCFParameter.CPUS)

    @staticmethod
    def check_scrappers(config: dict) -> None:
        """Contrôle la validité de la structures des paramètres des scrappers"""
        # Chacun des paramètres meteociel, ogimet et wunderground sont optionnels,
        # mais s'ils sont présents, ils doivent contenir des objets JSON non vides.
        # Au moins un des champs présents ne doit pas être vide.

        all_configs = []
        for scrapper_name in UCFParameter.SCRAPPERS:
            try:
                json_obj_list = config[scrapper_name.json_name]
            except KeyError:
                continue

            if not all([isinstance(x, dict) and len(x) != 0 for x in json_obj_list]):
                raise ScrapperUCException(scrapper_name)

            all_configs.extend(json_obj_list)

        if len(all_configs) == 0:
            raise EmptyConfigFileException()

    @classmethod
    def check_ucs(cls, config: dict) -> None:

        for scrapper_name in UCFParameter.SCRAPPERS:
            try:
                ucs = config[scrapper_name.json_name]
            except KeyError:
                continue

            for uc in ucs:
                cls.check_uc(uc, scrapper_name)

    @classmethod
    def check_uc(cls,
                 uc: dict,
                 scrapper_name: UCFParameterEnumMember):
        """Détermine si un UC du fichier de configuration est valide ou pas"""
        #   (1) On vérifie que les champs str spécifiques au scrapper sont présents et bien remplis.
        #   (2) On vérifie que les champs str communs sont présents et bien remplis.
        #   (3) On vérifie que le champ dates est présent et bien remplis.
        if scrapper_name not in UCFParameter.SCRAPPERS:
            raise ValueError("UCFChecker.check_individual_uc : scrapper_name doit être un scrapper")

        # (1)
        for x in UCFParameter.SPECIFIC_FIELDS[scrapper_name]:
            try:
                if not cls.is_valid_str(uc[x.json_name]):
                    raise InvalidStrFieldException(scrapper_name, x)
            except KeyError:
                raise RequiredFieldException(scrapper_name, x)
        # (2)
        for x in UCFParameter.COMMON_FIELDS:
            try:
                if not cls.is_valid_str(uc[x.json_name]):
                    raise InvalidStrFieldException(scrapper_name, x)
            except KeyError:
                raise RequiredFieldException(scrapper_name, x)
        # (3)
        cls.check_dates_field(uc, scrapper_name)

    @classmethod
    def check(cls, path: str) -> dict:
        cls.check_ucf_existence(path)
        config = cls.check_ucf_structure(path)
        cls.check_general_parameters(config)
        cls.check_scrappers(config)
        cls.check_ucs(config)

        return config
