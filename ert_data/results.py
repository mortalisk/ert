import pandas as pd

from ert_data import loader
from ert_data.measured import MeasuredData, _add_index_range


class Results:

    def __init__(self, facade, keys, case):
        self._facade = facade
        self._case = case
        self._set_data(self._get_data(keys))

    @property
    def data(self):
        return self._data

    def _set_data(self, data):
        self._data = data

    def _get_data(self, data_keys):
        measured_data = pd.DataFrame()

        for key in data_keys:

            data = self._data_for_key(key)

            # Simulated data and observations both refer to the data
            # index at some levels, so having that information available is
            # helpful
            #_add_index_range(data)

            data = pd.concat({key: data}, axis=1)

            measured_data = pd.concat([measured_data, data], axis=1)

        try:
            return measured_data.astype(float)
        except ValueError:
            return measured_data

    def _data_for_key(self, key):
        if self._facade.is_summary_key(key):
            return self._facade.gather_summary_data(self._case, key).T
        elif self._facade.is_gen_kw_key(key):
            return self._facade.gather_gen_kw_data(self._case, key)
        elif self._facade.is_custom_kw_key(key):
            return self._facade.gather_custom_kw_data(self._case, key)
        elif self._facade.is_gen_data_key(key):
            return self._facade.gather_gen_data_data(self._case, key).T
