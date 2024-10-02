from enum import Enum
from types import NoneType
from typing import Union, Type, Tuple, List, Optional

_DTOFieldType_LIST = [str, list, int, float, bool, Type[Enum]]
_DTOFieldType = Union[*_DTOFieldType_LIST]

Nullable = Optional


class AbstractDTO:
    """
    Abstract DTO:
    type_of(name: str) -> Tuple[bool, <type>] - Get type of user field.
    Type may be only item of [str, list, int, float, bool, enum].
    And may be NULL. Please use Optional[...] or Union[<Type>, NoneType] of define nullable field.
    Return: Tuple[bool, <type>]. 1 - Is Nullable. 2 - Filed type.
    """

    def __init__(self, *args, **kwargs):
        self._fields_list = self._get_fields_list()

        for i, arg in enumerate(args):
            self.__setattr__(self._fields_list[i], arg)

        for key, val in kwargs.items():
            self.__setattr__(key, val)

        self._fields_types_meta = {}

        self._prepare()

    def _get_fields_list(self) -> List[str]:
        items = []

        for field in list(self.__class__.mro()[0].__annotations__.keys()):
            if '_' == field[0]:
                continue

            items.append(field)

        return items

    def _prepare(self):
        for filed in self._fields_list:
            _types = self._get_types_of(filed)

            self._check_field_types(filed, _types)

            if nullable := NoneType in _types:
                nullable = _types.pop(_types.index(NoneType))

            self._fields_types_meta.update({filed: (nullable, _types[0])})

    def _get_types_of(self, name: str) -> List[Union[*_DTOFieldType_LIST, NoneType]]:
        try:
            types = self.__annotations__[name].__reduce__()

            if type(types[1]) is tuple:
                return [_type for _type in types[1][1]]
        except (KeyError, TypeError):
            pass

        return [self.__getattribute__(name).__class__]

    def field_is_nullable(self, name: str) -> bool:
        return self._fields_types_meta[name][0]

    @staticmethod
    def _check_field_types(name: str, _types: List[Union[*_DTOFieldType_LIST, NoneType]]):
        _types_len = len(_types)

        if _types_len > 2:
            raise Exception(f"({name}) Dto field cannot be has more then 1 types. But can be nullable")

        if _types_len == 2 and not (NoneType in _types):
            raise Exception(f"({name}) Second type must be null.")

        if _types_len == 1:
            if NoneType in _types:
                raise Exception(f"({name}) Dto field cannot be only null type.")
            elif _types[0] in _types:
                return
        else:
            l_types = _types.copy()
            l_types.pop(_types.index(NoneType))

            if l_types[0] not in _DTOFieldType_LIST:
                return

        raise Exception(f"({name}) Type must be one of [{', '.join(map(lambda x: str(x), _DTOFieldType_LIST))}] and nullable.")

    def type_of(self, name: str) -> Tuple[bool, _DTOFieldType]:
        return self._fields_types_meta[name]

    # noinspection PyMethodMayBeStatic
    def as_dict(self) -> dict:
        return dict(map(lambda x: (x, self.__getattribute__(x)), self._fields_list))
