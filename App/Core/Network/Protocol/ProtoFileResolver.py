import re
from typing import Union, Tuple, Optional

from App.Core import Config
from App.Core.DataFiles import YamlDataFile


class ProtoFileResolver(YamlDataFile):
    PRIMITIVE_TYPES = [int, float, bool, str]

    PREG_TYPE = re.compile(r'^(\?)?([^[$]+)(?:\[(?:([^,]+),\s*([^]]+)|([^]]+))])?$')
    PREG_SUB_TYPE = re.compile(r'^(\?)?([^[$]+)$')

    TYPES_MAP = {
        "bytes": bytes,
        "float": float,
        "bool": bool,
        "int": int,
        "str": str,
    }

    # 'name': [can be null, has key, has value]
    OBJECT_TYPES_MAP = {
        'float': [True, False, False],
        'array': [False, False, True],
        'bool': [True, False, False],
        'int': [True, False, False],
        'str': [True, False, False],
        'map': [False, True, True],
    }

    def __init__(self, config: Config):
        self.__config = config.get('rcl')

        super().__init__(self.__config['proto_file_path'])

        self.__commands = {}
        self.__codes = {}
        self.__types = {}

    @staticmethod
    def __validate_number_parameters(number: Union[str, int], name: str) -> bool:
        required = False
        _type = type(number)

        if _type not in [str, int]:
            raise Exception(f"Invalid parameter numbers in parameter '{name}'")

        if _type is str:
            if number not in ['+', '*']:
                raise Exception(f"Parameter number must be `int` type or '+', '*' strings in parameter '{name}'")

            if number == '+':
                required = True

        if _type is int:
            if number < 0:
                raise Exception(f"Parameter number cannot be < 0 in parameter '{name}'")

            if number > 0:
                required = True

        return required

    def __prepare_proto_parameter(self, code: int, name: str, parameter_data: dict):
        default = None
        number = parameter_data.get('number')

        required = self.__validate_number_parameters(number, name) if number else None

        if not required:
            default = parameter_data.get('default')

        if _type := parameter_data.get('type'):
            if _type not in self.TYPES_MAP:
                raise Exception(f"Type {_type} not supported")

            _type = self.TYPES_MAP[_type]

            if required and (not type(default) is _type):
                raise Exception(f"Type default parameter must be '{_type.__name__}'")

        _type = _type or str
        _variants = {}

        if variants := parameter_data.get('variants'):
            if type(variants) is not list:
                raise Exception(f"Variants for parameter {name} must be list")

            for i, variant in enumerate(variants):
                if not type(variant) is _type:
                    raise Exception(f"Variant {str(variant)} is not of type {_type.__name__}")

                _variants.update({variant: i})

        if number := parameter_data.get('number'):
            self.__validate_number_parameters(number, name)

        return {
            "code": code,
            "default": default,
            "variants": _variants,
            "type": _type,
            "number": number
        }

    def __parse_parameters(self, parameters: dict) -> Tuple[dict, dict, dict]:
        parameters_data = {}
        codes = {}
        defaults = {}

        for i, (name, parameter_data) in enumerate(parameters.items()):
            data = self.__prepare_proto_parameter(i, name, parameter_data)

            if default := data.get("default"):
                defaults.update({name: default})

            parameters_data.update({name: data})

            codes[i] = {
                "name": name,
                "variants": dict(map(lambda x: (x[1], x[0]), data['variants'].items()))
            }

        return codes, parameters_data, defaults

    def __parse_subcommands(self, subcommands: dict) -> Tuple[dict, dict]:
        subcommands_data = {}
        codes = {}

        for i, (name, subcommand_data) in enumerate(subcommands.items()):
            parameters_data = subcommand_data.get('parameters')

            parameters_codes, parameters, defaults = self.__parse_parameters(parameters_data) if parameters_data else ({}, {}, {})

            subcommands_data.update({name: {
                'code': i,
                'parameters': parameters,
                'defaults': defaults,
            }})

            codes[i] = {
                "name": name,
                "parameters": parameters_codes
            }

        return codes, subcommands_data

    def __validate_key_type(self, key_type: str):
        nullable, typename = self.PREG_SUB_TYPE.findall(key_type)[0]

        nullable = bool(nullable)

        if nullable:
            raise Exception(f"Type '{typename}' cannot be nullable.")

        self.__validate_type(False, typename)

    def __parse_value_type(self, value_type: str) -> dict:
        nullable, typename = self.PREG_SUB_TYPE.findall(value_type)[0]

        nullable = bool(nullable)

        self.__validate_type(nullable, typename)

        return {
            "type": typename,
            "nullable": nullable,
        }

    def __validate_type(self, nullable: bool, _type: str, key_type: Optional[str] = None, value_type: Optional[str] = None):
        if not _type:
            raise Exception("Type cannot be empty.")

        if not (type_data := self.OBJECT_TYPES_MAP.get(_type)):
            raise Exception(f"Undefined type '{_type}'.")

        if not type_data[0] and nullable:
            raise Exception(f"Type '{_type}' cannot be nullable.")

        if not type_data[1] and key_type:
            raise Exception(f"Type '{_type}' cannot contain key type.")

        if not type_data[2] and value_type:
            raise Exception(f"Type '{_type}' cannot contain value type.")

        if key_type:
            self.__validate_key_type(key_type)

    def __parse_object_type(self, _type: str) -> dict:
        nullable, typename, key_type, value_type, once_type = self.PREG_TYPE.findall(_type)[0]

        nullable = bool(nullable)
        key_type = key_type or None

        self.__validate_type(nullable, typename, key_type, value_type or once_type)

        return {
            'type': typename,
            'nullable': nullable,
            'key_type': key_type,
            'value_type': self.__parse_value_type(value_type) if value_type else None,
        }

    def __parse_object_fields(self, object_fields: dict) -> dict:
        parameters = {}

        for key, _type in object_fields.items():
            parameters.update({key: self.__parse_object_type(_type)})

            self.OBJECT_TYPES_MAP.update({key: [True, False, False]})

        return parameters

    def parse(self):
        for i, (obj_name, obj_data) in enumerate((self.data().get('objects') or {}).items()):
            self.__types[obj_name] = self.__parse_object_fields(obj_data)

        for i, (name, command_data) in enumerate((self.data().get("commands") or {}).items()):
            subcommands_data = command_data.get('subcommands')
            parameters_data = command_data.get('parameters')

            subcommands_codes, subcommands_data = self.__parse_subcommands(
                subcommands_data
            ) if subcommands_data else ({}, {})

            parameters_codes, parameters_data, defaults = self.__parse_parameters(
                parameters_data
            ) if parameters_data else ({}, {}, {})

            self.__commands[name] = {
                "code": i,
                "subcommands": subcommands_data,
                "parameters": parameters_data,
                "defaults": defaults,
            }

            self.__codes[i] = {
                "name": name,
                "subcommands": subcommands_codes,
                "parameters": parameters_codes,
            }

        return self.__commands, self.__codes, self.__types
