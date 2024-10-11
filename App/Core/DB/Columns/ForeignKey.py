from typing import Union, Optional

from sqlalchemy import INTEGER, ForeignKey as Fk, Null, Column

from App.Core.DB import Model
from App.Core.DB.Columns.AbstractColumn import AbstractColumn
from App.Core.DB.Columns.Auto import TYPE


class ForeignKey(AbstractColumn):
    def __init__(
        self,
        ref_column: Union[str, Model, Column],
        type_: TYPE = INTEGER,
        ondelete: Optional[str] = None,
        onupdate: Optional[str] = None,
        server_default: Union[str, Null, None] = None,
        nullable: bool = True,
        *args,
        **kw
    ):
        kw.update({'primary_key': True, 'nullable': nullable, 'server_default': server_default})

        super().__init__(type_, Fk(ref_column, ondelete=ondelete, onupdate=onupdate), *args, **kw)
