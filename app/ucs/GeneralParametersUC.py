from app.boite_a_bonheur.UCFParameterEnum import UCFParameter


class GeneralParametersUC:

    INSTANCE = None

    def __init__(self):
        self.waiting = UCFParameter.MIN_WAITING
        raise Exception("GeneralParametersUC : utiliser GeneralParametersUC.get_instance")

    @classmethod
    def get_instance(cls):

        if cls.INSTANCE is None:
            cls.INSTANCE = cls.__new__(cls)
            cls.INSTANCE.waiting = UCFParameter.MIN_WAITING

        return cls.INSTANCE

    @classmethod
    def from_json_object(cls, jsono):

        instance = cls.get_instance()
        try:
            instance.waiting = jsono[UCFParameter.WAITING.name]
        except KeyError:
            pass

        return instance
