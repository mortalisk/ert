from res.enkf import EnKFMain, ResConfig

from ert_data.http_api import HttpApi
from ert_data.http_client import HttpClient
from ert_shared.libres_facade import LibresFacade
from ert_data.gui_api import GuiApi
import sys
import os
import threading
import time


config = "test-data/local/poly_example/poly.ert"#sys.argv[2]

dir = os.path.dirname(config)
file = os.path.basename(config)

os.chdir(dir)

res_config = ResConfig(file)
enkf_main = EnKFMain(res_config, strict=True)
facade = LibresFacade(enkf_main)
api = GuiApi(facade)

def run_server():
    http_api = HttpApi(api)
    http_api.run_http_server()


t = threading.Thread(target=run_server)
t.start()

#time.sleep(1)

http_client = HttpClient("localhost", 1337)

project = http_client.allDataTypeKeys()

keys = api.allDataTypeKeys()
cases = api.getAllCasesNotRunning()

key = project[0]["key"]
case = cases[0]["name"]

df = api.dataForKey(case, key)

print(df)

http_client.stop_server()


print("waiting for server to stop")
t.join()

print("Finished")



