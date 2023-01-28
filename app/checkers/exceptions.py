class ConfigFileCheckerException(Exception):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de la validation du fichier de configuration",)

        super().__init__(*args, **kwargs)

class NoDictException(ConfigFileCheckerException):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, aucun dictionnaire trouvé",)

        super().__init__(*args, **kwargs)

class UnknownKeysException(ConfigFileCheckerException):
    # pour les clés du dict principal (noms des scrappers + waiting)
    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, il existe des champs inconnus",)

        super().__init__(*args, **kwargs)

class UnknownOrMissingParametersException(ConfigFileCheckerException):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, certains paramètres de configuration manquent ou sont inconnus",)

        super().__init__(*args, **kwargs)

class WaitingException(ConfigFileCheckerException):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, waiting doit être un entier positif",)

        super().__init__(*args, **kwargs)

class DatesException(ConfigFileCheckerException):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, year, month et day doivent être des listes de 1 ou 2 entiers positifs ordonnés",)

        super().__init__(*args, **kwargs)

class MonthsException(ConfigFileCheckerException):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, month doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 12",)

        super().__init__(*args, **kwargs)

class DaysException(ConfigFileCheckerException):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, day doit être une liste de 1 ou 2 entiers positifs ordonnés compris entre 1 et 31",)

        super().__init__(*args, **kwargs)

class OtherFieldsException(ConfigFileCheckerException):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de lecture du fichier, les champs autres que year, month et day doivent être entre \" \" ",)

        super().__init__(*args, **kwargs)
