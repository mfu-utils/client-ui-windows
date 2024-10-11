from abc import ABC


class AbstractServiceWarning(ABC):
    __type__ = None

    def __init__(self, warning_code: __type__, parameters: dict = None):
        self.__warning_code = warning_code
        self.__parameters = parameters or {}

    def code(self) -> __type__:
        return self.__warning_code

    def parameters(self) -> dict:
        return self.__parameters
