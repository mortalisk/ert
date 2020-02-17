import math

import numpy
from pandas import DataFrame
from res.analysis.analysis_module import AnalysisModule
from res.analysis.enums.analysis_module_options_enum import \
    AnalysisModuleOptionsEnum
from res.enkf import RealizationStateEnum
from res.enkf.export import (GenDataCollector, SummaryCollector,
                             SummaryObservationCollector, GenDataObservationCollector, GenKwCollector,
                             CustomKWCollector)
from res.enkf.plot_data import PlotBlockDataLoader, EnsemblePlotGenKW, EnsemblePlotGenData

from ert_shared.data_result import DataResult


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

    def all_data_type_keys(self):
        return self._enkf_main.getKeyManager().allDataTypeKeys()

    def observation_keys(self, key):
        if self._enkf_main.getKeyManager().isGenDataKey(key):
            key_parts = key.split("@")
            key = key_parts[0]
            if len(key_parts) > 1:
                report_step = int(key_parts[1])
            else:
                report_step = 0

            obs_key = GenDataObservationCollector.getObservationKeyForDataKey(self._enkf_main, key, report_step)
            if obs_key is not None:
                return [obs_key]
            else:
                return []
        elif self._enkf_main.getKeyManager().isSummaryKey(key):
            return list(SummaryObservationCollector.observationKeys(self._enkf_main, key))
        else:
            return []

    def keyIndexType(self, key):
        if self._enkf_main.getKeyManager().isGenDataKey(key):
            return "INDEX"
        elif self._enkf_main.getKeyManager().isSummaryKey(key):
            return "VALUE"
        else:
            return None

    def activeRealizations(self):
        return SummaryCollector.createActiveList(self)

    def data_for_key(self, case=None, key=None, realization=None):


        if case is not None:
            cases = [case]
        else:
            cases = [case
                     for case
                     in self.cases()
                     if (not self.is_case_hidden(case)
                         and not self.is_case_running(case)
                         and self.case_has_data(case))]
        if key is not None:
            keys = [key]
        else:
            keys = self.all_data_type_keys()

        if realization is not None:
            realizations = [realization]
        else:
            realizations = self.activeRealizations()

        for case in cases:
            fs = self._enkf_main.getEnkfFsManager().getFileSystem(case)
            for realization in realizations:
                for key in keys:
                    if self.isSummaryKey(key):
                        data, index = self.gatherSummaryData(self._case, key)
                    elif self.isGenKwKey(key):
                        data, index = self.genKwData(case, key, realization)
                    elif self.isCustomKwKey(key):
                        data, index = self.gatherCustomKwData(self._case, key).T
                    elif self.isGenDataKey(key):
                        data, index = self.loadGenData(fs, key, realization)

                    res = DataResult(case, key, realization, data, index)
                    yield res


    def loadGenData(ert, case_fs, key, realization_number):

        key_parts = key.split("@")
        key = key_parts[0]
        if len(key_parts) > 1:
            report_step = int(key_parts[1])
        else:
            report_step = 0


        fs = case_fs
        realizations = fs.realizationList( RealizationStateEnum.STATE_HAS_DATA )
        config_node = ert.ensembleConfig().getNode(key)
        gen_data_config = config_node.getModelConfig()

        ensemble_data = EnsemblePlotGenData( config_node , fs , report_step )
        # The data size and active can only be inferred *after* the EnsembleLoad.
        data_size = gen_data_config.getDataSize( report_step )
        active_mask = gen_data_config.getActiveMask()

        realization_vector = ensemble_data[realization_number]

        index_array = []
        value_array = []

        if len(realization_vector) > 0: # Must check because of a bug changing between different case with different states
            for data_index in range(data_size):
                value = None
                if active_mask[data_index]:
                    value = realization_vector[data_index]
                value_array.append(value)
                index_array.append(data_index)

        data_numpy = numpy.array(value_array)
        index_numpy = numpy.array(index_array)
        return data_numpy, index_numpy

    def genKwData(self, fs, key, realization_number):

        realizations = GenKwCollector.createActiveList(self._enkf_main, fs)


        key, keyword = key.split(":")

        use_log_scale = False
        if key.startswith("LOG10_"):
            key = key[6:]
            use_log_scale = True

        ensemble_config_node = self._enkf_main.ensembleConfig().getNode(key)
        ensemble_data = EnsemblePlotGenKW(ensemble_config_node, fs)
        keyword_index = ensemble_data.getIndexForKeyword(keyword)


        realization_vector = ensemble_data[realization_number]

        value = realization_vector[keyword_index]

        if use_log_scale:
            value = math.log10(value)

        data_array = numpy.array([value])
        index_array = numpy.array([0])
        return data_array, index_array


    def _old_data_for_key(self, case, key=None, realization=None):
        if self.isSummaryKey(key):
            return self.gatherSummaryData(self._case, key)
        elif self.isGenKwKey(key):
            return self.genKwData(case, key, realization)
        elif self.isCustomKwKey(key):
            return self.gatherCustomKwData(self._case, key).T
        elif self.isGenDataKey(key):
            return self.gatherGenDataData(self._case, key)

    def gatherGenKwData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = GenKwCollector.loadAllGenKwData(self._enkf_main, case, [key])
        return data[key].dropna()

    def gatherSummaryData(self, case, key):
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

    def has_refcase(self, key):
        refcase = self._enkf_main.eclConfig().getRefcase()
        return refcase is not None and key in refcase

    def refcase_data(self, key):
        refcase = self._enkf_main.eclConfig().getRefcase()

        if refcase is None or key not in refcase:
            return DataFrame()

        values = refcase.numpy_vector(key, report_only=False)
        dates = refcase.numpy_dates

        data = DataFrame(zip(dates, values), columns=['Date', key])
        data.set_index("Date", inplace=True)

        return data.iloc[1:]

    def gatherGenDataData(self, case, key):
        """ :rtype: pandas.DataFrame """
        key_parts = key.split("@")
        key = key_parts[0]
        if len(key_parts) > 1:
            report_step = int(key_parts[1])
        else:
            report_step = 0

        try:
            data = GenDataCollector.loadGenData(self._enkf_main, case, key, report_step)
        except ValueError:
            data = DataFrame()

        return data.dropna() # removes all rows that has a NaN

    def gatherCustomKwData(self, case, key):
        """ :rtype: pandas.DataFrame """
        data = CustomKWCollector.loadAllCustomKWData(self._enkf_main, case, [key])[key]

        return data

    def isSummaryKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().summaryKeys()

    def isGenKwKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().genKwKeys()

    def isCustomKwKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().customKwKeys()

    def isGenDataKey(self, key):
        """ :rtype: bool """
        return key in self._enkf_main.getKeyManager().genDataKeys()

    def dimentionality_of_key(self, key):
        if self.isSummaryKey(key) or self.isGenDataKey(key):
            return 2
        else:
            return 1

