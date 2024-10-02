from typing import Any

from App.Core.Abstract import AbstractCacheDriver
from App.Core.Logger import Log


class CacheManager:
    def __init__(self, driver: AbstractCacheDriver, logger: Log):
        self.__driver: AbstractCacheDriver = driver
        self.__logger: logger

    def get(self, key: str, default: Any = None) -> Any:
        res = self.__driver.get(key)

        if res is None:
            return default

        return res

    def has(self, key: str) -> bool:
        return bool(self.get(key, False))
        
    def set(self, key: str, value: Any):
        return self.__driver.set(key, value)

    def clear_all(self):
        self.__driver.clear()
