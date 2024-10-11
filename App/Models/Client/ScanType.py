from sqlalchemy.orm import Mapped, relationship

from App.Core.DB import Model
from App.Core.DB.Columns import Auto, Char


class ScanType(Model):
    __tablename__ = 'scan_types'

    id = Auto().col
    name = Char(32, nullable=False, unique=True).col

    # noinspection PyUnresolvedReferences
    scans: Mapped['Scan'] = relationship(back_populates='type')
