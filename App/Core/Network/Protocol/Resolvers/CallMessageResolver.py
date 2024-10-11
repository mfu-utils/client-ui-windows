from .AbstractMessageResolver import AbstractMessageResolver


class CallMessageResolver(AbstractMessageResolver):
    """
    Call type message.

    Encoding:
        The call message is a block struct where block 1 is a command number, blocks 1 + n is subcommands,
            blocks 1 + n + x are parameters and flags.

    Command Block:

        REQUIRED.

        [0xXX] - is a command byte. This byte must be specified in server and client proto file.

    Subcommands Blocks:

        Size byte is REQUIRED.
        Subcommands bytes are OPTIONAL.

        [0xXX][0xXX...] - 1 byte is a size of subcommand blocks. [2 … 1 + size] - is a subcommands. Subcommands
            must be specified in proto file.

    Parameters block:

        Size byte is REQUIRED.
        Parameters bytes are OPTIONAL

        [0xXX][Parameter block...] - 1 byte is a size of parameters block.

        Parameter sub-block:

            Parameter byte is REQUIRED.
            Size byte is REQUIRED.
            Encoded data block is OPTIONAL.

            [0xXX][0xXXXXXXXX][Encoded Data] - 1 bytes is a parameter. Parameter must be specified in proto file.
                2 ... 3 byte is size of data. [4 … 3 + size] - bytes is data
    """

    COMMAND_BLOCK_START_BYTE = 0
    SUBCOMMANDS_BLOCK_START_BYTE = 1

    PARAMETER_BLOCK_SIZE_START = 1
    PARAMETER_BLOCK_SIZE_LEN = 4

    def __get_subcommands_size(self, data: bytes) -> int:
        return int(data[self.SUBCOMMANDS_BLOCK_START_BYTE])

    def __get_subcommands_list(self, data: bytes) -> list:
        size = self.__get_subcommands_size(data)

        if not size:
            return []

        start = self.SUBCOMMANDS_BLOCK_START_BYTE + 1

        subcommands = data[start:start + size]

        return [*subcommands] if len(subcommands) > 1 else [subcommands]

    def __get_start_pos_parameters_block(self, data: bytes) -> int:
        return self.SUBCOMMANDS_BLOCK_START_BYTE + self.__get_subcommands_size(data) + 1

    def __get_parameters_block_size(self, data: bytes) -> int:
        return int(data[self.__get_start_pos_parameters_block(data)])

    def __get_parameters_dict(self, data: bytes) -> dict:
        size = self.__get_parameters_block_size(data)

        if not size:
            return {}

        params = {}
        start_block = self.__get_start_pos_parameters_block(data) + 1

        for i in range(size):
            parameter = data[start_block]

            start_data_pos = start_block + self.PARAMETER_BLOCK_SIZE_START + self.PARAMETER_BLOCK_SIZE_LEN

            param_size = int.from_bytes(data[start_block + self.PARAMETER_BLOCK_SIZE_START:start_data_pos])
            start_block = start_data_pos
            params[parameter] = data[start_block:start_block + param_size]
            start_block += param_size

        return params

    def create(self, params: dict) -> bytes:
        data = b""

        data += params["command"].to_bytes(1, byteorder='big')

        subcommands = params.get("subcommands") or []

        data += len(subcommands).to_bytes(1, byteorder='big')

        for subcommand in subcommands:
            data += subcommand.to_bytes(1, byteorder='big')

        parameters = params.get("parameters") or {}

        data += len(parameters.keys()).to_bytes(1, byteorder='big')

        for key, val in parameters.items():
            data += key.to_bytes(1, byteorder='big') + len(val).to_bytes(4, byteorder='big') + val

        return data

    def parse(self, data: bytes) -> dict:
        return {
            "command": data[self.COMMAND_BLOCK_START_BYTE],
            "subcommands": self.__get_subcommands_list(data),
            "parameters": self.__get_parameters_dict(data),
        }
