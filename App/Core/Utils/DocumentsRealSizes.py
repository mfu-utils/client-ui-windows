from typing import Tuple, Dict

from App.Core.Utils import DocumentMediaType


class DocumentsRealSizes:
    SIZES: Dict[DocumentMediaType, Tuple[int, int]] = {
        DocumentMediaType.Letter: (216, 279),
        DocumentMediaType.Legal: (216, 356),
        DocumentMediaType.COM10: (241, 105),
        DocumentMediaType.A4: (210, 297),
        DocumentMediaType.DL: (220, 110),
    }

    @staticmethod
    def size(size: DocumentMediaType) -> Tuple[int, int]:
        if size := DocumentsRealSizes.SIZES.get(size):
            return size

        raise KeyError(f'Unknown document size "{size}"')

    @staticmethod
    def letter() -> Tuple[int, int]:
        return DocumentsRealSizes.SIZES[DocumentMediaType.Letter]

    @staticmethod
    def legal() -> Tuple[int, int]:
        return DocumentsRealSizes.SIZES[DocumentMediaType.Legal]

    @staticmethod
    def com10() -> Tuple[int, int]:
        return DocumentsRealSizes.SIZES[DocumentMediaType.COM10]

    @staticmethod
    def a4() -> Tuple[int, int]:
        return DocumentsRealSizes.SIZES[DocumentMediaType.A4]

    @staticmethod
    def dl() -> Tuple[int, int]:
        return DocumentsRealSizes.SIZES[DocumentMediaType.DL]
