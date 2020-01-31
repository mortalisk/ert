from res.enkf import RealizationStateEnum

from ert_data.measured import MeasuredData
from ert_data.observations import Observations
from ert_data.results import Results
from ert_shared import ERT
from pandas import DataFrame
from res.enkf.export import GenKwCollector, SummaryCollector, GenDataCollector, SummaryObservationCollector, \
    GenDataObservationCollector, CustomKWCollector


class GuiApi:

    def __init__(self, facade):
        self._facade = facade
        """:type: res.enkf.enkf_main.EnKFMain"""

    def allDataTypeKeys(self):
        return [{"key": key,
                 "index_type": self._facade._keyIndexType(key),
                 "observations": self._facade.observation_keys(key),
                 "dimentionality": self._facade._dimentionalityOfKey(key)}
                for key in self._facade.allDataTypeKeys()]

    def getAllCasesNotRunning(self):
        """ @rtype: list[str] """
        facade = self._facade
        return [{"name": case,
                 "hidden": facade.is_case_hidden(case),
                 "has_data": facade.case_has_data(case)}
                for case
                in facade.cases()
                if not facade.is_case_running(case)]

    def dataForKey(self, case, key):
        return Results(self._facade, [key], case).data

    def observationsForObsKeys(self, case, obs_keys):
        return Observations(self._facade, obs_keys, case).data
