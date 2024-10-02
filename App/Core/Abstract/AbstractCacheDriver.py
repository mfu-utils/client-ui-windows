from abc import ABC, abstractmethod
from typing import Any


class AbstractCacheDriver(ABC):
    @abstractmethod
    def get(self, key: str) -> dict:
        pass

    @abstractmethod
    def set(self, key: str, value: Any):
        pass

    @abstractmethod
    def clear(self):
        pass
