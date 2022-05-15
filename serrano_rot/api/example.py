import sys
import signal

import clientContext
import clientInstance
import clientEvents
from PyQt5.QtCore import QCoreApplication


class Example:

    def __init__(self):
        self.client = None

    def start(self):
        context = clientContext.ClientContext("a3b05c0e-58f9-46c5-b607-a08df512286a", "test", "fr13nd!", "10.100.221.191",
                                              10020, 10030)
        self.client = clientInstance.ClientInstance(context)

        context.connect([clientEvents.EventExecutionCompleted, clientEvents.EventExecutionError], self.print_response)
        context.connect([clientEvents.EventEnginesChanged], self.on_engines_changed)

    def on_engines_changed(self):
        print("available engines changed")

    def print_response(self, evt):
        print("ROT controller response !!!!")
        print(evt)
        if isinstance(evt, clientEvents.EventExecutionCompleted):
            print(evt.execution_uuid)
            print(evt.results)
        else:
            print(evt.execution_uuid)
            print(evt.status)
            print(evt.reason)

    def play_with_rest(self):
        engines = self.client.get_engines()
        print(engines)
        print()
        for engine_uuid in engines:
            print(self.client.get_engine(engine_uuid))
        print()

       
        k = self.client.post_execution("Dummy", {})
        print(k)
        print()
      

        
        for exc in self.client.get_executions():
            print(self.client.get_execution(exc["execution_id"]))
        


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QCoreApplication(sys.argv)

    ex = Example()
    ex.start()

    ex.play_with_rest()

    sys.exit(app.exec_())
