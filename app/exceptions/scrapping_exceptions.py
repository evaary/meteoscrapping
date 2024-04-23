class ProcessException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class HtmlPageException(Exception):

    MESSAGE = "Echec de récupération du html"

    def __init__(self):
        super().__init__(self.MESSAGE)


class ScrapException(Exception):

    MESSAGE = "Echec de récupération des données de la table html"

    def __init__(self):
        super().__init__(self.MESSAGE)


class ReworkException(Exception):

    MESSAGE = "Echec du traitement des données récupérées"

    def __init__(self):
        super().__init__(self.MESSAGE)
