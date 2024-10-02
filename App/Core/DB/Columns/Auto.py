from typing import Union

from sqlalchemy import SMALLINT, INTEGER, BIGINT, UUID

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


TYPE = Union[INTEGER, BIGINT, SMALLINT, UUID]


class Auto(AbstractColumn):
    def __init__(self, type_: TYPE = INTEGER, *args, **kw):
        kw.update({'unique': True, 'primary_key': True})

        super().__init__(type_, *args, **kw)
