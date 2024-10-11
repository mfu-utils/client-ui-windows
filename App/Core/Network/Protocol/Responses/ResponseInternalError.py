from .AbstractResponse import AbstractResponse
from App.Core.Network.Protocol.RCLProtocol import RCLProtocol


class ResponseInternalError(AbstractResponse):
    def __init__(self, data: [str, None] = None) -> None:
        super().__init__(data)

    @staticmethod
    def type() -> int:
        return RCLProtocol.RCL_MESSAGE_TYPE_INTERNAL_ERROR
