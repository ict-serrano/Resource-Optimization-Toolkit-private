import sys
import signal

import api.clientEvents as clientEvents
import api.clientInstance as clientInstance

from PyQt5.QtCore import QCoreApplication


class Example:

    def __init__(self):
        self.client = None

    def start(self):
        self.client = clientInstance.ClientInstance()

        self.client.connect([clientEvents.EventExecutionCompleted, clientEvents.EventExecutionError], self.print_response)
        self.client.connect([clientEvents.EventEnginesChanged], self.on_engines_changed)

    def on_engines_changed(self, evt):
        print("------------")
        print("available engines changed")
        print(evt)
        print(evt.engine_uuid)
        print(evt.event_id)
        print(evt.timestamp)
        print("-----------------")
        print()

    def print_response(self, evt):
        print()
        print("ROT controller response !!!!")
        print()
        if isinstance(evt, clientEvents.EventExecutionCompleted):
            print(evt.execution_uuid)
            print(evt.results)
            print()
        else:
            print(evt.execution_uuid)
            print(evt.status)
            print(evt.reason)
            print()

    def play_with_rest(self):
        engines = self.client.get_engines()
        print(engines)
        print()

        #k = self.client.post_execution("Dummy2", {"times":2, "length": 8})
        #print(k)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QCoreApplication(sys.argv)

    ex = Example()
    ex.start()

    ex.play_with_rest()

    sys.exit(app.exec_())
