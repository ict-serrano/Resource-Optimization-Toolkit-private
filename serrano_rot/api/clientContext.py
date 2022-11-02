from serrano_rot.api import clientEvents
from serrano_rot.api import asynchInterface


class ClientContext:

    def __init__(self, client_uuid, databroker):

        self.__events_handlers = dict()

        self.asynchInterface = asynchInterface.AsynchInterface(client_uuid, databroker)
        self.asynchInterface.rotResponse.connect(self.__handle_rot_response)
        self.asynchInterface.rotNotification.connect(self.__handle_rot_notification)
        self.asynchInterface.start()

    def __handle_rot_notification(self, notification_params):
        self.__notify_event_handlers(clientEvents.EventEnginesChanged(notification_params))

    def __handle_rot_response(self, evt):
        print(evt)
        if evt.response["status"] == 2:
            self.__notify_event_handlers(clientEvents.EventExecutionCompleted(evt.response))
        elif evt.response["status"] == 3:
            self.__notify_event_handlers(clientEvents.EventExecutionError(evt.response))
        elif evt.response["status"] == 4:
            self.__notify_event_handlers(clientEvents.EventExecutionTerminated(evt.response))

    def __notify_event_handlers(self, event):

        event_name = event.__class__.__name__

        if event_name not in self.__events_handlers.keys():
            return

        for handler in self.__events_handlers[event_name]:
            handler(event)

    def connect(self, events, handler):

        for evt in events:
            if evt.__name__ not in self.__events_handlers.keys():
                self.__events_handlers[evt.__name__] = [handler]
            else:
                self.__events_handlers[evt.__name__].append(handler)
