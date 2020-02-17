from ert_data.observations import Observations
from ert_data.results import Results


class PlotApi:

    def __init__(self, facade):
        self._facade = facade

    def all_data_type_keys(self):
        return [{"key": key,
                 "index_type": self._key_index_type(key),
                 "observations": self._facade.observation_keys(key),
                 "has_refcase": self._facade.has_refcase(key),
                 "dimentionality": self._dimentionality_of_key(key),
                 "metadata": self._metadata(key)}
                for key in self._facade.all_data_type_keys()]

    def _metadata(self, key):
        meta = {}
        if self._facade.is_summary_key(key):
            meta["data_origin"] = "Summary"
        elif self._facade.is_gen_data_key(key):
            meta["data_origin"] = "Gen Data"
        elif self._facade.is_gen_kw_key(key):
            meta["data_origin"] = "Gen KW"
        elif self._facade.is_custom_kw_key(key):
            meta["data_origin"] = "Custom Data"
        return meta

    def get_all_cases_not_running(self):
        """ @rtype: list[str] """
        facade = self._facade
        return [{"name": case,
                 "hidden": facade.is_case_hidden(case),
                 "has_data": facade.case_has_data(case)}
                for case
                in facade.cases()
                if not facade.is_case_running(case)]

    def data_for_key(self, case, key):
        return Results(self._facade, [key], case).data

    def observations_for_obs_keys(self, case, obs_keys):
        return Observations(self._facade, obs_keys, case).data

    def refcase_data(self, key):
        return self._facade.refcase_data(key)

    def _dimentionality_of_key(self, key):
        if self._facade.is_summary_key(key) or self._facade.is_gen_data_key(key):
            return 2
        else:
            return 1

    def _key_index_type(self, key):
        if self._facade.is_gen_data_key(key):
            return "INDEX"
        elif self._facade.is_summary_key(key):
            return "VALUE"
        else:
            return None


