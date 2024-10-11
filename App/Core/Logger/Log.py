from typing import Optional

from App.Core.Logger.LogHelper import LogHelper
from App.Core.Utils.Wrapper import Wrapper
from App.Core.Abstract import AbstractLogChannel
from App.Core import Config


class Log:
    def __init__(self, chanel: AbstractLogChannel, config: Config):
        self.__channel: AbstractLogChannel = chanel
        self.__wrapper = Wrapper()
        self.__colors = config.get('logger.colors')
        self.__enabled = config.get('app.debug')

    def log(self, log_level: str, message: str, subject: Optional[dict] = None):
        if not self.__enabled:
            return

        self.__channel.append(log_level, message, subject)

    def info(self, message: str, subject: Optional[dict] = None):
        self.log(message, LogHelper.LOG_LEVEL_INFO, subject)

    def error(self, message: str, subject: Optional[dict] = None):
        self.log(message, LogHelper.LOG_LEVEL_ERROR, subject)

    def warning(self, message: str, subject: Optional[dict] = None):
        self.log(message, LogHelper.LOG_LEVEL_WARNING, subject)

    def success(self, message: str, subject: Optional[dict] = None):
        self.log(message, LogHelper.LOG_LEVEL_SUCCESS, subject)

    def debug(self, message: str, subject: Optional[dict] = None):
        self.log(message, LogHelper.LOG_LEVEL_DEBUG, subject)

