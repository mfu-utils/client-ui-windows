from typing import Optional

from App.Core.Abstract import AbstractDTO
from App.Core.Utils import DocumentMediaType, DocumentOrder, MimeType
from App.Core.Utils.PaperTray import PaperTray
from App.Core.Utils.Ui.PrintingPagePolicy import PrintingPagePolicy


class PrintingDocumentDTO(AbstractDTO):
    device: str = ""
    copies: int = 1
    paper_tray: Optional[PaperTray] = None
    pages_policy: PrintingPagePolicy = PrintingPagePolicy.All
    pages: str = ""
    paper_size: DocumentMediaType = DocumentMediaType.A4
    order: DocumentOrder = DocumentOrder.Normal
    mirror: bool = False
    landscape: bool = False
    transparency: bool = False
    file: bytes = b""
    mime_type: Optional[MimeType] = None
    send_converted: bool = False

    def as_dict(self) -> dict:
        res = super(PrintingDocumentDTO, self).as_dict().copy()

        res['file'] = b"..."

        return res
