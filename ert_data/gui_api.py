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
        keys = [{"key": key,
                 "index_type": self._facade.keyIndexType(key),
                 "observations": self._facade.observation_keys(key),
                 "has_refcase": self._facade.has_refcase(key),
                 "dimentionality": self._facade.dimentionality_of_key(key),
                 "metadata": self._metadata(key)}
                for key in self._facade.all_data_type_keys()]
        return keys

    def _metadata(self, key):
        meta = {}
        if self._facade.isSummaryKey(key):
            meta["data_origin"] = "Summary"
        elif self._facade.isGenDataKey(key):
            meta["data_origin"] = "Gen Data"
        elif self._facade.isGenKwKey(key):
            meta["data_origin"] = "Gen KW"
        elif self._facade.isCustomKwKey(key):
            meta["data_origin"] = "Custom Data"
        return meta

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

    def refcase_data(self, key):
        return self._facade.refcase_data(key)


