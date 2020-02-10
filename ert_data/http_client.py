import http.client
import json
import pandas as pd
import time

class HttpClient:

    def __init__(self, url, port):
        self.url = url
        self.port = port
        connection = http.client.HTTPConnection(self.url, self.port)

        # for i in range(1, 10):
        time.sleep(1)
        # try:
        print("start client, attempt connect")
        connection.request("GET", "/")
        reply = connection.getresponse().read().decode()
        print("started, reply: {}".format(reply))
        #     break
        # except:
        #     continue

    def _get_project(self):
        connection = http.client.HTTPConnection(self.url, self.port)
        connection.request("GET", "/")
        reply = connection.getresponse().read().decode()
        print(reply)
        project = json.loads(reply)
        return project

    def _get_data(self, case = "", key=None, obs_keys=[], refcase=False):
        connection = http.client.HTTPConnection(self.url, self.port)
        if not refcase:
            path = "/data?case={}".format(case)
        else:
            path = "/data?key={}&refcase=true".format(key)

        if key is not None:
            path += "&key={}".format(key)

        path += "".join(["&obs_key={}".format(k) for k in obs_keys])

        connection.request("GET", path)
        reply = connection.getresponse()
        rows = reply.headers["X-header-rows"]
        rowsi = int(rows)
        # def data_parser()
        dataframe = pd.read_csv(reply, infer_datetime_format=True, parse_dates=True,
                                index_col=[0], header=list(range(rowsi)))
        dataframe.index = list(range(len(dataframe)))

        dataframe.columns

        try:
            return dataframe.astype(float)
        except ValueError:
            return dataframe.astype(object)

    def allDataTypeKeys(self):
        project = self._get_project()
        return project["keys"]

    def getAllCasesNotRunning(self):
        project = self._get_project()
        return project["cases"]

    def dataForKey(self, case, key):
        return self._get_data(case=case, key=key)

    def observationsForObsKeys(self, case, obs_keys):
        return self._get_data(case=case, obs_keys=obs_keys)

    def refcase_data(self, key):
        return self._get_data(key=key, refcase=True)

    def stop_server(self):
        connection = http.client.HTTPConnection(self.url, self.port)
        connection.request("GET", "/stop")

