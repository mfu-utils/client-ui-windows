import enum
from typing import List

from sqlalchemy.orm import Mapped, relationship

from App.Core.DB import Model
from App.Models.Client.Scan import Scan
from App.Core.DB.Columns import Auto, ForeignKey, Enum, Varchar, Timestamp


class Type(enum.Enum):
    TXT = 1
    PDF = 2
    MS_WORD = 3
    HTML = 4
    RTF = 5
    ODT = 6
    FB2 = 7
    EPUB = 8
    CSV = 9


class Document(Model):
    __tablename__ = "documents"

    id = Auto().col

    scan_id = ForeignKey(Scan.id, ondelete="CASCADE", nullable=False).col

    type = Enum(Type).col
    path = Varchar(1023, nullable=False).col
    created_at = Timestamp().col
    updated_at = Timestamp().col

    scan: Mapped[List[Scan]] = relationship(back_populates='documents')
