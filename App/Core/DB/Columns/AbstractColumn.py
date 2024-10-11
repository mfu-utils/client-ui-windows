from abc import ABC
from typing import Any, Literal, Union, Optional, Type

from sqlalchemy import Column, TextClause, ColumnElement
from sqlalchemy.sql.base import SchemaEventTarget
from sqlalchemy.sql.schema import SchemaConst, FetchedValue

_TypeEngineArgument = Union[Type["TypeEngine[_T]"], "TypeEngine[_T]"]


# __name_pos: str | Type[TypeEngine[_T]] | TypeEngine[_T] | SchemaEventTarget | None = None,
# __type_pos: Type[TypeEngine[_T]] | TypeEngine[_T] | SchemaEventTarget | None = None,
# *args: SchemaEventTarget,
# name: str | None = None,
# type_: Type[TypeEngine[_T]] | TypeEngine[_T] | None = None,
# autoincrement: Literal["auto", "ignore_fk"] | bool = "auto",
# default: Any | None = _NoArg.NO_ARG,
# insert_default: Any | None = _NoArg.NO_ARG,
# doc: str | None = None,
# key: str | None = None,
# index: bool | None = None,
# unique: bool | None = None,
# info: dict | None = None,
# nullable: bool | SchemaConst | None = SchemaConst.NULL_UNSPECIFIED,
# onupdate: Any | None = None,
# primary_key: bool = False,
# server_default: FetchedValue | str | TextClause | ColumnElement | None = None,
# server_onupdate: FetchedValue | None = None,
# quote: bool | None = None,
# system: bool = False,
# comment: str | None = None,
# insert_sentinel: bool = False,
# _omit_from_statements: bool = False,
# _proxies: Any | None = None,
# **dialect_kwargs: Any


class AbstractColumn(ABC):
    def __init__(
        self,
        __name_pos: Any = None,
        __type_pos: Any = None,
        *args: SchemaEventTarget,
        name: Optional[str] = None,
        type_: Any = None,
        autoincrement: Union[Literal["auto", "ignore_fk"], bool] = "auto",
        default: Optional[Any] = 0,
        insert_default: Optional[Any] = 0,
        doc: Optional[str] = None,
        key: Optional[str] = None,
        index: Optional[bool] = None,
        unique: Optional[bool] = None,
        info: Optional[dict] = None,
        nullable: Union[bool, SchemaConst, None] = SchemaConst.NULL_UNSPECIFIED,
        onupdate: Optional[Any] = None,
        primary_key: bool = False,
        server_default: Union[FetchedValue, str, TextClause, ColumnElement, None] = None,
        server_onupdate: Optional[FetchedValue] = None,
        quote: Optional[bool] = None,
        system: bool = False,
        comment: Optional[str] = None,
        insert_sentinel: bool = False,
        _omit_from_statements: bool = False,
        _proxies: Optional[Any] = None,
        **dialect_kwargs: Any
    ):
        self.__name_pos = __name_pos
        self.__type_pos = __type_pos
        self.__pos_args = args
        self.__name = name
        self.__type = type_
        self.__autoincrement = autoincrement
        self.__default = default
        self.__insert_default = insert_default
        self.__doc = doc
        self.__key = key
        self.__index = index
        self.__unique = unique
        self.__info = info
        self.__nullable = nullable
        self.__onupdate = onupdate
        self.__primary_key = primary_key
        self.__server_default = server_default
        self.__server_onupdate = server_onupdate
        self.__quote = quote
        self.__system = system
        self.__comment = comment
        self.__insert_sentinel = insert_sentinel
        self.__omit_from_statements = _omit_from_statements
        self.__proxies = _proxies
        self.__dialect_kwargs = dialect_kwargs

    @property
    def name_pos(self) -> Any:
        return self.__name_pos

    def set_name_pos(
        self, __name_pos: Any
    ) -> 'AbstractColumn':
        self.__name_pos = __name_pos
        return self

    @property
    def type_pos(self) -> Any:
        return self.__type_pos

    def set_type_pos(
        self, __type_pos: Any
    ) -> 'AbstractColumn':
        self.__type_pos = __type_pos
        return self

    @property
    def name(self) -> Optional[str]:
        return self.__name

    def set_name(self, name: Optional[str]) -> 'AbstractColumn':
        self.__name = name
        return self

    @property
    def type(self) -> Any:
        return self.__type

    def set_type(self, type_: Any) -> 'AbstractColumn':
        self.__type = type_
        return self

    @property
    def autoincrement(self) -> Union[Literal["auto", "ignore_fk"], bool]:
        return self.__autoincrement

    def set_autoincrement(self, autoincrement: Union[Literal["auto", "ignore_fk"], bool]) -> 'AbstractColumn':
        self.__autoincrement = autoincrement
        return self

    @property
    def default(self) -> Optional[Any]:
        return self.__default

    def set_default(self, default: Optional[Any]) -> 'AbstractColumn':
        self.__default = default
        return self

    @property
    def insert_default(self) -> Optional[Any]:
        return self.__insert_default

    def set_insert_default(self, insert_default: Optional[Any]) -> 'AbstractColumn':
        self.__insert_default = insert_default
        return self

    @property
    def doc(self) -> Optional[str]:
        return self.__doc

    def set_doc(self, doc: Optional[str]) -> 'AbstractColumn':
        self.__doc = doc
        return self

    @property
    def key(self) -> Optional[str]:
        return self.__key

    def set_key(self, key: Optional[str]) -> 'AbstractColumn':
        self.__key = key
        return self

    @property
    def index(self) -> Optional[bool]:
        return self.__index

    def set_index(self, index: Optional[bool]) -> 'AbstractColumn':
        self.__index = index
        return self

    @property
    def unique(self) -> Optional[bool]:
        return self.__unique

    def set_unique(self, unique: Optional[bool]) -> 'AbstractColumn':
        self.__unique = unique
        return self

    @property
    def info(self) -> Optional[dict]:
        return self.__info

    def set_info(self, info: Optional[dict]) -> 'AbstractColumn':
        self.__info = info
        return self

    @property
    def nullable(self) -> Union[bool, SchemaConst]:
        return self.__nullable

    def set_nullable(self, nullable: Union[bool, SchemaConst]) -> 'AbstractColumn':
        self.__nullable = nullable
        return self

    @property
    def onupdate(self) -> Optional[Any]:
        return self.__onupdate

    def set_onupdate(self, onupdate: Optional[Any]) -> 'AbstractColumn':
        self.__onupdate = onupdate
        return self

    @property
    def primary_key(self) -> bool:
        return self.__primary_key

    def set_primary_key(self, primary_key: bool) -> 'AbstractColumn':
        self.__primary_key = primary_key
        return self

    @property
    def server_default(self) -> Union[FetchedValue, str, TextClause, ColumnElement, None]:
        return self.__server_default

    def set_server_default(
            self, server_default: Union[FetchedValue, str, TextClause, ColumnElement, None]
    ) -> 'AbstractColumn':
        self.__server_default = server_default
        return self

    @property
    def server_onupdate(self) -> Optional[FetchedValue]:
        return self.__server_onupdate

    def set_server_onupdate(self, server_onupdate: Optional[FetchedValue]) -> 'AbstractColumn':
        self.__server_onupdate = server_onupdate
        return self

    @property
    def quote(self) -> Optional[bool]:
        return self.__quote

    def set_quote(self, quote: Optional[bool]) -> 'AbstractColumn':
        self.__quote = quote
        return self

    @property
    def system(self) -> bool:
        return self.__system

    def set_system(self, system: bool) -> 'AbstractColumn':
        self.__system = system
        return self

    @property
    def comment(self) -> Optional[str]:
        return self.__comment

    def set_comment(self, comment: Optional[str]) -> 'AbstractColumn':
        self.__comment = comment
        return self

    @property
    def insert_sentinel(self) -> bool:
        return self.__insert_sentinel

    def set_insert_sentinel(self, insert_sentinel: bool) -> 'AbstractColumn':
        self.__insert_sentinel = insert_sentinel
        return self

    @property
    def omit_from_statements(self) -> bool:
        return self.__omit_from_statements

    def set_omit_from_statements(self, omit_from_statements: bool) -> 'AbstractColumn':
        self.__omit_from_statements = omit_from_statements
        return self

    @property
    def proxies(self) -> Optional[Any]:
        return self.__proxies

    def set_proxies(self, proxies: Optional[Any]) -> 'AbstractColumn':
        self.__proxies = proxies
        return self

    @property
    def dialect_kwargs(self) -> dict:
        return self.__dialect_kwargs

    def set_dialect_kwargs(self, dialect_kwargs: dict) -> 'AbstractColumn':
        self.__dialect_kwargs.update(dialect_kwargs)
        return self

    @property
    def col(self) -> Column:
        return Column(
            self.__name_pos,
            self.__type_pos,
            *self.__pos_args,
            name=self.__name,
            type_=self.__type,
            autoincrement=self.__autoincrement,
            default=self.__default,
            insert_default=self.__insert_default,
            doc=self.__doc,
            key=self.__key,
            index=self.__index,
            unique=self.__unique,
            info=self.__info,
            nullable=self.__nullable,
            onupdate=self.__onupdate,
            primary_key=self.__primary_key,
            server_default=self.__server_default,
            server_onupdate=self.__server_onupdate,
            quote=self.__quote,
            system=self.__system,
            comment=self.__comment,
            insert_sentinel=self.__insert_sentinel,
            _omit_from_statements=self.__omit_from_statements,
            _proxies=self.__proxies,
            **self.__dialect_kwargs,
        )
