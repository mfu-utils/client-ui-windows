from typing import Union

from App.Core.Network.Protocol.Resolvers.AbstractMessageResolver import AbstractMessageResolver


class InternalErrorMessageResolver(AbstractMessageResolver):
    def create(self, data: [str, None]) -> bytes:
        if data is None:
            return b""

        return data.encode("utf-8")

    def parse(self, data: bytes) -> Union[str, None]:
        if data == b"":
            return None

        return data.decode("utf-8")
