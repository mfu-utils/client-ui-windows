from typing import List

from sqlalchemy.orm import Mapped, relationship

from App.Core.DB import Model
from App.Core.DB.Columns import Auto, Varchar


class Tag(Model):
    __tablename__ = 'tags'

    id = Auto().col
    name = Varchar(31, nullable=False, unique=True).col

    # noinspection PyUnresolvedReferences
    scans: Mapped[List['Scan']] = relationship(secondary='scan_tag', back_populates='tags')
