from App.Core.Utils import Color
from App.Core.Utils import Wrapper


class Output:
    OUTPUT_TYPE_SUCCESS = 'success'
    OUTPUT_TYPE_INFO = 'info'
    OUTPUT_TYPE_WARNING = 'warning'
    OUTPUT_TYPE_ERROR = 'error'
    OUTPUT_TYPE_LINE = 'line'
    OUTPUT_TYPE_SUBTITLE = 'subtitle'

    OUTPUT_TYPES_COLORS = {
        OUTPUT_TYPE_SUCCESS: '#5B9561',
        OUTPUT_TYPE_LINE: '#5C962C',
        OUTPUT_TYPE_INFO: '#3F74BA',
        OUTPUT_TYPE_WARNING: '#E4B40F',
        OUTPUT_TYPE_ERROR: '#D64D5B',
        OUTPUT_TYPE_SUBTITLE: '#A68A0D',
    }

    def __output_with_prefix(self, prefix: str, message: str, _type: str):
        prefix = Wrapper.bold(prefix)
        prefix = Wrapper.background_color(prefix, Color(self.OUTPUT_TYPES_COLORS[_type]))

        print(f"{prefix} {message}")

    def __output(self, message: str, _type: str, indent: int, end: str):
        message = Wrapper.color(message, Color(self.OUTPUT_TYPES_COLORS[_type]))

        print(f"{' ' * indent}{message}", end=end)

    def success_message(self, message: str):
        self.__output_with_prefix(Wrapper.color(f" SUCCESS ", Color('black')), message, Output.OUTPUT_TYPE_SUCCESS)

    def info_message(self, message: str):
        self.__output_with_prefix(" INFO ", message, Output.OUTPUT_TYPE_INFO)

    def warning_message(self, message: str):
        self.__output_with_prefix(Wrapper.color(f" WARNING ", Color('black')), message, Output.OUTPUT_TYPE_WARNING)

    def error_message(self, message: str):
        self.__output_with_prefix(" ERROR ", message, Output.OUTPUT_TYPE_ERROR)

    def line(self, message: str, indent: int = 0, end: str = '\n'):
        self.__output(message, Output.OUTPUT_TYPE_LINE, indent, end)

    def endl(self):
        self.line('')

    def header(self, message: str, indent: int = 0, end: str = '\n'):
        self.__output(message, Output.OUTPUT_TYPE_SUBTITLE, indent, end)
