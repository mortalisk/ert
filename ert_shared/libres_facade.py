from pandas import DataFrame
from res.analysis.analysis_module import AnalysisModule
from res.analysis.enums.analysis_module_options_enum import \
    AnalysisModuleOptionsEnum
from res.enkf.export import (GenDataCollector, SummaryCollector,
                             SummaryObservationCollector, GenDataObservationCollector, GenKwCollector,
                             CustomKWCollector)
from res.enkf.plot_data import PlotBlockDataLoader


class LibresFacade(object):
    """Facade for libres inside ERT."""

    def __init__(self, enkf_main):
        self._enkf_main = enkf_main

    def get_analysis_module_names(self, iterable=False):
        modules = self.get_analysis_modules(iterable)
        return [module.getName() for module in modules]

    def get_analysis_modules(self, iterable=False):
        module_names = self._enkf_main.analysisConfig().getModuleList()

        modules = []
        for module_name in module_names:
            module = self._enkf_main.analysisConfig().getModule(module_name)
            module_is_iterable = module.checkOption(AnalysisModuleOptionsEnum.ANALYSIS_ITERABLE)

            if iterable == module_is_iterable:
                modules.append(module)

        return sorted(modules, key=AnalysisModule.getName)

    def get_ensemble_size(self):
        return self._enkf_main.getEnsembleSize()

    def get_current_case_name(self):
        return str(self._enkf_main.getEnkfFsManager().getCurrentFileSystem().getCaseName())

    def get_queue_config(self):
        return self._enkf_main.get_queue_config()

    def get_number_of_iterations(self):
        return self._enkf_main.analysisConfig().getAnalysisIterConfig().getNumIterations()

    def get_observations(self):
        return self._enkf_main.getObservations()

    def get_impl_type_name_for_obs_key(self, key):
        return self._enkf_main.getObservations()[key].getImplementationType().name

    def get_current_fs(self):
        return self._enkf_main.getEnkfFsManager().getCurrentFileSystem()

    def get_data_key_for_obs_key(self, observation_key):
        return self._enkf_main.getObservations()[observation_key].getDataKey()

    def get_matching_wildcards(self):
        return self._enkf_main.getObservations().getMatchingKeys

    def get_observation_key(self, index):
        return self._enkf_main.getObservations()[index].getKey()

    def load_gen_data(self, case_name, key, report_step):
        return GenDataCollector.loadGenData(
            self._enkf_main, case_name, key, report_step
        )

    def load_all_summary_data(self, case_name, keys=None):
        return SummaryCollector.loadAllSummaryData(
            self._enkf_main, case_name, keys
        )

    def load_observation_data(self, case_name, keys=None):
        return SummaryObservationCollector.loadObservationData(
            self._enkf_main, case_name, keys
        )

    def create_plot_block_data_loader(self, obs_vector):
        return PlotBlockDataLoader(obs_vector)

    def select_or_create_new_case(self, case_name):
        if self.get_current_case_name() != case_name:
            fs = self._enkf_main.getEnkfFsManager().getFileSystem(case_name)
            self._enkf_main.getEnkfFsManager().switchFileSystem(fs)


# from GuiApi

    def cases(self):
        return self._enkf_main.getEnkfFsManager().getCaseList()

    def is_case_hidden(self, case):
        return self._enkf_main.getEnkfFsManager().isCaseHidden(case)

    def case_has_data(self, case):
        return self._enkf_main.getEnkfFsManager().caseHasData(case)

    def is_case_running(self, case):
        return self._enkf_main.getEnkfFsManager().isCaseRunning(case)

    def allDataTypeKeys(self):
        return self._enkf_main.getKeyManager().allDataTypeKeys()

    def _isKeyWithObservations(self, key):
        return self._enkf_main.getKeyManager().isKeyWithObservations(key)

    def observation_keys(self, key):
        if self._enkf_main.getKeyManager().isGenDataKey(key):
            key = key.split("@")[0]
            return [GenDataObservationCollector.getObservationKeyForDataKey(self._enkf_main, key, 0)]
        elif self._enkf_main.getKeyManager().isSummaryKey(key):
            return SummaryObservationCollector.observationKeys(key)
        else:
            return []

    def _keyIndexType(self, key):
        if self._enkf_main.getKeyManager().isGenDataKey(key):
            return "INDEX"
        elif self._enkf_main.getKeyManager().isSummaryKey(key):
            return "VALUE"
        else:
            return None


    def _gatherGenKwData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = GenKwCollector.loadAllGenKwData(self._enkf_main, case, [key])
        return data[key].dropna()

    def _gatherSummaryData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = SummaryCollector.loadAllSummaryData(self._enkf_main, case, [key])
        if not data.empty:
            data = data.reset_index()

            if any(data.duplicated()):
                print("** Warning: The simulation data contains duplicate "
                      "timestamps. A possible explanation is that your "
                      "simulation timestep is less than a second.")
                data = data.drop_duplicates()


            data = data.pivot(index="Date", columns="Realization", values=key)

        return data #.dropna()

    def _gatherSummaryRefcaseData(self, key):
        refcase = self._enkf_main.eclConfig().getRefcase()

        if refcase is None or key not in refcase:
            return DataFrame()

        values = refcase.numpy_vector(key, report_only=False)
        dates = refcase.numpy_dates

        data = DataFrame(zip(dates, values), columns=['Date', key])
        data.set_index("Date", inplace=True)

        return data.iloc[1:]

    def _gatherSummaryObservationData(self, case, key):
        if self._enkf_main.getKeyManager().isKeyWithObservations(key):
            return SummaryObservationCollector.loadObservationData(self._enkf_main, case, [key]).dropna()
        else:
            return DataFrame()

    def _gatherGenDataData(self, case, key):
        """ :rtype: pandas.DataFrame """
        key = key.split("@")[0]
        report_step = 0
        try:
            data = GenDataCollector.loadGenData(self._enkf_main, case, key, report_step)
        except ValueError:
            data = DataFrame()

        return data.dropna() # removes all rows that has a NaN

    def _gatherGenDataObservationData(self, case, key_with_report_step):
        """ :rtype: pandas.DataFrame """
        key = key_with_report_step.split("@")[0]
        report_step = 0

        obs_key = GenDataObservationCollector.getObservationKeyForDataKey(self._enkf_main, key, report_step)

        if obs_key is not None:
            obs_data = GenDataObservationCollector.loadGenDataObservations(self._enkf_main, case, obs_key)
            columns = {obs_key: key_with_report_step, "STD_%s" % obs_key: "STD_%s" % key_with_report_step}
            obs_data = obs_data.rename(columns=columns)
        else:
            obs_data = DataFrame()

        return obs_data.dropna()

    def _gatherCustomKwData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = CustomKWCollector.loadAllCustomKWData(self._enkf_main, case, [key])[key]

        return data


    def _isKeyWithObservations(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().allDataTypeKeysWithObservations()

    def _isSummaryKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().summaryKeys()

    def _isGenKwKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().genKwKeys()

    def _isCustomKwKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().customKwKeys()

    def _isGenDataKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().genDataKeys()

    def _isMisfitKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().misfitKeys()

    def _dimentionalityOfKey(self, key):
        if self._isSummaryKey(key) or self._isGenDataKey(key):
            return 2
        else:
            return 1

