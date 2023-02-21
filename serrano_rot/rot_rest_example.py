import time
from enum import IntEnum
import requests


class ResponseStatus(IntEnum):
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3
    REJECTED = 4
    CANCELLED = 5


ROT_SERVICE = "http://rot.wp5.services.cloud.ict-serrano.eu"

ROT_SIMPLE_USER = ("rot_test", "s3rr@no_t3st")
ROT_ADMIN_USER = ("serrano_dev", "s3rr@n0_d3v")


# Get statistics for the completed executions
def rot_service_statistics(auth):
    res = requests.get(f"{ROT_SERVICE}/api/v1/rot/statistics", auth=auth)
    print(res.json())


#  Get the UUIDs of the available execution engines.
def rot_service_engines(auth):
    res = requests.get(f"{ROT_SERVICE}/api/v1/rot/engines", auth=auth)
    print(res.json())
    return res.json()


# Get details for a specific execution engine
def rot_service_engine(engine_uuid, auth):
    res = requests.get(f"{ROT_SERVICE}/api/v1/rot/engine/{engine_uuid}", auth=auth)
    print(res.json())

"""
    Request the execution of a specific algorithm that is integrated in the ROT.
    
    The required request body should include two keys: (a) execution_plugin , (b) parameters
    
    The first is a string whose value corresponds to the requested algorithm. Currently, there 
    are available two algothims: (1) SimpleMatch and (b) Dummy.  The Dummy algorithm is just for 
    testing the framework.
    
    The second parameter is an object whose syntax depends on the algorithm. For example for the Dummy
    is the following { "length": 5, "times":5 } 
"""
def rot_service_request_execution(data, auth):
    res = requests.post(f"{ROT_SERVICE}/api/v1/rot/execution", json=data, auth=auth)
    return res.json()

# Retrieve the full history for all executions for the specific user
def rot_service_history(auth):
    res = requests.get(f"{ROT_SERVICE}/api/v1/rot/history", auth=auth)
    print(res.json())

# Retrieve the current list of all active executions, their status is Pending or Started
def rot_service_executions(auth):
    res = requests.get(f"{ROT_SERVICE}/api/v1/rot/executions", auth=auth)
    print(res.json())

# Retrieve details for the current state of an execution request
def rot_service_get_execution(execution_id, auth):
    res = requests.get(f"{ROT_SERVICE}/api/v1/rot/execution/{execution_id}", auth=auth)
    print(res.json())

# Retrieve detailed logging information for a specific execution request
def rot_service_get_execution_logs(execution_id, auth):
    res = requests.get(f"{ROT_SERVICE}/api/v1/rot/logs/{execution_id}", auth=auth)
    print(res.json())

#################
#   EXAMPLES    #
#################

""" 
  The following three requests are available only to user that are created with admin rights. 
  For ROT_ADMIN_USER are executed successfully, for ROT_SIMPLE_USER we get error
"""

"""
rot_service_statistics(ROT_ADMIN_USER)
res = rot_service_engines(ROT_ADMIN_USER)
rot_service_engine(res["engines"][0], ROT_ADMIN_USER)

rot_service_statistics(ROT_SIMPLE_USER)
rot_service_engines(ROT_SIMPLE_USER)
rot_service_engine(res["engines"][0], ROT_SIMPLE_USER)
"""

"""
  The following example requests a valid execution and then check the status its status
"""

"""
valid_data = {"execution_plugin": "Dummy", "parameters": {"length": 5, "times": 5}}
res = rot_service_request_execution(valid_data, ROT_SIMPLE_USER)
print(res)
time.sleep(2)
execution_id = res["execution_id"]
rot_service_get_execution(execution_id, ROT_SIMPLE_USER)

# This request will not return anything, since the targeted request is made from other user
rot_service_get_execution(execution_id, ROT_ADMIN_USER)

# Retrieve extensive details for a specific request
rot_service_get_execution_logs(execution_id, ROT_SIMPLE_USER)
"""

"""
  The following example requests a valid execution and then check the status its status
"""


"""  
 The following examples get the list of all executions for the specific user 
"""
rot_service_history(ROT_SIMPLE_USER)
rot_service_history(ROT_ADMIN_USER)

"""  
 The following examples get the list of active executions for the specific user 
"""
rot_service_executions(ROT_SIMPLE_USER)
rot_service_executions(ROT_ADMIN_USER)

"""
invalid_valid_data = {"execution_plugin": "SomePlugin", "parameters": {"length": 5, "times": 5}}
data_2 = {"execution_plugin": "Dummy", "parameters": {"length": 5, "ts": 5}}
"""
