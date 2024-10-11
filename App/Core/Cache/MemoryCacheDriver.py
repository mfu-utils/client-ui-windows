from App.Core.Abstract import AbstractCacheDriver
from App.Core.Utils import DotPathAccessor

from typing import Any


class MemoryCacheDriver(AbstractCacheDriver):
    def __init__(self):
        self.__storage = DotPathAccessor({})

    def get(self, path: str) -> Any:
        return self.__storage.get(path)

    def set(self, key: str, value: Any):
        self.__storage.set(key, value)

    def clear(self):
        self.__storage = DotPathAccessor({})
