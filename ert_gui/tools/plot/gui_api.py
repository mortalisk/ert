from ert_shared import ERT
from pandas import DataFrame
from res.enkf.export import GenKwCollector, SummaryCollector, GenDataCollector, SummaryObservationCollector, \
    GenDataObservationCollector, CustomKWCollector


class GuiApi:

    def __init__(self):
        self._ert = ERT.ert
        """:type: res.enkf.enkf_main.EnKFMain"""

        self._key_manager = self._ert.getKeyManager()

    def dataForKey(self, case, key):
        pass

    def allDataTypeKeys(self):
        self._key_manager.allDataTypeKeys()

    def gatherGenKwData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = GenKwCollector.loadAllGenKwData(self._ert, case, [key])
        return data[key].dropna()

    def gatherSummaryData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = SummaryCollector.loadAllSummaryData(self._ert, case, [key])
        if not data.empty:
            data = data.reset_index()

            if any(data.duplicated()):
                print("** Warning: The simulation data contains duplicate "
                      "timestamps. A possible explanation is that your "
                      "simulation timestep is less than a second.")
                data = data.drop_duplicates()


            data = data.pivot(index="Date", columns="Realization", values=key)

        return data #.dropna()

    def gatherSummaryRefcaseData(self, key):
        refcase = self._ert.eclConfig().getRefcase()

        if refcase is None or key not in refcase:
            return DataFrame()

        values = refcase.numpy_vector(key, report_only=False)
        dates = refcase.numpy_dates

        data = DataFrame(zip(dates, values), columns=['Date', key])
        data.set_index("Date", inplace=True)

        return data.iloc[1:]

    def gatherSummaryHistoryData(self, case, key):
        # create history key
        if ":" in key:
            head, tail = key.split(":", 2)
            key = "%sH:%s" % (head, tail)
        else:
            key = "%sH" % key

        data = GuiApi.gatherSummaryRefcaseData(key)
        if data.empty and case is not None:
            data = GuiApi.gatherSummaryData(case, key)

        return data

    def gatherSummaryObservationData(self, case, key):
        if self._ert.getKeyManager().isKeyWithObservations(key):
            return SummaryObservationCollector.loadObservationData(self._ert, case, [key]).dropna()
        else:
            return DataFrame()

    def gatherGenDataData(self, case, key):
        """ :rtype: pandas.DataFrame """
        key, report_step = key.split("@", 1)
        report_step = int(report_step)
        try:
            data = GenDataCollector.loadGenData(self._ert, case, key, report_step)
        except ValueError:
            data = DataFrame()

        return data.dropna() # removes all rows that has a NaN

    def gatherGenDataObservationData(self, case, key_with_report_step):
        """ :rtype: pandas.DataFrame """
        key, report_step = key_with_report_step.split("@", 1)
        report_step = int(report_step)

        obs_key = GenDataObservationCollector.getObservationKeyForDataKey(self._ert, key, report_step)

        if obs_key is not None:
            obs_data = GenDataObservationCollector.loadGenDataObservations(self._ert, case, obs_key)
            columns = {obs_key: key_with_report_step, "STD_%s" % obs_key: "STD_%s" % key_with_report_step}
            obs_data = obs_data.rename(columns=columns)
        else:
            obs_data = DataFrame()

        return obs_data.dropna()

    def gatherCustomKwData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = CustomKWCollector.loadAllCustomKWData(self._ert, case, [key])[key]

        return data


    def isKeyWithObservations(self, key):
        """ :rtype: bool """
        return key in self._key_manager.allDataTypeKeysWithObservations()

    def isSummaryKey(self, key):
        """ :rtype: bool """
        return key in self._key_manager.summaryKeys()

    def isGenKwKey(self, key):
        """ :rtype: bool """
        return key in self._key_manager.genKwKeys()

    def isCustomKwKey(self, key):
        """ :rtype: bool """
        return key in self._key_manager.customKwKeys()

    def isGenDataKey(self, key):
        """ :rtype: bool """
        return key in self._key_manager.genDataKeys()

    def isMisfitKey(self, key):
        """ :rtype: bool """
        return key in self._key_manager.misfitKeys()
