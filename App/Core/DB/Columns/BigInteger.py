from sqlalchemy import BIGINT

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class BigInteger(AbstractColumn):
    def __init__(self, nullable: bool = True, *args, **kwargs):
        kwargs.update({'nullable': nullable})

        AbstractColumn.__init__(self, BIGINT(), *args, **kwargs)