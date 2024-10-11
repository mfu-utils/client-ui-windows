from sqlalchemy import CHAR

from App.Core.DB.Columns.AbstractColumn import AbstractColumn


class Char(AbstractColumn):
    def __init__(self, size: int = 255, *args, **kwargs):
        super().__init__(CHAR(size), *args, **kwargs)
