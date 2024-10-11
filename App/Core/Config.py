from importlib import import_module

from App.Core.Utils import DotPathAccessor
from typing import Any

from App.Core.Filesystem import Filesystem
from config import ROOT, CONFIG_FILES_METADATA


class Config:
    cache = {}
    meta = {}

    def __init__(self):
        self.__type_loaders = {
            'py': self._load_py,
            'json': self._load_json,
            'yml': self._load_yml,
        }

        keys = list(self.__type_loaders.keys())

        for namespace, data in Filesystem.read_yaml(CONFIG_FILES_METADATA).items():
            _type = data['type']

            if _type not in keys:
                raise Exception(f'Cannot create meta data with incorrect type: "{_type}"')

            for file in data['files']:
                self.meta[file] = {
                    'namespace': namespace,
                    'type': _type
                }

    @staticmethod
    def _load_py(name: str):
        return import_module(name).__getattribute__("__CONFIG__")

    @staticmethod
    def _load_json(name: str):
        return Filesystem.read_json(f"{ROOT}/{name}.json")

    @staticmethod
    def _load_yml(name: str):
        return Filesystem.read_yaml(f"{ROOT}/{name}.yml")

    @staticmethod
    def _create_path(namespace: str, name: str, _type: str) -> str:
        namespace = f"{namespace}.{name}"

        if _type == 'py':
            return namespace

        return namespace.replace('.', '/')

    def __load_file(self, name: str):
        meta = self.meta[name]
        _type = meta['type']

        data = self.__type_loaders[_type](self._create_path(meta['namespace'], name, _type))

        self.cache[name] = DotPathAccessor(data)

    def __has_file(self, name: str) -> bool:
        return bool(self.cache.get(name))

    def set(self, dot_path: str, value):
        segments = dot_path.split('.')

        if not self.__has_file(name := segments[0]):
            self.__load_file(name)

        item = self.cache[name]
        item.set(segments[1:], value)

    def get(self, dot_path: str, default: Any = None) -> Any:
        segments = dot_path.split('.')

        if not segments[0]:
            return default

        if not self.__has_file(name := segments[0]):
            self.__load_file(name)

        item = self.cache[name]

        if not item:
            return default

        if dot_path == segments[0]:
            return item.data()

        try:
            return item.get(segments[1:])
        except KeyError:
            return default
