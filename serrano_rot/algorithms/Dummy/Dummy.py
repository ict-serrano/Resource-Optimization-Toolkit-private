import time
import json
import serrano_rot.algorithms.algorithmInterface as algorithmInterface

"""
def Dummy(params):

    return "!!!! - algo output here"
"""


class Dummy(algorithmInterface.AlgorithmInterface):

    def __init__(self, params):
        super().__init__(params)

    def launch(self):
        # self.get_input_param1()
        # self.get_input_param2()
        # self.get_input_param3()
        results = {"kati": "run Forest run !!!", "allo": "run Forest run !!!"}
        time.sleep(1)

        return json.dumps(results)
