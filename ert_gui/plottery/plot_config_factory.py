from ert_gui.plottery import PlotConfig


class PlotConfigFactory(object):

    @classmethod
    def createPlotConfigForKey(cls, api, key):
        """
        @type ert: res.enkf.enkf_main.EnKFMain
        @param key: str
        @return: PlotConfig
        """
        plot_config = PlotConfig(plot_settings=None , title = key)

        # The styling of statistics changes based on the nature of the data
        if api.isSummaryKey(key) or api.isGenDataKey(key):
            mean_style = plot_config.getStatisticsStyle("mean")
            mean_style.line_style = "-"
            plot_config.setStatisticsStyle("mean", mean_style)

            p10p90_style = plot_config.getStatisticsStyle("p10-p90")
            p10p90_style.line_style = "--"
            plot_config.setStatisticsStyle("p10-p90", p10p90_style)
        else:
            mean_style = plot_config.getStatisticsStyle("mean")
            mean_style.line_style = "-"
            mean_style.marker = "o"
            plot_config.setStatisticsStyle("mean", mean_style)

            std_style = plot_config.getStatisticsStyle("std")
            std_style.line_style = "--"
            std_style.marker = "D"
            plot_config.setStatisticsStyle("std", std_style)

        return plot_config
