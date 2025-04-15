import copy
from typing import List

from app.boite_a_bonheur.UCFParameterEnum import UCFParameters
from app.UCFChecker import UCFChecker
from app.ucs_module import ScrapperUC, GeneralParametersUC


class UserConfigFile:

    def __init__(self):
        self._ogimet_ucs = []
        self._meteociel_ucs = []
        self._wunderground_ucs = []

    @property
    def ogimet_ucs(self) -> List[ScrapperUC]:
        return [copy.deepcopy(uc) for uc in self._ogimet_ucs]

    @property
    def meteociel_ucs(self) -> List[ScrapperUC]:
        return [copy.deepcopy(uc) for uc in self._meteociel_ucs]

    @property
    def wunderground_ucs(self) -> List[ScrapperUC]:
        return [copy.deepcopy(uc) for uc in self._wunderground_ucs]

    @classmethod
    def from_json(cls, path_to_ucf) -> "UserConfigFile":

        config_file = UCFChecker.check(path_to_ucf)
        ucf = UserConfigFile()

        try:
            general_parameters = config_file[UCFParameters.GENERAL_PARAMETERS.json_name]
            GeneralParametersUC.from_json_object(general_parameters)
        except KeyError:
            GeneralParametersUC.instance()

        try:
            oucs = config_file[UCFParameters.OGIMET.json_name]
            ucf._ogimet_ucs = list(set([ScrapperUC.from_json(ouc, UCFParameters.OGIMET) for ouc in oucs]))
        except KeyError:
            pass

        try:
            mucs = config_file[UCFParameters.METEOCIEL.json_name]
            ucf._meteociel_ucs = list(set([ScrapperUC.from_json(muc, UCFParameters.METEOCIEL) for muc in mucs]))
        except KeyError:
            pass

        try:
            wucs = config_file[UCFParameters.WUNDERGROUND.json_name]
            ucf._wunderground_ucs = list(set([ScrapperUC.from_json(wuc, UCFParameters.WUNDERGROUND) for wuc in wucs]))
        except KeyError:
            pass

        return ucf

    def get_all_ucs(self) -> List[ScrapperUC]:
        all_ucs = []
        all_ucs.extend(self.ogimet_ucs)
        all_ucs.extend(self.meteociel_ucs)
        all_ucs.extend(self.wunderground_ucs)

        return all_ucs

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._meteociel_ucs} {self._ogimet_ucs} {self._wunderground_ucs}"
