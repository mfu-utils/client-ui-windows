import json
from typing import List, Type, Dict, Union, Any
from enum import Enum


class Casts:
    @staticmethod
    def enum2dict(enum: Union[Type[Enum], List[Enum]], names: Dict[str, str] = None) -> dict:
        if not names:
            names = {}

        return dict(map(lambda x: (x.value, names.get(x.value) or x.name), enum))

    @staticmethod
    def str2bool(value: str) -> bool:
        value = value.lower()

        if value in ['yes', 'true', 't', 'y', '1']:
            return True
        elif value in ['no', 'false', 'f', 'n', '0']:
            return False

        raise ValueError(f'Value {value} is not a boolean')

    @staticmethod
    def bool2str(value: bool) -> str:
        return "True" if value else "False"

    @staticmethod
    def str2float(value: str) -> float:
        if value.isdecimal():
            return float(value)

        return 0.0

    @staticmethod
    def str2int(value: str) -> int:
        if value.isdigit():
            return int(value)

        return 0

    @staticmethod
    def str2list(value: str) -> List[Any]:
        return json.loads(value or '[]')

    @staticmethod
    def str2int_list(value: str) -> list:
        return list(map(lambda x: int(x), Casts.str2list(value)))

    @staticmethod
    def list2str(value: List[Any]) -> str:
        return json.dumps(value)

    @staticmethod
    def str_to(value: str, _type: Union[bool, float, list, int, str, Type[Enum], type], nullable: bool = False):
        if _type == str:
            return value

        if nullable and value == '':
            return None

        if _type == bool:
            return Casts.str2bool(value)

        if _type == int:
            return Casts.str2int(value)

        if _type == float:
            return Casts.str2float(value)

        if _type == list:
            return Casts.str2list(value)

        if issubclass(_type, Enum):
            return _type(value)

        return value

    @staticmethod
    def to_str(value: Union[bool, float, list, int, str, Enum]) -> str:
        if isinstance(value, bool):
            return Casts.bool2str(value)

        if isinstance(value, int):
            return str(value)

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, list):
            return Casts.list2str(value)

        return value
