from typing import Union, Type, Dict, Any

from sqlalchemy.orm import DeclarativeBase

from App.Application import Application
from sqlalchemy import Column, Exists
from sqlalchemy.orm import Query

from App.Core.DB import Connection


class Base(DeclarativeBase):
    pass


class Model(Base):
    __abstract__ = True
    __primary_key__ = "id"

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
        self.__connection: Connection = Application().get('db')

    @staticmethod
    def db() -> Connection:
        return Application().get('db')

    @classmethod
    def query(cls, *entities) -> Query:
        return cls.db().query(cls.__mro__[0], *entities)

    @classmethod
    def select(cls, *columns: Union[str, Column, Type['Model']]) -> Query:
        return cls.db().select(cls.__mro__[0], columns)

    @classmethod
    def count(cls, column: Union[str, Column] = '*') -> int:
        return cls.db().count(cls.__mro__[0], column)

    def save(self):
        self.db().save([self])

    def update(self, data: dict):
        return self.db().update(self, data)

    def delete(self) -> bool:
        return self.db().delete(self)

    @classmethod
    def delete_by(cls, by: Union[str, Dict[str, Any]], value: Any = None) -> bool:
        return cls.db().delete_by(cls.__mro__[0], by, value)

    @classmethod
    def exists(cls, exists_: Exists) -> bool:
        return cls.db().exists(exists_)

    @classmethod
    def create(cls, **kw) -> 'Model':
        return cls.db().create(cls.__mro__[0], **kw)

    @classmethod
    def find_or_create(cls, find: Dict[str, Any], **kwargs) -> 'Model':
        q = cls.query(cls.__mro__[0])

        for k, v in find.items():
            # noinspection PyTypeChecker
            q = q.where(getattr(cls.__mro__[0], k) == v)

        if obj := q.one_or_none():
            return obj[0]

        kwargs.update(find)

        return cls.create(**kwargs)
