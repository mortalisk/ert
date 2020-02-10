from flask import Flask, request, abort
import pandas as pd

class HttpApi:
    def __init__(self, gui_api):
        self._api = gui_api

    def get_project(self):
        keys = self._api.allDataTypeKeys()
        cases = self._api.getAllCasesNotRunning()
        res = {
            "keys": keys,
            "cases": cases
        }
        return res

    def get_data(self):
        key = request.args.get("key")
        case = request.args.get("case")
        obs_keys = request.args.getlist("obs_key")
        refcase = request.args.get("refcase")

        if refcase == "true" and key is not None:
            data = self._api.refcase_data(key)
            return data.to_csv()

        if case is None or case == "":
            abort(400, "must have case")

        if key is not None:
            if len(obs_keys) > 0:
                abort(400, "can not accept both key and obs_key at the same time")
            data = self._api.dataForKey(case, key)
            data = pd.concat({case:data})
            return data.to_csv()

        obs_data = self._api.observationsForObsKeys(case, obs_keys)
        #obs_data.
        csv = obs_data.to_csv()
        return csv

    def stop(self):
        shutdown_hook = request.environ.get('werkzeug.server.shutdown')
        if shutdown_hook is not None:
            shutdown_hook()
        return "shutdown"


    def run_http_server(self):
        app = Flask("Ert http api")
        app.add_url_rule('/', 'project', self.get_project)
        app.add_url_rule('/data', 'data', self.get_data)
        app.add_url_rule('/stop', "stop", self.stop)

        app.run(host='0.0.0.0', port=1337)

        print("exit server")
