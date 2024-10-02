from sqlalchemy import BOOLEAN

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class Bool(AbstractColumn):
    def __init__(self, nullable: bool = True, *args, **kwargs):
        kwargs.update({'nullable': nullable})

        AbstractColumn.__init__(self, BOOLEAN(), *args, **kwargs)