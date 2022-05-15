import json
import time
import logging

from serrano_rot.utils.enums import ResponseStatus
import serrano_rot.controller.dbHandler as dbHandler

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

logger = logging.getLogger("SERRANO.ROT.Dispatcher")


class Dispatcher(QObject):
    dispatcherRequest = pyqtSignal(object)
    executionResponse = pyqtSignal(object)

    def __init__(self, config):
        super(QObject, self).__init__()

        self.engines = []
        self.executions_per_engine = {}
        self.client_uuid_per_execution_id = {}
        self.dbHandler = dbHandler.DBHandler(config["heartbeat_limit"])
        self.bookkeepingTimer = QTimer()
        self.bookkeepingTimer.timeout.connect(self.__bookkeeping_engines)
        self.bookkeepingTimer.start(90000)

        logger.info("Dispatcher is ready ...")

    def __bookkeeping_engines(self):
        engine_ids = self.dbHandler.check_engines()
        for eid in engine_ids:
            self.engines.remove(eid)
            del self.executions_per_engine[eid]
            self.dbHandler.set_engine_inactive(eid)
            logger.info("Lost engine '%s' - set it inactive" % eid)

        # TODO -> check for pending assigned executions at affected engines and "reschedule" them

    def __schedule_execution_request(self):
        # Minimal logic , assign the request to the execution engine with the fewest active executions
        n = 9999
        engine_id = ""
        for k, v in self.executions_per_engine.items():
            if len(v) < n:
                n = len(v)
                engine_id = k

        return engine_id

    # SLOT Method
    def handle_access_request(self, data):
        logger.debug("Request parameters: %s" % data)
        if data["cmd"] == "create":
            if len(self.engines) == 0:
                logging.debug("No available engines, execution request is discarded.")
                print("CHECK FOR DISPATCHER NOTIFICATION EVENT")
                return
            engine_id = self.__schedule_execution_request()
            self.executions_per_engine[engine_id].append(data["execution_id"])
            self.client_uuid_per_execution_id[data["execution_id"]] = data["client_uuid"]
            self.dbHandler.update_engine_total_executions(engine_id)
            self.dbHandler.update_execution_engine_assignment(data["execution_id"], engine_id)
            self.dbHandler.add_log_entry(data["execution_id"], "Dispatcher", "Assigned to engine_id: %s" % engine_id)
            logger.debug("Execution '%s' is assigned to engine: '%s'" % (data["execution_id"], engine_id))
            self.dispatcherRequest.emit(
                {"engine_id": engine_id, "action": "start", "execution_id": data["execution_id"],
                 "execution_plugin": data["request_params"]["execution_plugin"],
                 "parameters": data["request_params"]["parameters"]})

        elif data["cmd"] == "terminate":
            if data["execution_id"] in self.executions_per_engine.keys():
                engine_id = self.executions_per_engine[data["execution_id"]]
                k = {"engine_id": engine_id, "action": "cancel", "execution_id": data["execution_id"]}
                self.dbHandler.add_log_entry(data["execution_id"], "Dispatcher", "Request execution terminate.")
            else:
                logger.debug("Unable to find active execution for termination with the requested execution "
                             "id: %s - Request discarded" % data["execution_id"])
        else:
            logger.debug("Request discarded - Invalid requested command: %s" % data["cmd"])

    def handle_engine_response(self, response):
        logger.debug("Handle engine response: %s" % response)
        data = json.loads(response)

        if data["type"] == "heartbeat":
            if data["engine_id"] not in self.engines:
                logger.info("New execution engine is detected.")
                self.engines.append(data["engine_id"])
                self.executions_per_engine[data["engine_id"]] = []
                if self.dbHandler.is_engine_in_db(data["engine_id"]) == 0:
                    self.dbHandler.create_engine_entry(data)
                else:
                    self.dbHandler.update_engine_heartbeat(data)
            else:
                self.dbHandler.update_engine_heartbeat(data)

        elif data["type"] == "execution":
            self.dbHandler.add_log_entry(data["execution_id"], "Dispatcher", "Receive engine response. Status: %s - "
                                                                             "Reason: %s" % (data["status"],
                                                                                             data["reason"]))

            if data["status"] == ResponseStatus.FAILED or data["status"] == ResponseStatus.REJECTED:
                self.dbHandler.update_engine_failed_executions(data["engine_id"])

            self.dbHandler.update_execution_results(data["execution_id"], data["status"], data["results"])
            self.dbHandler.add_log_entry(data["execution_id"], "Results", data["results"])

            if data["execution_id"] in self.client_uuid_per_execution_id:
                client_uuid = self.client_uuid_per_execution_id[data["execution_id"]]
                self.executionResponse.emit({"client_uuid": client_uuid, "uuid": data["execution_id"],
                                             "status": data["status"], "reason": data["reason"],
                                             "results": data["results"]})
                logger.debug("Response for execution '%s' is forwarded at client '%s'" % (data["execution_id"],
                                                                                          client_uuid))
                del self.client_uuid_per_execution_id[data["execution_id"]]
            else:
                logger.error("Unable to forward response. Unknown client for execution '%s'" % data["execution_id"])

        else:
            logger.debug("Unsupported response type, message is discarded.")
