from typing import List

from sqlalchemy import null
from sqlalchemy.orm import relationship, Mapped

from App.Core.DB.Model import Model
import enum

from App.Models.Client.ScanType import ScanType
from App.Core.DB.Columns import Auto, ForeignKey, Timestamp, Varchar, Enum


class Format(enum.Enum):
    TIFF = 1
    JPEG = 2
    PNG = 3


class Scan(Model):
    __tablename__ = 'scans'

    id = Auto().col
    type_id = ForeignKey(ScanType.id, ondelete="SET NULL", server_default=null()).col
    format = Enum(Format).col
    title = Varchar(nullable=False).col
    path = Varchar(1023, nullable=False).col
    created_at = Timestamp().col
    updated_at = Timestamp().col

    type: Mapped['ScanType'] = relationship(back_populates='scans')
    # noinspection PyUnresolvedReferences
    tags: Mapped[List['Tag']] = relationship(secondary='scan_tag', back_populates='scans')
    # noinspection PyUnresolvedReferences
    # scan_tags: Mapped[List['ScanTag']] = relationship(back_populates='tag')
    # noinspection PyUnresolvedReferences
    documents: Mapped[List['Document']] = relationship(back_populates='scan')
