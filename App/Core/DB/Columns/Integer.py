from sqlalchemy import INTEGER

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class Integer(AbstractColumn):
    def __init__(self, nullable: bool = True, *args, **kwargs):
        kwargs.update({'nullable': nullable})

        AbstractColumn.__init__(self, INTEGER(), *args, **kwargs)