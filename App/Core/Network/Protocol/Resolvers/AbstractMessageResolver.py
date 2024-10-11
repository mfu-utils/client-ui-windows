from abc import ABC, abstractmethod
from typing import Union


class AbstractMessageResolver(ABC):
    @abstractmethod
    def create(self, data: Union[dict, list, str, bytes, None]) -> bytes:
        pass

    @abstractmethod
    def parse(self, data: bytes) -> Union[dict, list, str, bytes, None]:
        pass
