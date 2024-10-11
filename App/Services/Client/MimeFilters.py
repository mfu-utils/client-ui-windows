from typing import Union, List

from App.helpers import mime
from PySide6.QtCore import QUrl


class MimeService:
    FILE_SCHEME = 'file'

    @staticmethod
    def has_q_url(file: QUrl, scheme: str, types: str) -> bool:
        if file.scheme() != scheme:
            return False

        return mime().has_type(file.toLocalFile(), types)

    @staticmethod
    def filter_q_urls(files: List[QUrl], scheme: str, types: str) -> List[QUrl]:
        filtered = []

        for file_ in files:
            if MimeService.has_q_url(file_, scheme, types):
                filtered.append(file_)

        return filtered

    @staticmethod
    def check_printing_type(file: Union[QUrl]) -> bool:
        return MimeService.has_q_url(file, MimeService.FILE_SCHEME, "available_printing_types")

    @staticmethod
    def filter_printing_types(files: List[QUrl]) -> List[QUrl]:
        return MimeService.filter_q_urls(files, MimeService.FILE_SCHEME, "available_printing_types")
