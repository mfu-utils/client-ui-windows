from sqlalchemy import VARCHAR

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class Varchar(AbstractColumn):
    def __init__(self, size: int = 255, *args, **kw):
        super().__init__(VARCHAR(size), *args, **kw)
