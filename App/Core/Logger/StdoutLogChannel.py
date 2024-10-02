from typing import Optional

from App.Core.Abstract import AbstractLogChannel
from App.Core.Logger.LogHelper import LogHelper
from App.Core import Config
from App.Core.Utils.Wrapper import Wrapper


class StdoutLogChannel(AbstractLogChannel):
    ERROR_TEXT_COLOR = "#FFFFFF"

    def __init__(self, config: Config):
        super().__init__(config, 'stdout')
        self.__wrapper = Wrapper()

        self.__colors = self._config['colors']
        self.__level = self._config['level']
        self.__colorize = self._config['colorize']
        self.__importance = LogHelper.get_importance(self.__level)

    def append(self, message: str, log_level: str, subject: Optional[dict] = None):
        if LogHelper.get_importance(log_level) < self.__importance:
            return

        message = LogHelper.get_log(log_level, message, subject)

        if self.__colorize:
            if log_level == LogHelper.LOG_LEVEL_ERROR:
                message = self.__wrap_error_message(message)
            else:
                message = self.__wrap_message(message, log_level)

        print(message)

    def __wrap_error_message(self, message: str) -> str:
        bg_color = self.__colors['error']

        return self.__wrapper.background_color(self.__wrapper.color(message, self.ERROR_TEXT_COLOR), bg_color)

    def __wrap_message(self, message: str, log_level: str) -> str:
        return self.__wrapper.color(message, self.__colors[log_level])
