class ProcessException(Exception):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec du job",)

        super().__init__(*args, **kwargs)

class HtmlPageException(ProcessException):

    MESSAGE = "Echec de récupération du html"

    def __init__(self):
        super().__init__(self.MESSAGE)

class ScrapException(ProcessException):

    MESSAGE = "Echec de récupération des données de la table html"

    def __init__(self):
        super().__init__(self.MESSAGE)

class ReworkException(ProcessException):

    MESSAGE = "Echec du traitement des données récupérées"

    def __init__(self):
        super().__init__(self.MESSAGE)
