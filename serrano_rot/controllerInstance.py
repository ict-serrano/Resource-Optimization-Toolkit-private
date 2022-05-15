import sys
import json
import time
import signal
import os.path
import logging

from PyQt5.QtCore import QObject, QCoreApplication

import controller.dispatcher
import controller.accessInterface
import controller.dataBrokerInterface

LOG_LEVEL = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10}


class ControllerInstance:

    def __init__(self, conf_file):
        self.dispatcher = None
        self.accessInterface = None
        self.dataBrokerInterface = None

        with open(conf_file) as f:
            self.config = json.load(f)

        logging.basicConfig(filename="%s.log" % (int(time.time())), level=LOG_LEVEL[self.config["log_level"]])

        # Suppress logging messages from pika only to levels: WARNING,ERROR and CRITICAL
        logging.getLogger('pika').setLevel(logging.WARNING)

        self.logger = logging.getLogger("SERRANO.ROT.ControllerInstance")

    def boot(self):

        self.logger.info("Initialize services ... ")

        self.dispatcher = controller.dispatcher.Dispatcher(self.config["engines"])

        self.accessInterface = controller.accessInterface.AccessInterface(self.config["rest_interface"])
        self.accessInterface.restInterfaceMessage.connect(self.dispatcher.handle_access_request)
        self.accessInterface.start()

        self.dataBrokerInterface = controller.dataBrokerInterface.DataBrokerInterface(self.config["databroker_interface"])
        self.dataBrokerInterface.engineResponse.connect(self.dispatcher.handle_engine_response)
        self.dispatcher.dispatcherRequest.connect(self.dataBrokerInterface.forward_dispatcher_request)
        self.dispatcher.executionResponse.connect(self.dataBrokerInterface.forward_execution_request_response)
        self.dataBrokerInterface.start()

        self.logger.info("ROT controller is ready ...")


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    config_file = "%s/.rot/config.json" % os.path.expanduser("~")

    # We don't need GUI dependencies only access to event-loop, hence instead of
    # PyQt5.QtWidgets.QApplication we should use the PyQt5.QCore.QCoreApplication
    app = QCoreApplication(sys.argv)

    if len(sys.argv) == 2:
        config_file = sys.argv[1]

    instance = ControllerInstance(config_file)
    instance.boot()

    sys.exit(app.exec_())
