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
        super().__init__(f"{ucfpem.json_name} n'est pas un objet JSON.")


class NotAJsonListException(UCFCheckerException):
    def __init__(self, ucfpem: UCFParameterEnumMember):
        super().__init__(f"{ucfpem.json_name} n'est pas une liste JSON.")


class EmptyConfigFileException(UCFCheckerException):
    def __init__(self, path: str):
        try:
            msg = "{p} ne contient aucun des paramètres {m}, {o} et/ou {w}.".format(p=path,
                                                                                    m=UCFParameter.METEOCIEL.json_name,
                                                                                    o=UCFParameter.OGIMET.json_name,
                                                                                    w=UCFParameter.WUNDERGROUND.json_name)
        except KeyError:
            msg = "{m}, {o}, {w} : aucun paramètre détecté".format(m=UCFParameter.METEOCIEL.json_name,
                                                                   o=UCFParameter.OGIMET.json_name,
                                                                   w=UCFParameter.WUNDERGROUND.json_name)
        super().__init__(msg)


class ScrapperUCException(UCFCheckerException):
    def __init__(self, scrapper_name: UCFParameterEnumMember):
        super().__init__(f"{scrapper_name.json_name} doit contenir des objets JSON non vides")


class InvalidStrFieldException(UCFCheckerException):
    def __init__(self,
                 scrapper_name: UCFParameterEnumMember,
                 field_name: UCFParameterEnumMember):
        super().__init__(f"configurations {scrapper_name.json_name} : le champ {field_name.json_name} doit être rempli.")


class RequiredFieldException(UCFCheckerException):
    def __init__(self,
                 scrapper_name: UCFParameterEnumMember,
                 field_name: UCFParameterEnumMember):
        super().__init__(f"configurations {scrapper_name.json_name} : le champ {field_name.json_name} est obligatoire.")


class UnavailableScrapperException(UCFCheckerException):
    def __init__(self,
                 scrapper_name: UCFParameterEnumMember,
                 complement: str):
        super().__init__(f"{scrapper_name.json_name} ne peut télécharger des données {complement}")


class DateFieldException(UCFCheckerException):
    def __init__(self):
        super().__init__(f"Le champ {UCFParameter.DATES.json_name} doit être une liste d'1 ou 2 str formatées (jj/)mm/aaaa et ordonnées")


class YearsDateException(UCFCheckerException):
    def __init__(self):
        super().__init__(f"Les années doivent être supérieures à {UCFParameter.MIN_YEARS}")


class MonthsDateException(UCFCheckerException):
    def __init__(self):
        super().__init__(f"Les mois doivent être compris entre {UCFParameter.MIN_MONTHS_DAYS_VALUE} et {UCFParameter.MAX_MONTHS}")


class DaysDateException(UCFCheckerException):
    def __init__(self):
        super().__init__(f"Les jours doivent être compris entre {UCFParameter.MIN_MONTHS_DAYS_VALUE} et {UCFParameter.MAX_DAYS}")


class GeneralParametersFieldException(UCFCheckerException):
    def __init__(self, gpuc_field: UCFParameterEnumMember):

        if gpuc_field == UCFParameter.PARALLELISM:
            msg = f"{UCFParameter.GENERAL_PARAMETERS.json_name} : '{gpuc_field.json_name}' doit être 'true' ou 'false'"
        else:
            msg = f"{UCFParameter.GENERAL_PARAMETERS.json_name} : '{gpuc_field.json_name}' doit être un entier positif (non nul), ou -1."
        super().__init__(msg)
