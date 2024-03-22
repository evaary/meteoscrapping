import copy

from app.boite_a_bonheur.UCFParameterEnum import UCFParameter
from app.ucs.GeneralParametersUC import GeneralParametersUC
from app.ucs.ucs_module import ScrapperUC
from app.ucs.UCFChecker import UCFChecker


class UserConfigFile:

    def __init__(self):
        self.ogimet_ucs = []
        self.meteociel_ucs = []
        self.wunderground_ucs = []

        raise Exception("UserConfigFile : utiliser from_json")

    @classmethod
    def from_json(cls, path_to_ucf):

        config_file = UCFChecker.check(path_to_ucf)
        ucf = UserConfigFile.__new__(cls)

        try:
            GeneralParametersUC.from_json_object(config_file[UCFParameter.GENERAL_PARAMETERS.name])
        except KeyError:
            pass

        try:
            oucs = config_file[UCFParameter.OGIMET.name]
            ucf.ogimet_ucs = list(set([ScrapperUC.from_json_object(ouc, UCFParameter.OGIMET) for ouc in oucs]))
        except KeyError:
            pass

        try:
            mucs = config_file[UCFParameter.METEOCIEL.name]
            ucf.meteociel_ucs = list(set([  ScrapperUC.from_json_object(muc, UCFParameter.METEOCIEL)
                                            for muc in mucs]))
        except KeyError:
            pass

        try:
            wucs = config_file[UCFParameter.WUNDERGROUND.name]
            wucs = [ScrapperUC.from_json_object(wuc, UCFParameter.WUNDERGROUND) for wuc in wucs]
            wucs = set(wucs)
            wucs = list(wucs)
            ucf.wunderground_ucs = wucs
        except KeyError:
            pass

        return ucf

    def get_ogimet_ucs(self):
        return [copy.deepcopy(uc) for uc in self.ogimet_ucs]

    def get_meteociel_ucs(self):
        return [copy.deepcopy(uc) for uc in self.meteociel_ucs]

    def get_wunderground_ucs(self):
        return [copy.deepcopy(uc) for uc in self.wunderground_ucs]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.meteociel_ucs} {self.ogimet_ucs} {self.wunderground_ucs}"
