from typing import Union, Any, List


class ProtoBuilder:
    def __init__(self, commands: dict, codes: dict, types: dict):
        self.__commands = commands
        self.__codes = codes
        self.__types = types

    @staticmethod
    def __determinate_int_len(data: int) -> int:
        if data == 0:
            return 1

        for i in range(1, 8):
            if data < 0xFF ** i:
                return i

        raise Exception("Int len cannot be more than 64 bit")

    @staticmethod
    def __encode_float(value: float) -> bytes:
        if negative := value < 0:
            value *= -1

        f, s = str(value).split(".")

        if len(s) > 1:
            s = s[::-1]

        f, s = int(f), int(s)

        f = ProtoBuilder.__encode_int(f)
        s = ProtoBuilder.__encode_int(s) if s else b""

        return (len(f) | (0xF0 if negative else 0x00)).to_bytes(1, 'big') + f + s

    @staticmethod
    def __decode_float(value: bytes) -> float:
        first_len = value[0]
        negative = -1 if (first_len & 0xF0) else 1
        first = value[1:first_len + 1]
        second = '0' if value[1:] == first else value[first_len + 1:]

        if len(second) > 1:
            second = second[::-1]

        return float(f"{first}.{second}") * negative

    @staticmethod
    def __decode_int(data: bytes) -> int:
        if len(data) > 1 and data[0] == '\x00':
            return int.from_bytes(data[1:], 'big') * -1

        return int.from_bytes(data, 'big')

    @staticmethod
    def __encode_int(value: int) -> bytes:
        negative = b""

        if value < 0:
            value *= -1
            negative = "\x00"

        return negative + value.to_bytes(ProtoBuilder.__determinate_int_len(value), 'big')

    @staticmethod
    def __encode_list(value: List[Union[str, int, float, bool]]) -> bytes:
        data = b""

        for item in value:
            val = ProtoBuilder.__encode_value(item)

            data += len(val).to_bytes(1, 'big') + val

        return data

    @staticmethod
    def __decode_list(value: bytes, _type: type) -> List[Union[str, int, float, bool]]:
        values = []

        while len(value):
            _len = value[0]
            values.append(ProtoBuilder.__decode_value(value[1:_len + 1], _type))
            value = value[_len + 1:]

        return values

    @staticmethod
    def __encode_value(value: Union[str, bytes, int, float, bool, list]) -> bytes:
        _type = type(value)

        if _type is bytes:
            return value

        if _type is str:
            return value.encode('utf-8')

        if _type is int:
            return ProtoBuilder.__encode_int(value)

        if _type is bool:
            return b"\x01" if value else b"\x00"

        if _type is float:
            return ProtoBuilder.__encode_float(value)

        if _type is list:
            return ProtoBuilder.__encode_list(value)

        raise Exception(f"Cannot encode data")

    @staticmethod
    def __decode_value(value: bytes, _type: type, is_list: bool = False) -> Union[str, bytes, int, float, bool, list]:
        if is_list:
            return ProtoBuilder.__decode_list(value, _type)

        if _type is bytes:
            return value

        if _type is str:
            return value.decode('utf-8')

        if _type is int:
            return ProtoBuilder.__decode_int(value)

        if _type is float:
            return ProtoBuilder.__decode_float(value)

        if _type is bool:
            return False if value == b"\x00" else True

        raise Exception(f"Cannot decode data")

    def __prepare_parameter(self, name: str, value: Any, parameters_data: dict) -> dict:
        if not (parameters_data := parameters_data.get(name)):
            raise Exception(f"Cannot find parameter {name}")

        _type = parameters_data['type']
        _val_type = type(value)
        number = parameters_data['number']
        _number_type = type(number)

        if value is None and parameters_data['required']:
            raise Exception(f"Missing required parameter {name}")

        if _val_type is list:
            if _number_type is str:
                if len(value) < 1 and number == "+":
                    raise Exception(f"Missing required parameter {name}")

            if _number_type is int:
                if len(value) != number:
                    raise Exception(f"Len of parameters must be equal to {str(number)}")

            for i, val in enumerate(value):
                if type(val) is not _type:
                    raise Exception(f"Parameter {i} in {name} must be type {_type.__name__}")
        else:
            if _type is not _val_type:
                raise Exception(f"Parameter {name} must be type {_type.__name__}")

        if variants := parameters_data.get('variants'):
            if value not in variants:
                raise Exception(f"Parameter '{name}' must be one of '{', '.join(variants)}'")

            value = variants[value]

        return {parameters_data['code']: self.__encode_value(value)}

    def prepare_command(self, command: str, subcommands: list, parameters: dict) -> dict:
        command_data = self.__commands.get(command)
        subcommands_data = command_data.get('subcommands')

        subcommands = subcommands or []
        parameters = parameters or {}

        if not command_data:
            raise Exception(f"Unknown command '{command}'")

        subcommands_codes = []
        parameters_data = None

        for subcommand in subcommands:
            if not (subcommand_data := subcommands_data.get(subcommand)):
                raise Exception(f"Cannot find subcommand '{subcommand}'")

            subcommands_codes.append(subcommand_data['code'])
            parameters_data = subcommand_data.get('parameters')

        if len(subcommands) == 0:
            parameters_data = command_data.get('parameters') or {}

        parameters_codes = {}

        for parameter, value in parameters.items():
            parameters_codes.update(self.__prepare_parameter(parameter, value, parameters_data))

        return {
            "command": command_data['code'],
            "subcommands": subcommands_codes,
            "parameters": parameters_codes
        }

    def from_codes(self, command: int, subcommands: list[bytes], parameters: dict) -> dict:
        command_codes_data = self.__codes.get(command)

        if not command_codes_data:
            raise Exception(f"Unknown command code '{command}'")

        command_name: str = command_codes_data["name"]
        command_data = self.__commands.get(command_name)

        subcommands_codes_data = command_codes_data.get('subcommands')
        subcommands_data = command_data.get('subcommands')
        subcommands_names = []
        parameters_codes_data = None
        parameters_data = None
        defaults = None

        for subcommand in subcommands:
            subcommand_code_data = subcommands_codes_data.get(int.from_bytes(subcommand, 'big'))

            if not subcommand_code_data:
                raise Exception(f"Unknown subcommand code '{subcommand}'")

            name = subcommand_code_data['name']
            subcommand_data = subcommands_data.get(name)
            subcommands_names.append(name)

            parameters_codes_data = subcommand_code_data.get("parameters")
            parameters_data = subcommand_data.get("parameters")
            defaults = subcommand_data.get("defaults")

        parameters_values = {}

        if not parameters_codes_data:
            parameters_codes_data = command_codes_data.get('parameters')
            parameters_data = command_data.get("parameters")
            defaults = command_data.get("defaults")

        for parameter, value in parameters.items():
            parameter_code_data = parameters_codes_data.get(parameter)

            if not parameter_code_data:
                raise Exception(f"Unknown subcommand parameter code '{parameter}'")

            name = parameter_code_data['name']

            parameter_data = parameters_data.get(name)

            if variants := parameter_code_data.get("variants"):
                value = variants.get(value[0])
            else:
                value = self.__decode_value(value, parameter_data['type'], bool(parameter_data['number']))

            parameters_values.update({name: value})

        for name, value in defaults.items():
            if name in parameters_values:
                continue

            parameters_values.update({name: value})

        return {
            "command": command_name,
            "subcommands": subcommands_names,
            "parameters": parameters_values,
        }
