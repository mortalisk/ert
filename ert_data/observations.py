import pandas as pd

from ert_data import obs_loader as loader


class Observations:
    def __init__(self, facade, keys, case):
        self._facade = facade
        self._case = case
        self._set_data(self._get_data(keys))

    @property
    def data(self):
        return self._data

    def _set_data(self, data):
        expected_keys = ["OBS", "STD"]
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "Invalid type: {}, should be type: {}".format(type(data), pd.DataFrame)
            )
        elif not data.empty and not set(expected_keys).issubset(data.index):
            raise ValueError(
                "{} should be present in DataFrame index, missing: {}".format(
                    ["OBS", "STD"], set(expected_keys) - set(data.index)
                )
            )
        else:
            self._data = data

    def _get_data(self, observation_keys):
        """
        Adds simulated and observed data and returns a dataframe where ensamble
        members will have a data key, observed data will be named OBS and
        observed standard deviation will be named STD.
        """
        measured_data = pd.DataFrame()
        case_name = self._case

        for key in observation_keys:
            observation_type = self._facade.get_impl_type_name_for_obs_key(key)
            data_loader = loader.data_loader_factory(observation_type)

            data = data_loader(self._facade, key, case_name)

            # Simulated data and observations both refer to the data
            # index at some levels, so having that information available is
            # helpful
            _add_index_range(data)

            data = pd.concat({key: data}, axis=1, names=["obs_key"])

            measured_data = pd.concat([measured_data, data], axis=1)

        return measured_data.astype(float)


def _add_index_range(data):
    """
    Adds a second column index with which corresponds to the data
    index. This is because in libres simulated data and observations
    are connected through an observation key and data index, so having
    that information available when the data is joined is helpful.
    """
    arrays = [data.columns.to_list(), list(range(len(data.columns)))]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=['key_index', 'data_index'])
    data.columns = index
