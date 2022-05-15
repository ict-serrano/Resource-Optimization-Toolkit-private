import zmq
import json
import clientEvents
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal


class ResponseInterface(QThread):
    controllerResponse = pyqtSignal(object)

    def __init__(self, config):
        QThread.__init__(self)

        self.__zmq_context = zmq.Context()
        self.__connection_url = "tcp://%s:%s" % (config["controller_address"], config["zmq_port"])

        self.__zmq_socket = self.__zmq_context.socket(zmq.DEALER)
        self.__zmq_socket.setsockopt(zmq.IDENTITY, config["client_uuid"].encode("ascii"))

    def __del__(self):
        self.wait()

    def run(self):
        self.__zmq_socket.connect(self.__connection_url)

        try:
            while True:
                res = self.__zmq_socket.recv()
                self.controllerResponse.emit(clientEvents.ControllerResponse(json.loads(res)))
        except KeyboardInterrupt:
            pass
        finally:
            print("!!!!!")
            self.__zmq_socket.close(0)
            self.__zmq_context.destroy(0)

