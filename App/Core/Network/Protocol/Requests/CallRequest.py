from .AbstractRequest import AbstractRequest
from App.Core.Network.Protocol.RCLProtocol import RCLProtocol

from typing import Optional, Union


class CallRequest(AbstractRequest):
    PRIMITIVE_TYPES = [str, int, float, bool]

    def __init__(self, command: str, subcommands: Optional[list] = None, parameters: Optional[dict] = None):
        super().__init__({"command": command, "subcommands": subcommands, "parameters": parameters})

    def command(self) -> str:
        return self._data["command"]

    def add_subcommand(self, subcommand: str):
        self._data['subcommands'].append(subcommand)

    def set_parameter(self, name: str, value: Union[str, int, float, bool]):
        self._data['parameters'][name] = value

    def subcommands(self) -> list:
        return self._data['subcommands']

    def subcommand(self, name: str) -> bool:
        return name in self._data['subcommands']

    def parameters(self) -> dict:
        return self._data['parameters']

    def parameter(self, name: str, default: Union[str, int, float, bool, None]) -> Union[str, int, float, bool, None]:
        if value := self._data['parameters'].get(name):
            return value

        return default

    @staticmethod
    def type() -> int:
        return RCLProtocol.RCL_MESSAGE_TYPE_CALL
