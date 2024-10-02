from typing import List

from App.Models.Client.Document import Type as DocumentType, Document
from App.helpers import now


class DocumentService:
    @staticmethod
    def store(scan_id: int, _type: DocumentType, path: str) -> Document:
        _now = now()

        return Document.create(scan_id=scan_id, type=_type, path=path, created_at=_now, updated_at=_now)

    @staticmethod
    def has_doc_types(scan_id: int):
        docs: List[Document] = Document.query(Document.id, Document.type).filter(Document.scan_id == scan_id).all()

        return list(map(lambda x: DocumentType(x.type), docs))
