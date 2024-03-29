from app.boite_a_bonheur.UCFParameterEnum import UCFParameter, UCFParameterEnumMember


class UCFCheckerException(Exception):
    pass


class NoConfigFoundException(UCFCheckerException):
    def __init__(self, path: str):
        super().__init__(f"{path} n'existe pas ou n'est pas un fichier.")


class NotAJsonFileException(UCFCheckerException):
    def __init__(self, path: str):
        super().__init__(f"{path} n'est pas un fichier JSON valide.")


class NotAJsonObjectException(UCFCheckerException):
    def __init__(self, ucfpem: UCFParameterEnumMember):
        super().__init__(f"{ucfpem.name} ne contient pas un objet JSON.")


class NotAJsonListException(UCFCheckerException):
    def __init__(self, ucfpem: UCFParameterEnumMember):
        super().__init__(f"{ucfpem.name} ne contient pas une liste d'objets JSON.")


class EmptyConfigFileException(UCFCheckerException):
    def __init__(self, **kwargs):
        try:
            msg = "{p} ne contient aucun des paramètres {m}, {o} et/ou {w}.".format(p=kwargs.get("path"),
                                                                                    m=UCFParameter.METEOCIEL.name,
                                                                                    o=UCFParameter.OGIMET.name,
                                                                                    w=UCFParameter.WUNDERGROUND.name)
        except KeyError:
            msg = "{m}, {o}, {w} : aucun paramètre détecté".format(m=UCFParameter.METEOCIEL.name,
                                                                   o=UCFParameter.OGIMET.name,
                                                                   w=UCFParameter.WUNDERGROUND.name)
        super().__init__(msg)


class WaitingException(UCFCheckerException):
    def __init__(self):
        super().__init__("{g} doit contenir le paramètre {w}, compris entre {m} et {M}".format(g=UCFParameter.GENERAL_PARAMETERS.name,
                                                                                               w=UCFParameter.WAITING.name,
                                                                                               m=UCFParameter.MIN_WAITING,
                                                                                               M=UCFParameter.MAX_WAITING))


class ScrapperUCException(UCFCheckerException):
    def __init__(self, ucfpem: UCFParameterEnumMember):
        super().__init__(f"{ucfpem.name} doit contenir des objets JSON non vides")


class CommonStrFieldException(UCFCheckerException):
    def __init__(self):
        super().__init__(f"Le paramètre {UCFParameter.CITY} est obligatoire dans toutes les configurations.")


class SpecificStrFieldException(UCFCheckerException):
    def __init__(self, ucfpem: UCFParameterEnumMember):

        if ucfpem == UCFParameter.METEOCIEL:
            first_param = UCFParameter.CODE.name
            second_param = UCFParameter.CODE_NUM.name

        elif ucfpem == UCFParameter.WUNDERGROUND:
            first_param = UCFParameter.REGION.name
            second_param = UCFParameter.COUNTRY_CODE.name

        elif ucfpem == UCFParameter.OGIMET:
            first_param = UCFParameter.IND.name
            second_param = ""

        else:
            raise ValueError(f"SpecificStrFieldException: {ucfpem.name} doit être un des scrappers.")

        if second_param == "":
            msg = f"configurations {ucfpem.name} : le champ {first_param} est obligatoire."

        else:
            msg = f"configurations {ucfpem.name} : les champs {first_param} et {second_param} sont obligatoires."

        super().__init__(msg)


class NoSuchDateFieldException(UCFCheckerException):
    def __init__(self):
        super().__init__("Les champs {y} et {m} sont obligatoires dans toutes les configurations".format(y=UCFParameter.YEARS.name,
                                                                                                         m=UCFParameter.MONTHS.name))


class UnavailableScrapperException(UCFCheckerException):
    def __init__(self, ucfpem: UCFParameterEnumMember):
        super().__init__("Le champ {d} est incompatible avec {ucfpem}".format(d=UCFParameter.DAYS.name,
                                                                              ucfpem=ucfpem.name))


class DateFieldException(UCFCheckerException):
    def __init__(self):
        super().__init__("Les champs {y}, {m} et {d} doivent contenir 1 ou 2 entiers positifs ordonnés".format(y=UCFParameter.YEARS.name,
                                                                                                               m=UCFParameter.COUNTRY_CODE.name,
                                                                                                               d=UCFParameter.DAYS.name))


class YearsDateException(UCFCheckerException):
    def __init__(self):
        super().__init__("La valeur minimum du champ {y} doit être de {m}".format(y=UCFParameter.YEARS.name,
                                                                                  m=UCFParameter.MIN_YEARS))


class MonthsDateException(UCFCheckerException):
    def __init__(self):
        super().__init__("Le champ {m} doit être compris entre {x} et {y}".format(m=UCFParameter.MONTHS.name,
                                                                                  x=UCFParameter.MIN_MONTHS_DAYS_VALUE,
                                                                                  y=UCFParameter.MAX_MONTHS))


class DaysDateException(UCFCheckerException):
    def __init__(self):
        super().__init__("Le champ {d} doit être compris entre {x} et {y}".format(d=UCFParameter.DAYS.name,
                                                                                  x=UCFParameter.MIN_MONTHS_DAYS_VALUE,
                                                                                  y=UCFParameter.MAX_DAYS))
