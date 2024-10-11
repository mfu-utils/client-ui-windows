from abc import ABC, abstractmethod


class AbstractRequest(ABC):
    def __init__(self, data: dict):
        self._data = data

    def data(self) -> dict:
        return self._data

    @staticmethod
    @abstractmethod
    def type() -> int:
        pass
