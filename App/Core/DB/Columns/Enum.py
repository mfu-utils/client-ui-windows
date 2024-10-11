import enum
from typing import Type

from sqlalchemy import Enum as SQLAlchemyEnum

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class Enum(AbstractColumn):
    def __init__(self, enum_: Type[enum.Enum], *args, **kwargs):
        super().__init__(SQLAlchemyEnum(enum_), *args, **kwargs)
