from abc import ABC


class AbstractServiceError(ABC):
    __type__ = None

    def __init__(self, error_code: __type__, parameters: dict = None):
        self.__error_code = error_code
        self.__parameters = parameters or {}

    def code(self) -> __type__:
        return self.__error_code

    def parameters(self) -> dict:
        return self.__parameters
