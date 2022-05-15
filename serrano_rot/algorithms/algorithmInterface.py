import abc
import json


class AlgorithmInterface(metaclass=abc.ABCMeta):

    def __init__(self, parameters):
        self.__parameters = json.loads(parameters)
        self.__INPUT_PARAM1 = {"param1": "fobero"}
        self.__INPUT_PARAM2 = {"param2": "tromero"}
        self.__INPUT_PARAM3 = {"param3": "para polu wraioooo"}

    def get_input_param1(self):
        return self.__INPUT_PARAM1

    def get_input_param2(self):
        return self.__INPUT_PARAM2

    def get_input_param3(self):
        return self.__INPUT_PARAM3

    @abc.abstractmethod
    def launch(self):
        pass

