import os
from typing import Any, Optional
from App.Core.Utils import DotPathAccessor

from App.Core.Abstract import AbstractCacheDriver
from App.Core import Filesystem, Config


class FileCacheDriver(AbstractCacheDriver):
    def __init__(self, config: Config):
        self.__path: str = config.get('cache.drivers.file')['path']

        self.__storage: Optional[DotPathAccessor] = None

        if Filesystem().exists(self.__path):
            self.__load_file()
            return

        self.__storage = DotPathAccessor({})
        self.__store_file()

    def __load_file(self):
        self.__storage = DotPathAccessor(Filesystem.read_json(self.__path))

    def __store_file(self):
        if not Filesystem.exists(self.__path):
            os.makedirs(os.path.dirname(self.__path), exist_ok=True)

        Filesystem.write_json(self.__path, self.__storage.data())

    def get(self, path: str) -> Any:
        return self.__storage.get(path)

    def set(self, path: str, value: Any):
        self.__storage.set(path, value)
        self.__store_file()

    def clear(self):
        self.__storage = DotPathAccessor({})
        Filesystem.delete(self.__path)
