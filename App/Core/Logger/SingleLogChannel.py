from typing import Optional
from App.Core import Filesystem
from App.Core.Abstract import AbstractLogChannel
from App.Core.Logger.LogHelper import LogHelper
from App.Core import Config


class SingleLogChannel(AbstractLogChannel):
    def __init__(self, config: Config):
        super().__init__(config, 'single')

        self.__path = self._config['path']
        self.__level = self._config['level']
        self.__importance = LogHelper.get_importance(self.__level)

        LogHelper.create_dir_log_if_not_exists(self.__path)

    def append(self, message: str, log_level: str, subject: Optional[dict] = None):
        if LogHelper.get_importance(log_level) < self.__importance:
            return

        Filesystem.append_file(self.__path, LogHelper.get_log(log_level, message, subject))
