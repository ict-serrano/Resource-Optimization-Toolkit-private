import json
import logging
import requests

# import openmic.agent.heartbeat as heartbeat
# import openmic.agent.internal_manager as internalManager
# import openmic.agent.communication_interface as communicationInterface

logger = logging.getLogger("SERRANO.ROT.API.ClientInstance")


class ClientInstance:

    def __init__(self, client_context):
        self.__client_context = client_context
        self.__http_auth = client_context.get_http_basic_auth()
        self.__rest_url = client_context.get_rest_url()
        # self.communication_interface = communicationInterface.CommunicationInterface(agent_context)
        #self.internal_manager = internalManager.InternalManager(client_context)

    def get_engines(self):
        data = {}
        res = requests.get("%s/api/v1/rot/engines" % self.__rest_url, auth=self.__http_auth)
        if res.status_code == 200:
            data = json.loads(res.text)["engines"]
        return data

    def get_engine(self, engine_uuid):
        data = {}
        res = requests.get("%s/api/v1/rot/engine/%s" % (self.__rest_url, engine_uuid), auth=self.__http_auth)
        if res.status_code == 200:
            data = json.loads(res.text)
        return data

    def get_logs(self, execution_uuid):
        data = {}
        res = requests.get("%s/api/v1/rot/logs/%s" % (self.__rest_url, execution_uuid), auth=self.__http_auth)
        if res.status_code == 200:
            data = json.loads(res.text)["log_details"]
        return data

    def get_statistics(self, **kwargs):
        start = kwargs.get('start', None)
        end = kwargs.get('end', None)
        return {}

    def delete_execution(self, execution_uuid):
        res = requests.delete("%s/api/v1/rot/execution/%s" % (self.__rest_url, execution_uuid), auth=self.__http_auth)
        print(res.text)

    def post_execution(self, execution_plugin, parameters):
        data = None
        if type(parameters) is not dict:
            parameters = json.loads(parameters)
        res = requests.post("%s/api/v1/rot/execution" % self.__rest_url,
                            auth=self.__http_auth,
                            json={"execution_plugin": execution_plugin, "parameters": parameters})
        if res.status_code == 200 or res.status_code == 201:
            data = json.loads(res.text)
        return data

    def get_execution(self, execution_uuid):
        data = {}
        res = requests.get("%s/api/v1/rot/execution/%s" % (self.__rest_url, execution_uuid), auth=self.__http_auth)
        if res.status_code == 200:
            data = json.loads(res.text)
        return data

    def get_executions(self):
        data = {}
        res = requests.get("%s/api/v1/rot/executions" % self.__rest_url, auth=self.__http_auth)
        if res.status_code == 200:
            data = json.loads(res.text)["executions"]
        return data
