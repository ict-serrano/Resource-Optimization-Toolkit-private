import sys
import uuid
import json
import time
import signal
import logging
import os.path
import platform

from PyQt5.QtCore import QTimer, QObject, QCoreApplication

import engine.engineInterface
import engine.executionManager
# import engine.dataBrokerInterface

LOG_LEVEL = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10}


class EngineInstance(QObject):

    def __init__(self):

        super(QObject, self).__init__()

        conf_file = "%s/.rot/engine.json" % os.path.expanduser("~")
        id_file = "%s/.rot/engine_id" % os.path.expanduser("~")

        self.engineInterface = None
        self.executionManager = None
        self.statusTimer = None

        self.hostname = platform.uname()[1]

        with open(conf_file) as f:
            self.config = json.load(f)

        logging.basicConfig(filename="%s.log" % (int(time.time())), level=LOG_LEVEL[self.config["log_level"]])

        # Suppress logging messages from pika only to levels: WARNING,ERROR and CRITICAL
        logging.getLogger('pika').setLevel(logging.WARNING)

        self.logger = logging.getLogger("SERRANO.ROT.EngineInstance")

        if os.path.exists(id_file):
            with open(id_file) as f:
                self.engine_id = f.readline()
        else:
            self.engine_id = str(uuid.uuid4())
            with open(id_file, "w") as f:
                f.write(self.engine_id)

    def boot(self):

        self.logger.info("Initialize services ... ")

        self.executionManager = engine.executionManager.ExecutionManager(self.engine_id)

        self.engineInterface = engine.engineInterface.EngineInterface(self.engine_id, self.config["databroker_interface"])
        self.engineInterface.dispatcherRequest.connect(self.executionManager.handle_dispatch_request)
        self.engineInterface.start()

        self.executionManager.forwardResponse.connect(self.engineInterface.forward_response)
        # self.executionHelper =

        self.engine_heartbeat()

        self.statusTimer = QTimer(self)
        self.statusTimer.timeout.connect(self.engine_heartbeat)
        self.statusTimer.start(int(self.config["heartbeat"])*1000)

        self.logger.info("ROT execution engine is ready ...")

    def engine_heartbeat(self):
        self.engineInterface.forward_response(json.dumps({"engine_id": self.engine_id, "type": "heartbeat",
                                                          "timestamp": int(time.time()), "hostname": self.hostname}))


if __name__ == "__main__":

    if os.path.exists("%s/.rot/engine.json" % os.path.expanduser("~")):

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # We don't need GUI dependencies only acess to event-loop, hence instead of 
        # PyQt5.QtWidgets.QApplication we should use the PyQt5.QCore.QCoreApplication
        app = QCoreApplication(sys.argv)

        instance = EngineInstance()
        instance.boot()

        sys.exit(app.exec_())
    else:

        print("")
        print("Unable to find the required configuration file at the predefined location")
        print("")
