import copy
from app.boite_a_bonheur.UCFParameterEnum import UCFParameter
from app.ucs.UCFChecker import UCFChecker
from app.ucs.ucs_module import (GeneralParametersUC,
                                ScrapperUC)


class UserConfigFile:

    def __init__(self):
        self.ogimet_ucs = []
        self.meteociel_ucs = []
        self.wunderground_ucs = []

    @classmethod
    def from_json(cls, path_to_ucf):

        config_file = UCFChecker.check(path_to_ucf)
        ucf = UserConfigFile()

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
            ucf.meteociel_ucs = list(set([ScrapperUC.from_json_object(muc, UCFParameter.METEOCIEL)
                                          for muc in mucs]))
        except KeyError:
            pass

        try:
            wucs = config_file[UCFParameter.WUNDERGROUND.name]
            ucf.wunderground_ucs = list(set([ScrapperUC.from_json_object(wuc, UCFParameter.WUNDERGROUND)
                                             for wuc in wucs]))
        except KeyError:
            pass

        return ucf

    def get_ogimet_ucs(self) -> "list[ScrapperUC]":
        return [copy.deepcopy(uc) for uc in self.ogimet_ucs]

    def get_meteociel_ucs(self) -> "list[ScrapperUC]":
        return [copy.deepcopy(uc) for uc in self.meteociel_ucs]

    def get_wunderground_ucs(self) -> "list[ScrapperUC]":
        return [copy.deepcopy(uc) for uc in self.wunderground_ucs]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.meteociel_ucs} {self.ogimet_ucs} {self.wunderground_ucs}"
