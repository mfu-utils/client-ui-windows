from sqlalchemy import SMALLINT

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class SmallInteger(AbstractColumn):
    def __init__(self, nullable: bool = True, *args, **kwargs):
        kwargs.update({'nullable': nullable})

        AbstractColumn.__init__(self, SMALLINT(), *args, **kwargs)