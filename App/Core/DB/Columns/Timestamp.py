from sqlalchemy import TIMESTAMP

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class Timestamp(AbstractColumn):
    def __init__(self, nullable: bool = True, *args, **kwargs):
        kwargs.update({'nullable': nullable})

        super().__init__(TIMESTAMP(), *args, **kwargs)
