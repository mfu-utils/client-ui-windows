from typing import Union

from .AbstractResponse import AbstractResponse
from App.Core.Network.Protocol.RCLProtocol import RCLProtocol


class ResponseSuccess(AbstractResponse):
    def __init__(self, data: Union[str, bytes, list, dict]) -> None:
        super().__init__(data)

    @staticmethod
    def type() -> int:
        return RCLProtocol.RCL_MESSAGE_TYPE_RETURN
