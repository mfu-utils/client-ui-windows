from enum import Enum
from typing import List

MIME_MS_WORD = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_PDF = "application/pdf"

# MIME_TEXT = "text/plain"

MIME_TIFF = "image/tiff"
MIME_PNG = "image/png"
MIME_JPEG = "image/jpeg"

_UNDEFINED = 'undefined'

MIME_NAMES = {
    MIME_MS_WORD: 'Microsoft word',
    MIME_PDF: 'PDF',
    MIME_TIFF: 'TIFF',
    MIME_PNG: 'PNG',
    MIME_JPEG: 'JPEG',
}

MIME_EXTENSIONS = {
    MIME_MS_WORD: 'docx',
    MIME_PDF: 'pdf',
    MIME_TIFF: 'tiff',
    MIME_PNG: 'png',
    MIME_JPEG: 'jpeg',
}

AVAILABLE_PRINTING_TYPES = [
    MIME_MS_WORD,
    MIME_PDF,
    MIME_TIFF,
    MIME_PNG,
    MIME_JPEG,
]

SERVER_SIDE_CONVERT = [
    MIME_MS_WORD
]


class MimeType(Enum):
    # Type not
    UNDEFINED = _UNDEFINED

    # Documents
    MSWORD = MIME_MS_WORD
    PDF = MIME_PDF

    # Text
    # TEXT = MIME_TEXT

    # Images
    TIFF = MIME_TIFF
    PNG = MIME_PNG
    JPEG = MIME_JPEG

    @staticmethod
    def values() -> List[str]:
        return list(map(lambda x: x.value, MimeType))

    @staticmethod
    def doc_group() -> List['MimeType']:
        return [MimeType.MSWORD, MimeType.PDF]

    @staticmethod
    def image_group() -> List['MimeType']:
        return [MimeType.TIFF, MimeType.PNG, MimeType.JPEG]

    @staticmethod
    def alias(_type: 'MimeType') -> str:
        return MIME_NAMES[_type.value]

    @staticmethod
    def available_printing_types() -> List[str]:
        return AVAILABLE_PRINTING_TYPES

    @staticmethod
    def is_server_side_convert_type(_type: str) -> bool:
        return _type in SERVER_SIDE_CONVERT

    @staticmethod
    def mime_extension(_type: 'MimeType') -> str:
        return MIME_EXTENSIONS[_type.value]
