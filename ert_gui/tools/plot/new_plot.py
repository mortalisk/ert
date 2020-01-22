from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMainWindow, QDockWidget, QTabWidget, QWidget, QVBoxLayout

from ert_gui.plottery.plots.ensemble import EnsemblePlot
from ert_gui.plottery.plots.statistics import StatisticsPlot
from ert_shared import ERT
from ert_gui.ertwidgets import showWaitCursorWhileWaiting
from ert_gui.ertwidgets.models.ertmodel import getCurrentCaseName
from ert_gui.plottery import PlotContext, PlotDataGatherer as PDG, PlotConfig, plots, PlotConfigFactory

from ert_gui.tools.plot import DataTypeKeysWidget, CaseSelectionWidget, PlotWidget, DataTypeKeysListModel
from ert_gui.tools.plot.customize import PlotCustomizer

from .gui_api import GuiApi

CROSS_CASE_STATISTICS = "Cross Case Statistics"
DISTRIBUTION = "Distribution"
GAUSSIAN_KDE = "Gaussian KDE"
ENSEMBLE = "Ensemble"
HISTOGRAM = "Histogram"
STATISTICS = "Statistics"

class NewPlotWindow(QMainWindow):


    def __init__(self, config_file, parent):
        QMainWindow.__init__(self, parent)

        self._api = GuiApi()

        self.setMinimumWidth(850)
        self.setMinimumHeight(650)

        self.setWindowTitle("Plotting - {}".format(config_file))
        self.activateWindow()

        self._plot_customizer = PlotCustomizer(self)

        def plotConfigCreator(key):
            return PlotConfigFactory.createPlotConfigForKey(self._api, key)

        self._plot_customizer.setPlotConfigCreator(plotConfigCreator)
        self._plot_customizer.settingsChanged.connect(self.keySelected)

        self._central_tab = QTabWidget()
        self._central_tab.currentChanged.connect(self.currentPlotChanged)

        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(central_layout)

        central_layout.addWidget(self._central_tab)

        self.setCentralWidget(central_widget)

        self._plot_widgets = []
        """:type: list of PlotWidget"""

        self.addPlotWidget(ENSEMBLE, EnsemblePlot(self._api))
        self.addPlotWidget(STATISTICS, StatisticsPlot(self._api))
        # self.addPlotWidget(HISTOGRAM, plots.plotHistogram, 1)
        # self.addPlotWidget(GAUSSIAN_KDE, plots.plotGaussianKDE, 1)
        # self.addPlotWidget(DISTRIBUTION, plots.plotDistribution, 1)
        # self.addPlotWidget(CROSS_CASE_STATISTICS, plots.plotCrossCaseStatistics, 1)

        data_types_key_model = DataTypeKeysListModel(self._api.allDataTypeKeys())

        self._data_type_keys_widget = DataTypeKeysWidget(data_types_key_model)
        self._data_type_keys_widget.dataTypeKeySelected.connect(self.keySelected)
        self.addDock("Data types", self._data_type_keys_widget)
        cases = self._api.getAllCasesNotRunning()
        case_names = [case["name"] for case in cases if not case["hidden"] and case["has_data"]]
        self._case_selection_widget = CaseSelectionWidget(case_names)
        self._case_selection_widget.caseSelectionChanged.connect(self.keySelected)
        self.addDock("Plot case", self._case_selection_widget)

        current_plot_widget = self._plot_widgets[self._central_tab.currentIndex()]
        current_plot_widget.setActive()
        self._data_type_keys_widget.selectDefault()
        self._updateCustomizer(current_plot_widget)


    def currentPlotChanged(self):
        for plot_widget in self._plot_widgets:
            plot_widget.setActive(False)
            index = self._central_tab.indexOf(plot_widget)

            if index == self._central_tab.currentIndex() and plot_widget.canPlotKey(self.getSelectedKey()):
                plot_widget.setActive()
                self._updateCustomizer(plot_widget)
                plot_widget.updatePlot()

    def _updateCustomizer(self, plot_widget):
        """ @type plot_widget: PlotWidget """
        key = self.getSelectedKey()
        index_type = self._api.keyIndexType(key)


        x_axis_type = PlotContext.UNKNOWN_AXIS
        y_axis_type = PlotContext.UNKNOWN_AXIS

        if plot_widget.name == ENSEMBLE:
            x_axis_type = index_type
            y_axis_type = PlotContext.VALUE_AXIS
        elif plot_widget.name == STATISTICS:
            x_axis_type = index_type
            y_axis_type = PlotContext.VALUE_AXIS
        elif plot_widget.name == DISTRIBUTION:
            y_axis_type = PlotContext.VALUE_AXIS
        elif plot_widget.name == CROSS_CASE_STATISTICS:
            y_axis_type = PlotContext.VALUE_AXIS
        elif plot_widget.name == HISTOGRAM:
            x_axis_type = PlotContext.VALUE_AXIS
            y_axis_type = PlotContext.COUNT_AXIS
        elif plot_widget.name == GAUSSIAN_KDE:
            x_axis_type = PlotContext.VALUE_AXIS
            y_axis_type = PlotContext.DENSITY_AXIS

        self._plot_customizer.setAxisTypes(x_axis_type, y_axis_type)


    def createPlotContext(self, figure):
        key = self.getSelectedKey()
        cases = self._case_selection_widget.getPlotCaseNames()
        plot_config = PlotConfig.createCopy(self._plot_customizer.getPlotConfig())
        plot_config.setTitle(key)
        return PlotContext(figure, plot_config, cases, key)


    def getSelectedKey(self):
        return str(self._data_type_keys_widget.getSelectedItem())

    def addPlotWidget(self, name, plotter, enabled=True):
        plot_widget = PlotWidget(name, plotter, self.createPlotContext)
        plot_widget.customizationTriggered.connect(self.toggleCustomizeDialog)

        index = self._central_tab.addTab(plot_widget, name)
        self._plot_widgets.append(plot_widget)
        self._central_tab.setTabEnabled(index, enabled)


    def addDock(self, name, widget, area=Qt.LeftDockWidgetArea, allowed_areas=Qt.AllDockWidgetAreas):
        dock_widget = QDockWidget(name)
        dock_widget.setObjectName("%sDock" % name)
        dock_widget.setWidget(widget)
        dock_widget.setAllowedAreas(allowed_areas)
        dock_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        self.addDockWidget(area, dock_widget)
        return dock_widget


    @showWaitCursorWhileWaiting
    def keySelected(self):
        key = self.getSelectedKey()
        self._plot_customizer.switchPlotConfigHistory(key)

        for plot_widget in self._plot_widgets:
            plot_widget.setDirty()
            index = self._central_tab.indexOf(plot_widget)
            self._central_tab.setTabEnabled(index, plot_widget.canPlotKey(key))

        for plot_widget in self._plot_widgets:
            if plot_widget.canPlotKey(key):
                plot_widget.updatePlot()

        self.currentPlotChanged()


    def toggleCustomizeDialog(self):
        self._plot_customizer.toggleCustomizationDialog()
