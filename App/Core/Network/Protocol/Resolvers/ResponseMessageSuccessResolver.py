from typing import Union
import json
from .AbstractMessageResolver import AbstractMessageResolver


class ResponseMessageSuccessResolver(AbstractMessageResolver):
    TYPE_CODE_STR = 0x01
    TYPE_CODE_JSON = 0x02
    TYPE_CODE_BYTES = 0x03
    TYPE_CODE_BOOL = 0x04

    @staticmethod
    def __get_type_code(data: Union[str, list, dict, bytes, bool, None]):
        _type = type(data)

        if _type is str:
            return ResponseMessageSuccessResolver.TYPE_CODE_STR

        if _type is list or _type is dict:
            return ResponseMessageSuccessResolver.TYPE_CODE_JSON

        if _type is bytes:
            return ResponseMessageSuccessResolver.TYPE_CODE_BYTES

        if _type is bool:
            return ResponseMessageSuccessResolver.TYPE_CODE_BOOL

        raise Exception(f"Unknown type '{_type}' for response")

    def __encode_data(self, data: Union[str, list, dict, bytes, bool], _type: int) -> bytes:
        if _type == self.TYPE_CODE_STR:
            return data.encode("utf-8")

        if _type == self.TYPE_CODE_JSON:
            return json.dumps(data).encode("utf-8")

        if _type is self.TYPE_CODE_BYTES:
            return data

        if _type is self.TYPE_CODE_BOOL:
            return b"\x01" if data else b"\x00"

    def __decode_data(self, data: bytes, _type: int) -> Union[str, list, dict, bytes, bool]:
        if _type == self.TYPE_CODE_STR:
            return data.decode("utf-8")

        if _type == self.TYPE_CODE_JSON:
            return json.loads(data.decode("utf-8"))

        if _type is self.TYPE_CODE_BYTES:
            return data

        if _type is self.TYPE_CODE_BOOL:
            return False if b"\x00" == data else True

    def parse(self, data: bytes) -> Union[dict, list, str, bytes, None]:
        if data == b'':
            return None

        return self.__decode_data(data[1:], data[0])

    def create(self, data: Union[dict, list, str, bytes, None]) -> bytes:
        if not data:
            return b''

        _type = self.__get_type_code(data)

        return _type.to_bytes(1, 'big') + self.__encode_data(data, _type)
