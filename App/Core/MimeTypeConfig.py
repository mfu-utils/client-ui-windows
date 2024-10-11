import platform
from typing import Union, Optional, List

import magic

from App.Core.Utils import MimeType


class MimeTypeConfig:
    def __init__(self):
        self.__mime_types = {}

    def get_mime_types(self, key: str) -> List[str]:
        if not (data := self.__mime_types.get(key)):
            self.__mime_types[key] = getattr(MimeType, key)()

        return data or self.__mime_types[key]

    @staticmethod
    def get_mime(file: Union[str, bytes]) -> Optional[str]:
        _type = None

        if isinstance(file, bytes):
            _type = magic.from_buffer(file, mime=True)

        if platform.system() == 'Windows':
            with open(file, 'rb') as f:
                _type = magic.from_buffer(f.read(2048), mime=True)
        elif isinstance(file, str):
            _type = magic.from_file(file, mime=True)

        return _type

    @staticmethod
    def get_mime_enum(file: Union[str, bytes]) -> MimeType:
        if not (mime_type := MimeTypeConfig.get_mime(file)) in MimeType.values():
            return MimeType.UNDEFINED

        return MimeType(mime_type)

    def has_type(self, file: Union[str, bytes], types: str) -> bool:
        _type = MimeTypeConfig.get_mime(file)

        if _type is None:
            return False

        return _type in self.get_mime_types(types)
