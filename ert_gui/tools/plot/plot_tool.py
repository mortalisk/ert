from ert_data.gui_api import GuiApi
from ert_data.http_api import HttpApi
from ert_data.http_client import HttpClient
from ert_gui.ertwidgets import resourceIcon
from ert_gui.tools import Tool
from ert_gui.tools.plot import PlotWindow
from ert_shared import ERT
import threading


class PlotTool(Tool):
    def __init__(self, config_file):
        super(PlotTool, self).__init__("Create Plot", "tools/plot", resourceIcon("ide/chart_curve_add"))
        self._config_file = config_file

    def trigger(self):

        def run_server():
            api = GuiApi(ERT.enkf_facade)
            server = HttpApi(api)
            server.run_http_server()


        t = threading.Thread(target=run_server)
        t.start()

        client = HttpClient("localhost", 1337)
        plot_window = PlotWindow(self._config_file, client, self.parent())
        plot_window.show()


        #t.join()






