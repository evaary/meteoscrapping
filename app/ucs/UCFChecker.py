import os
from json import JSONDecodeError
from app.boite_a_bonheur.utils import from_json
from app.boite_a_bonheur.UCFParameterEnum import (UCFParameter,
                                                  UCFParameterEnumMember)
from app.ucs.ucf_checker_exceptions import (DateFieldException,
                                            DaysDateException,
                                            MonthsDateException,
                                            RequiredDateFieldException,
                                            UnavailableScrapperException,
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
        """Détermine si un champ date est valide ou pas."""

        """
        (1) Wunderground n'est pas disponible en version jour par jour.
        (2) Les champs date doivent être des listes ordonnées de max 2 entiers positifs.
            Les années doivent valoir au minimum 1800.
            Les mois doivent être compris entre 1 et 12.
            Les jours doivent être compris entre 1 et 31.
        """

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
        # (1)
        if is_day and scrapper_name == UCFParameter.WUNDERGROUND:
            raise UnavailableScrapperException(scrapper_name)
        # (2)
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
        """"""
        """
        (1) On tente de lire le fichier config.
        (2) Le fichier config doit contenir un dict.
        (3) Les paramètres pour chaque scrapper doivent être des listes.
            scrapper_presence associe ces paramètres à leur état de présence (True = présent, par défaut)
        (4) Chacun de ces paramètres est optionnel, mais il en faut au moins 1.
        """
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
                if not isinstance(config_file[array_field.name], list):
                    raise NotAJsonListException(array_field)
            except KeyError:
                scrapper_presence[array_field] = False
        # (4)
        if not any(scrapper_presence.values()):
            raise EmptyConfigFileException(path=path_to_config)

        return config_file

    @staticmethod
    def check_scrappers(config: dict) -> None:
        """"""
        """
        Chacun des paramètres meteociel, ogimet et wunderground sont optionnels,
        mais s'ils sont présents, ils doivent contenir des objets JSON non vides.
        Au moins un des champs présents ne doit pas être vide.
        """

        all_configs = []
        for ucfparameter in [UCFParameter.METEOCIEL,
                             UCFParameter.OGIMET,
                             UCFParameter.WUNDERGROUND]:
            try:
                json_obj_list = config[ucfparameter.name]
            except KeyError:
                continue

            if not all([isinstance(x, dict) and len(x) != 0 for x in json_obj_list]):
                raise ScrapperUCException(UCFParameter.METEOCIEL)

            all_configs.extend(json_obj_list)

        if len(all_configs) == 0:
            raise EmptyConfigFileException()

    @classmethod
    def check_ucs(cls, config: dict) -> None:

        for ucfparameter in [UCFParameter.METEOCIEL,
                             UCFParameter.OGIMET,
                             UCFParameter.WUNDERGROUND]:
            try:
                ucs = config[ucfparameter.name]
            except KeyError:
                continue

            for uc in ucs:
                cls.check_uc(uc, ucfparameter)

    @classmethod
    def check_uc(cls, uc, scrapper_name: UCFParameterEnumMember):
        """Détermine si un UC du fichier de configuration est valide ou pas"""

        """
        (1) On vérifie que les champs str spécifiques au scrapper sont bien remplis.
        (2) On vérifie que les champs str communs sont bien remplis.
        (3) On vérifie que tous les champs dates sont bien présents. Jours n'est pas obligatoire.
        """
        if scrapper_name not in UCFParameter.scrappers_parameters():
            raise ValueError("UCFChecker.check_individual_uc : {x} doit être {m}, {o}, ou {w}".format(x=scrapper_name.name,
                                                                                                      m=UCFParameter.METEOCIEL.name,
                                                                                                      o=UCFParameter.OGIMET.name,
                                                                                                      w=UCFParameter.WUNDERGROUND.name))
        try:
            specific_str_fields = UCFParameter.specific_fields_by_scrapper(scrapper_name)
        except KeyError:
            raise ValueError(f"UCFChecker.check_individual_uc : scrapper_name invalide : {scrapper_name}")
        # (1)
        try:
            if not all([cls.is_valid_str(uc[x.name]) for x in specific_str_fields]):
                raise SpecificStrFieldException(scrapper_name)
        except KeyError:
            raise SpecificStrFieldException(scrapper_name)
        # (2)
        try:
            if not all([cls.is_valid_str(uc[x.name]) for x in UCFParameter.COMMON_FIELDS]):
                raise CommonStrFieldException()
        except KeyError:
            raise CommonStrFieldException()
        # (3)
        for date_field in UCFParameter.DATE_FIELDS:
            try:
                cls.check_date_field(uc[date_field.name],
                                     date_field,
                                     scrapper_name)
            except KeyError:
                if date_field != UCFParameter.DAYS:  # jours n'est pas obligatoire
                    raise RequiredDateFieldException()

    @classmethod
    def check(cls, path: str) -> dict:
        cls.check_ucf_existence(path)
        config = cls.check_ucf_structure(path)
        cls.check_scrappers(config)
        cls.check_ucs(config)

        return config
