from sqlalchemy import UniqueConstraint

from App.Core.DB import Model
from App.Core.DB.Columns import ForeignKey
from App.Models.Client.Scan import Scan
from App.Models.Client.Tag import Tag


class ScanTag(Model):
    __tablename__ = 'scan_tag'

    __table_args__ = tuple(
        UniqueConstraint("scan_id", "tag_id")
    )

    scan_id = ForeignKey(Scan.id, nullable=False, ondelete='CASCADE').col
    tag_id = ForeignKey(Tag.id, nullable=False, ondelete='CASCADE').col

    # scan: Mapped[Tag] = relationship(back_populates='scan_tags')
    # tag: Mapped[Tag] = relationship(back_populates='scan_tags')

