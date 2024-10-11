from abc import ABC, abstractmethod
from typing import Union


class AbstractResponse(ABC):
    def __init__(self, data: Union[str, dict, list, bytes, None]):
        self._data = data

    def data(self) -> Union[str, dict, list, bytes, None]:
        return self._data

    @staticmethod
    @abstractmethod
    def type() -> int:
        pass
