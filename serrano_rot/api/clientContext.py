import logging
import clientEvents
import responseInterface

logger = logging.getLogger("SERRANO.ROT.API.ClientContext")


class ClientContext(object):

    def __init__(self, client_uuid, client_username, client_password, controller_address, rest_port, zmq_port):
        self.__client_uuid = client_uuid
        self.__client_username = client_username
        self.__client_password = client_password
        self.__controller_address = controller_address
        self.__rest_port = rest_port
        self.__zmq_port = zmq_port

        self.__responseInterface = responseInterface.ResponseInterface({"client_uuid": self.__client_uuid,
                                                                        "controller_address": self.__controller_address,
                                                                        "zmq_port": self.__zmq_port})
        self.__responseInterface.controllerResponse.connect(self.__handle_rot_response)
        self.__responseInterface.start()

        self.__events_handlers = dict()

    def __handle_rot_response(self, evt):
        if evt.response["status"] == 2:
            self.__notify_event_handlers(clientEvents.EventExecutionCompleted(evt.response))
        else:
            self.__notify_event_handlers(clientEvents.EventExecutionError(evt.response))

    def __notify_event_handlers(self, event):

        event_name = event.__class__.__name__

        if event_name not in self.__events_handlers.keys():
            return

        for handler in self.__events_handlers[event_name]:
            handler(event)

    def get_client_uuid(self):
        return self.__client_uuid.encode("ascii")

    def get_rest_url(self):
        return "http://%s:%s" % (self.__controller_address, self.__rest_port)

    def get_http_basic_auth(self):
        return self.__client_username, self.__client_password

    def connect(self, events, handler):

        for evt in events:
            if evt.__name__ not in self.__events_handlers.keys():
                self.__events_handlers[evt.__name__] = [handler]
            else:
                self.__events_handlers[evt.__name__].append(handler)
