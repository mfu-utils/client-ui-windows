from typing import Optional, Tuple, Union

from App.Core.Logger import Log
from App.Core import Config

from .RCLProtocol import RCLProtocol
from .ProtoFileResolver import ProtoFileResolver
from .ProtoBuilder import ProtoBuilder

from .Resolvers import InternalErrorMessageResolver, ResponseMessageSuccessResolver, CallMessageResolver

from .Requests import AbstractRequest, CallRequest

from .Responses import AbstractResponse, ResponseSuccess, ResponseInternalError


class RCL:
    RESOLVERS = {
        RCLProtocol.RCL_MESSAGE_TYPE_CALL: CallMessageResolver(),
        RCLProtocol.RCL_MESSAGE_TYPE_RETURN: ResponseMessageSuccessResolver(),
        RCLProtocol.RCL_MESSAGE_TYPE_INTERNAL_ERROR: InternalErrorMessageResolver(),
    }

    REQUESTS = {
        RCLProtocol.RCL_MESSAGE_TYPE_CALL: CallRequest,
    }

    RESPONSES = {
        RCLProtocol.RCL_MESSAGE_TYPE_RETURN: ResponseSuccess,
        RCLProtocol.RCL_MESSAGE_TYPE_INTERNAL_ERROR: ResponseInternalError,
    }

    def __init__(self, logger: Log, config: Config):
        self.__logger = logger
        self.__proto_file_resolver = ProtoFileResolver(config)
        self.__proto_file_builder = ProtoBuilder(*self.__proto_file_resolver.parse())

        self.__max_data_len = config.get('rcl.max_packet_size') - RCLProtocol.RCL_HEADERS_LENGTH - 4

    def __create(self, data: bytes, _type: int, _len: int) -> Optional[bytes]:
        if not RCLProtocol.check_message_type(_type):
            self.__logger.error(f"Message type '{_type}' not found.", {"object": self})
            return None

        return RCLProtocol.create_message(_type, data, _len)

    def __parse(self, data: bytes) -> Optional[Tuple[dict, bytes]]:
        obj = {"object": self}

        if not RCLProtocol.check_rcl_protocol(data[:3]):
            self.__logger.debug(f"Bytearray is not protocol struct", obj)
            return None

        headers = RCLProtocol.get_headers(data)

        if RCLProtocol.check_protocol_version(version := headers[RCLProtocol.RCL_HEADER_PROTOCOL_VERSION]):
            self.__logger.error(f"Protocol version {version} required")
            return None

        if not RCLProtocol.check_crc(data, headers[RCLProtocol.RCL_HEADER_DATA_LENGTH]):
            self.__logger.error(f"Crc check failed")
            return None

        return headers, RCLProtocol.get_message(data, headers[RCLProtocol.RCL_HEADER_DATA_LENGTH])

    def create_request(self, request: AbstractRequest) -> bytes:
        resolver = RCL.RESOLVERS[request.type()]

        if request.type() == RCLProtocol.RCL_MESSAGE_TYPE_CALL:
            data = self.__proto_file_builder.prepare_command(**request.data())
        else:
            data = request.data()

        data = resolver.create(data)

        return self.__create(data, request.type(), len(data))

    def parse_request(self, data: bytes) -> AbstractRequest:
        headers, data = self.__parse(data)

        _type = headers[RCLProtocol.RCL_HEADER_MESSAGE_TYPE]

        if _type == RCLProtocol.RCL_MESSAGE_TYPE_CALL:
            return self.REQUESTS[_type](**self.__proto_file_builder.from_codes(**RCL.RESOLVERS[_type].parse(data)))

        return self.REQUESTS[_type](RCL.RESOLVERS[_type].parse(data))

    def create_response(self, response: AbstractResponse) -> bytes:
        resolver = RCL.RESOLVERS[response.type()]

        data = resolver.create(response.data())

        return self.__create(data, response.type(), len(data))

    def parse_response(self, data: bytes) -> Optional[AbstractResponse]:
        if not (parameters := self.__parse(data)):
            return None

        headers, data = parameters

        _type = headers[RCLProtocol.RCL_HEADER_MESSAGE_TYPE]

        return self.RESPONSES[_type](RCL.RESOLVERS[_type].parse(data))

    def call_request(self, command: str, subcommand: Optional[list] = None, parameters: Optional[dict] = None) -> bytes:
        return self.create_request(CallRequest(command, subcommand, parameters))

    def response_success(self, data: Union[str, list, dict, bytes, None] = None) -> bytes:
        return self.create_response(ResponseSuccess(data))
