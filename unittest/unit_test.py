import sys
import json
import os.path
import signal

import requests
from requests.auth import HTTPBasicAuth

import unittest

CONF_FILE = "/home/serrano/unittest/unittest_conf.json"
print("PRINT SOMETHING")

class TestInstance(unittest.TestCase):
    
    def setUp(self):
        self.conf = config_params
        self.ip = self.conf["address"]
        self.port = self.conf["port"]
        self.username = self.conf["username"]
        self.password = self.conf["password"]
        self.cert = "/home/serrano/certs/cert.pem"
    
    def test_01_start_execution(self):
        self.params = {"execution_plugin": "test",
                       "parameters": {"times":2, "length": 8}}
        try:
            r = requests.post("https://%s:%s/api/v1/rot/execution" %(self.ip,
                                                                     self.port),
                                                                     auth=HTTPBasicAuth(self.username, self.password),
                                                                     json=self.params,
                                                                     verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_02_get_execution_history(self):
        try:
            r = requests.get("https://%s:%s/api/v1/rot/history" %(self.ip,
                                                                  self.port),
                                                                  auth=HTTPBasicAuth(self.username, self.password),
                                                                  verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_03_get_executions(self):
        global execution_id, engine_id
        try:
            r = requests.get("https://%s:%s/api/v1/rot/executions" %(self.ip,
                                                                     self.port),
                                                                     auth=HTTPBasicAuth(self.username, self.password),
                                                                     verify=self.cert)
            data = r.json()["executions"]
            test_execution = len(data)-1
            execution_id =  data[test_execution]["execution_id"]
            engine_id = data[test_execution]["engine_id"]
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_04_get_execution(self):
        try:
            r = requests.get("https://%s:%s/api/v1/rot/execution/%s" %(self.ip,
                                                                       self.port,
                                                                       execution_id),
                                                                       auth=HTTPBasicAuth(self.username, self.password),
                                                                       verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_05_delete_execution(self):
        try:
            r = requests.delete("https://%s:%s/api/v1/rot/execution/%s" %(self.ip,
                                                                          self.port,
                                                                          execution_id),
                                                                          auth=HTTPBasicAuth(self.username, self.password),
                                                                          verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_06_execution_statistics(self):
        try:
            r = requests.get("https://%s:%s/api/v1/rot/statistics" %(self.ip,
                                                                     self.port),
                                                                     auth=HTTPBasicAuth(self.username, self.password),
                                                                     verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_07_active_engines(self):
        try:
            r = requests.get("https://%s:%s/api/v1/rot/engines" %(self.ip,
                                                                  self.port),
                                                                  auth=HTTPBasicAuth(self.username, self.password),
                                                                  verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_08_engine_details(self):
        try:
            r = requests.get("https://%s:%s/api/v1/rot/engine/%s" %(self.ip,
                                                                  self.port,
                                                                  engine_id),
                                                                  auth=HTTPBasicAuth(self.username, self.password),
                                                                  verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_09_execution_logs(self):
        try:
            r = requests.get("https://%s:%s/api/v1/rot/logs/%s" %(self.ip,
                                                                  self.port,
                                                                  execution_id),
                                                                  auth=HTTPBasicAuth(self.username, self.password),
                                                                  verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_10_create_user(self):
        self.params = {"username": "test",
                       "password": "test"}
        try:
            r = requests.post("https://%s:%s/api/v1/rot/user" %(self.ip,
                                                                self.port,),
                                                                auth=HTTPBasicAuth(self.username, self.password),
                                                                json=self.params,
                                                                verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_11_get_users(self):
        global client_uuid
        try:
            r = requests.get("https://%s:%s/api/v1/rot/users" %(self.ip,
                                                                self.port),
                                                                auth=HTTPBasicAuth(self.username, self.password),
                                                                verify=self.cert)
            data = r.json()["users"]
            test_uuid = len(data)-1
            client_uuid = data[test_uuid]["client_uuid"]
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)
    
    def test_12_delete_user(self):
        try:
            r = requests.delete("https://%s:%s/api/v1/rot/user/%s" %(self.ip,
                                                                     self.port,
                                                                     client_uuid),
                                                                     auth=HTTPBasicAuth(self.username, self.password),
                                                                     verify=self.cert)
            r = r.status_code
        except requests.ConnectionError:
               r = 111
        self.assertEqual(r, 200)

if __name__ == '__main__':
    
    config_params = None

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    if os.path.exists(CONF_FILE):
        with open(CONF_FILE) as f:
            config_params = json.load(f)
    print(config_params)

    if config_params is None:
        sys.exit(0)

    unittest.main()
