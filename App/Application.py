from enum import Enum

from App.Core.Abstract import SingletonMeta
from App.Core.DataFiles import YamlDataFile
from importlib import import_module
from inspect import signature

from App.Core.Utils.Import import Import
from config import CONFIG_FILE_SERVICES
from typing import Optional, List, Union


class Application(YamlDataFile, metaclass=SingletonMeta):
    primitive_types = [int, str, bool, float, list, dict]

    instance = None

    class ApplicationType(Enum):
        Console = 1
        Client = 2
        ClientUI = 3
        Server = 4

    def __init__(self, _type: ApplicationType = None):
        if _type is None:
            raise TypeError('Application type cannot be None In first init.')

        self.__type = _type

        super().__init__(CONFIG_FILE_SERVICES)

        self.__singletons = {}
        self.__providers = {}
        self.__container = {}
        self.__aliases = {}
        self.__abstracts = {}
        self.__controllers = {}

        for namespace, data in self._data['abstracts'].items():
            self.__abstracts[self.__get_full_namespace(namespace)] = data

        for name, data in self._data['providers'].items():
            self.__register_provider(name, data)

        for namespace, data in self._data['services'].items():
            self.__register_service(namespace, data)


    def type(self) -> ApplicationType:
        return self.__type

    def __get_full_namespace(self, namespace: str) -> str:
        if concrete := self.__aliases.get(namespace):
            return concrete

        return '.'.join(Import.parse_import(namespace))

    def __add_controller(self, file: str, namespace: str):
        name = file.split('.')[0]

        if not name.endswith('Controller'):
            return

        alias = Import.create_controller_alias(name)

        self.register(f"{namespace}.{name}!", False, {}, {}, f"controller.{alias}")

    def __get_abstract(self, namespace: str):
        namespace = self.__get_full_namespace(namespace)

        if namespace not in self.__aliases:
            if namespace in self.__abstracts:
                self.__register_abstract(namespace, self.__abstracts[namespace])

        return self.get(namespace)

    def __register_abstract(self, namespace: str, data: Union[dict, str]):
        if type(data) is str:
            self.__aliases[namespace] = self.__get_full_namespace(data)
            self.__register_service(data)
            return

        parameter = self.__providers[data['provider']](data['parameter'])

        for value, concrete in data['match'].items():
            if parameter == value:
                self.__aliases[namespace] = self.__get_full_namespace(concrete)
                self.__register_service(concrete)
                return

        raise Exception(f"Cannot register abstract '{namespace}'")

    def register_type(self, _type: Union[type, object], data: Optional[dict] = None):
        namespace = _type.__module__

        namespace = f"{namespace}.{_type.__name__}" if namespace else _type.__name__

        self.__register_service(namespace, data)

    def __register_service(self, namespace: str, data: Optional[dict] = None):
        data = data or {}

        self.register(
            namespace,
            data.get('singleton') or False,
            data.get('parameters') or {},
            data.get('bindings') or {},
            data.get('alias') or None,
        )

    def __register_provider(self, name: str, data: list):
        self.__providers[name] = lambda x: self.get(data[0]).__getattribute__(data[1])(x)

    def __resolve_deps(self, obj, positional: tuple, argv: dict, bindings: dict):
        args = {}

        for key, _type in signature(obj).parameters.items():
            if str(_type) in ['self', '*args', '**kwargs']:
                continue

            if key == 'app':
                args[key] = self

                continue

            if len(positional) > 0:
                args[key] = positional[0]

                positional = positional[1:]

                continue

            if _type.annotation in self.primitive_types:
                args[key] = argv.get(key)
                continue

            annotation = _type.annotation

            _type = f"{annotation.__module__}.{annotation.__name__}"

            if binding_type := bindings.get(_type):
                _type = binding_type

            args[key] = self.__get_abstract(_type) if _type in self.__abstracts else self.get(_type)

        return args

    def __resolve_type(self, namespace: str, _class: str, argv: dict, bindings: dict):
        obj = import_module(namespace).__getattribute__(_class)

        return obj(**self.__resolve_deps(obj.__init__, (), argv, bindings))

    def __resolve_singleton(self, name: str) -> object:
        data = self.__get_container_type_data(name)

        namespace = f"{data['file']}.{data['class']}"

        if namespace not in self.__singletons:
            self.__singletons[namespace] = self.new(namespace)

        return self.__singletons[namespace]

    def __get_container_type_data(self, name: str) -> dict:
        if namespace := self.__aliases.get(name):
            name = namespace

        return self.__container[name]

    def get(self, name: str):
        if not self.has(name):
            print(f'Cannot find "{name}". This type not found.')

        if self.__get_container_type_data(name)['singleton']:
            return self.__resolve_singleton(name)

        return self.new(name)

    def has(self, name: str) -> bool:
        return bool(self.__aliases.get(name) or self.__container.get(name))

    def new(self, name: str) -> object:
        if not self.has(name):
            print(f'Cannot get "{name}". This type not found.')

        data = self.__get_container_type_data(name)

        return self.__resolve_type(data['file'], data['class'], data['argv'], data['bindings'])

    def register(self, namespace: str, singleton: bool, argv: dict, bindings: dict, alias: Optional[str] = None):
        if alias:
            if self.has(alias):
                print(f'Cannot register "{alias}". This object already exists.')

        file, _class = Import.parse_import(namespace)

        namespace = f'{file}.{_class}'

        if alias:
            self.__aliases[alias] = namespace

        bindings = dict(map(lambda x: (self.__get_full_namespace(x[0]), x[1]), bindings.items()))

        self.__container[namespace] = {
            'file': file,
            'class': _class,
            'argv': argv,
            'singleton': singleton,
            'bindings': bindings,
        }

    def __get_callable(self, name: Union[List[str], str]):
        if type(name) is str:
            segments = name.split('.')

            _class, _func = ['.'.join(segments[:-1]), segments[-1]]
        else:
            _class, _func = name

        if not self.has(_class):
            print(f'Cannot call "{_class}". This object not found.')

        return self.get(_class).__getattribute__(_func)

    def call(self, name: Union[List[str], str, callable], *args, **kwargs):
        func = name

        if type(name) in [str, list]:
            func = self.__get_callable(name)

        return func(**self.__resolve_deps(func, args, kwargs, {}))
