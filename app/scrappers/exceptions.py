class HtmlPageException(Exception):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de récupération de la page html",)

        super().__init__(*args, **kwargs)

class HtmlTableException(Exception):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de récupération de la table dans la page html",)

        super().__init__(*args, **kwargs)

class ScrapException(Exception):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec de récupération des données de la table html",)

        super().__init__(*args, **kwargs)

class ReworkException(Exception):

    def __init__(self, *args, **kwargs):

        if not args:
            args = ("Echec du traitement des données récupérées",)

        super().__init__(*args, **kwargs)
