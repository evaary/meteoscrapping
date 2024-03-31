import copy
from app.boite_a_bonheur.UCFParameterEnum import UCFParameter
from app.UCFChecker import UCFChecker
from app.ucs_module import ScrapperUC


class UserConfigFile:

    def __init__(self):
        self._ogimet_ucs = []
        self._meteociel_ucs = []
        self._wunderground_ucs = []

    @property
    def ogimet_ucs(self) -> "list[ScrapperUC]":
        return [copy.deepcopy(uc) for uc in self._ogimet_ucs]

    @property
    def meteociel_ucs(self) -> "list[ScrapperUC]":
        return [copy.deepcopy(uc) for uc in self._meteociel_ucs]

    @property
    def wunderground_ucs(self) -> "list[ScrapperUC]":
        return [copy.deepcopy(uc) for uc in self._wunderground_ucs]

    @classmethod
    def from_json(cls, path_to_ucf) -> "UserConfigFile":

        config_file = UCFChecker.check(path_to_ucf)
        ucf = UserConfigFile()

        try:
            oucs = config_file[UCFParameter.OGIMET.name]
            ucf._ogimet_ucs = list(set([ScrapperUC.from_json(ouc, UCFParameter.OGIMET) for ouc in oucs]))
        except KeyError:
            pass

        try:
            mucs = config_file[UCFParameter.METEOCIEL.name]
            ucf._meteociel_ucs = list(set([ScrapperUC.from_json(muc, UCFParameter.METEOCIEL)
                                          for muc in mucs]))
        except KeyError:
            pass

        try:
            wucs = config_file[UCFParameter.WUNDERGROUND.name]
            ucf._wunderground_ucs = list(set([ScrapperUC.from_json(wuc, UCFParameter.WUNDERGROUND)
                                             for wuc in wucs]))
        except KeyError:
            pass

        return ucf

    def get_all_ucs(self) -> "list[ScrapperUC]":
        all_ucs = []
        all_ucs.extend(self.ogimet_ucs)
        all_ucs.extend(self.meteociel_ucs)
        all_ucs.extend(self.wunderground_ucs)

        return all_ucs

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._meteociel_ucs} {self._ogimet_ucs} {self._wunderground_ucs}"
