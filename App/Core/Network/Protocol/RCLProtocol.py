from datetime import datetime, timezone
from zlib import crc32
from typing import Union, Optional
from config import RCL_PROTOCOL_VERSION


class RCLProtocol:
    """
    "Remote command line" protocol. Low Level part.

    Message struct:

      [HEADERS][DATA][CRC32]

    Headers struct:

      I - integer
      B - bytes

      +-----------+-----+------+------------------+----------------------------------+
      | Position  | Len | Type | Name             | Description                      |
      +-----------+-----+------+------------------+----------------------------------+
      | [0-3]     | 3   | B    | start_bytes      | Start bytes protocol 'rcl'.      |
      +-----------+-----+------+------------------+----------------------------------+
      | [3]       | 1   | B    | protocol_version | Protocol version number.         |
      +-----------+-----+------+------------------+----------------------------------+
      | [4-7]     | 4   | B    | request_id       | Request ID.                      |
      +-----------+-----+------+------------------+----------------------------------+
      | [8]       | 1   | I    | message_type     | Message type.                    |
      +-----------+-----+------+------------------+----------------------------------+
      | [9-13]    | 4   | I    | data_length      | Data len.                        |
      +-----------+-----+------+------------------+----------------------------------+
    """

    # PROTOCOL START BYTES 'rcl'
    RCL_PROTOCOL_START_BYTES = 0x72636c

    # PROTOCOL HEADER PARAMETERS
    RCL_HEADER_START_BYTES = 'start_bytes'
    RCL_HEADER_PROTOCOL_VERSION = 'protocol_version'
    RCL_HEADER_REQUEST_ID = 'request_id'
    RCL_HEADER_MESSAGE_TYPE = 'message_type'
    RCL_HEADER_DATA_LENGTH = 'data_length'

    RCL_HEADER_LEN_START_BYTES = 3
    RCL_HEADER_LEN_PROTOCOL_VERSION = 1
    RCL_HEADER_LEN_REQUEST_ID = 4
    RCL_HEADER_LEN_MESSAGE_TYPE = 1
    RCL_HEADER_LEN_DATA_LENGTH = 4

    RCL_HEADER_INDEX_START_BYTES = 0
    RCL_HEADER_INDEX_PROTOCOL_VERSION = RCL_HEADER_INDEX_START_BYTES + RCL_HEADER_LEN_START_BYTES
    RCL_HEADER_INDEX_REQUEST_ID = RCL_HEADER_INDEX_PROTOCOL_VERSION + RCL_HEADER_LEN_PROTOCOL_VERSION
    RCL_HEADER_INDEX_MESSAGE_TYPE = RCL_HEADER_INDEX_REQUEST_ID + RCL_HEADER_LEN_REQUEST_ID
    RCL_HEADER_INDEX_DATA_LENGTH = RCL_HEADER_INDEX_MESSAGE_TYPE + RCL_HEADER_LEN_MESSAGE_TYPE

    RCL_HEADERS_STRUCT_DICT = {
        0: (RCL_HEADER_START_BYTES, RCL_HEADER_INDEX_START_BYTES, RCL_HEADER_LEN_START_BYTES, bytes, True),
        1: (RCL_HEADER_PROTOCOL_VERSION, RCL_HEADER_INDEX_PROTOCOL_VERSION, RCL_HEADER_LEN_PROTOCOL_VERSION, int, True),
        2: (RCL_HEADER_REQUEST_ID, RCL_HEADER_INDEX_REQUEST_ID, RCL_HEADER_LEN_REQUEST_ID, int, True),
        3: (RCL_HEADER_MESSAGE_TYPE, RCL_HEADER_INDEX_MESSAGE_TYPE, RCL_HEADER_LEN_MESSAGE_TYPE, int, True),
        4: (RCL_HEADER_DATA_LENGTH, RCL_HEADER_INDEX_DATA_LENGTH, RCL_HEADER_LEN_DATA_LENGTH, int, True),
    }
    """ Header parameters metadata (PARAMETER NAME, POS, LEN, TYPE, NOT NULL) """

    RCL_HEADERS_LENGTH = sum(map(lambda x: x[2], RCL_HEADERS_STRUCT_DICT.values()))
    RCL_HEADERS_STRUCT_LIST = list(map(lambda x: x[0], RCL_HEADERS_STRUCT_DICT.values()))

    RCL_HEADERS_STRUCT_LEN = len(RCL_HEADERS_STRUCT_LIST)

    # Null value
    RCL_NULL = 0x00

    # Bool values
    RCL_TRUE = 0x01
    RCL_FALSE = 0x02

    # Message types
    RCL_MESSAGE_GROUP_REQUEST = 0x00
    RCL_MESSAGE_GROUP_RESPONSE_OK = 0x40
    RCL_MESSAGE_GROUP_CLIENT_ERRORS = 0x80
    RCL_MESSAGE_GROUP_SERVER_ERRORS = 0xC0
    # Request (0x00 <= x < 0x40)
    RCL_MESSAGE_TYPE_CALL = RCL_MESSAGE_GROUP_REQUEST | 0
    # Response ok types (0x40 <= x < 0x80)
    RCL_MESSAGE_TYPE_RETURN = RCL_MESSAGE_GROUP_RESPONSE_OK | 0
    # Client errors (0x80 <= x < 0xC0)
    RCL_MESSAGE_TYPE_NOT_FOUND = RCL_MESSAGE_GROUP_CLIENT_ERRORS | 0
    RCL_MESSAGE_TYPE_NOT_VALID_SIGNATURE = RCL_MESSAGE_GROUP_CLIENT_ERRORS | 1
    RCL_MESSAGE_TYPE_NO_REQUIRED_PARAMETERS = RCL_MESSAGE_GROUP_CLIENT_ERRORS | 2
    # Server errors (0xC0 <= x <= 0xFF)
    RCL_MESSAGE_TYPE_INTERNAL_ERROR = RCL_MESSAGE_GROUP_SERVER_ERRORS | 0

    RCL_MESSAGES_NAMES = {
        RCL_MESSAGE_TYPE_CALL: "call",
        RCL_MESSAGE_TYPE_RETURN: "return",
        RCL_MESSAGE_TYPE_NOT_FOUND: "method_not_found",
        RCL_MESSAGE_TYPE_NOT_VALID_SIGNATURE: "not_valid_signature",
        RCL_MESSAGE_TYPE_NO_REQUIRED_PARAMETERS: "no_required_parameters",
        RCL_MESSAGE_TYPE_INTERNAL_ERROR: "internal_error",
    }

    RCL_MESSAGES_TYPES = dict(map(lambda x: (x[1], x[0]), RCL_MESSAGES_NAMES.items()))

    @staticmethod
    def get_message_type_name(_type: int) -> Optional[str]:
        return RCLProtocol.RCL_MESSAGES_NAMES.get(_type)

    @staticmethod
    def get_message_type_by_name(name: str) -> Optional[int]:
        return RCLProtocol.RCL_MESSAGES_TYPES.get(name)

    @staticmethod
    def __current_time() -> int:
        return int(str(datetime.now(timezone.utc).timestamp())[:10])

    @staticmethod
    def __raise_error(error_text: str):
        raise Exception(f"RCL Error: {error_text}")

    @staticmethod
    def __encode_value(value: Union[int, bytes, bool, None], _len: int):
        _type = type(value)

        if _type is int:
            return list(value.to_bytes(_len, byteorder="big"))

        if _type is None:
            return [RCLProtocol.RCL_NULL]

        if _type is bool:
            return [RCLProtocol.RCL_TRUE if value else RCLProtocol.RCL_FALSE]

        if _type is bytes:
            return list(value)

        RCLProtocol.__raise_error(f"Cannot convert value: {str(value)} to bytes")

    @staticmethod
    def __decode_value(value: bytearray, _type: type) -> Union[int, bytes, bool, None]:
        if _type is int:
            return int.from_bytes(value, byteorder="big")

        if _type is bool:
            return value[0] == RCLProtocol.RCL_TRUE

        if _type is bytes:
            return bytes(value)

        if _type is None and value == RCLProtocol.RCL_NULL:
            return None

        type_name = _type.__class__
        RCLProtocol.__raise_error(f"Cannot decode value: {str(value)} of type {type_name}")

    @staticmethod
    def __checksum(data: bytes) -> bytes:
        return crc32(data).to_bytes(4, "big")

    @staticmethod
    def __validate_parameter(
        name: str,
        value: Union[int, bytes, bool, None],
        _len: int,
        not_null: bool,
        _type: bool
    ):
        if name not in RCLProtocol.RCL_HEADERS_STRUCT_LIST:
            RCLProtocol.__raise_error(f"Parameter '{name}' not define in protocol")

        p_type = type(value)

        if p_type is None:
            if not_null:
                RCLProtocol.__raise_error(f"Parameter '{name}' not define in protocol")
            elif p_type not in ([_type, int] if _type == bytes else [_type]):
                need_type_name = _type.__name__
                p_type_name = p_type.__name__
                RCLProtocol.__raise_error(f"Parameter '{name}' can not be {p_type_name}. Must be {need_type_name}")

        if p_type is int:
            return

        p_len = 1 if (p_type is None or p_type is bool) else len(value)

        if p_len != _len:
            RCLProtocol.__raise_error(f"Len of parameter '{name}' is {str(p_len)}. Must be {str(_len)}")

    @staticmethod
    def __decode_header(header: bytes) -> dict:
        buffer = bytearray(header)

        data = {}

        for i in range(RCLProtocol.RCL_HEADERS_STRUCT_LEN):
            _name, _pos, _len, _type, _not_null = RCLProtocol.RCL_HEADERS_STRUCT_DICT[i]

            val_buf = buffer[_pos:_pos + _len]

            val = RCLProtocol.__decode_value(val_buf, _type)

            RCLProtocol.__validate_parameter(_name, val, _len, _not_null, _type)

            data.update({_name: val})

        return data

    @staticmethod
    def __encode_header(parameters: dict) -> bytes:
        header = bytearray(RCLProtocol.RCL_HEADERS_LENGTH)

        for i in range(RCLProtocol.RCL_HEADERS_STRUCT_LEN):
            _name, _pos, _len, _type, _not_null = RCLProtocol.RCL_HEADERS_STRUCT_DICT[i]

            val = parameters.get(_name)

            RCLProtocol.__validate_parameter(_name, val, _len, _not_null, _type)

            val = RCLProtocol.__encode_value(val, _len)

            for j in range(len(val)):
                header[_pos + j] = int(val[j])

        return bytes(header)

    @staticmethod
    def create_message(message_type: int, data: bytes, _len: int) -> bytes:
        data = RCLProtocol.__encode_header({
            RCLProtocol.RCL_HEADER_START_BYTES: RCLProtocol.RCL_PROTOCOL_START_BYTES,
            RCLProtocol.RCL_HEADER_PROTOCOL_VERSION: RCL_PROTOCOL_VERSION,
            RCLProtocol.RCL_HEADER_REQUEST_ID: RCLProtocol.__current_time(),
            RCLProtocol.RCL_HEADER_MESSAGE_TYPE: message_type,
            RCLProtocol.RCL_HEADER_DATA_LENGTH: _len,
        }) + data

        return data + RCLProtocol.__checksum(data)

    @staticmethod
    def check_rcl_protocol(data: bytes) -> bool:
        if data == RCLProtocol.RCL_PROTOCOL_START_BYTES.to_bytes(3, 'big'):
            return True

        return False

    @staticmethod
    def get_headers(data: bytes) -> dict:
        return RCLProtocol.__decode_header(data[:RCLProtocol.RCL_HEADERS_LENGTH])

    @staticmethod
    def check_protocol_version(version: int) -> bool:
        return version > RCL_PROTOCOL_VERSION

    @staticmethod
    def get_message(data: bytes, _len: int) -> bytes:
        return data[RCLProtocol.RCL_HEADERS_LENGTH:RCLProtocol.RCL_HEADERS_LENGTH + _len]

    @staticmethod
    def check_crc(data: bytes, _len: int) -> bool:
        data = data[:RCLProtocol.RCL_HEADERS_LENGTH + _len + 4]

        return data[-4:] == RCLProtocol.__checksum(data[:-4])

    @staticmethod
    def check_message_type(_type: int) -> bool:
        return bool(RCLProtocol.RCL_MESSAGES_NAMES.get(_type))
