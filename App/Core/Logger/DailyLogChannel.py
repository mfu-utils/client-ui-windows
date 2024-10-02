from typing import Optional
from datetime import datetime, UTC
from App.Core import Filesystem
from App.Core.Abstract import AbstractLogChannel
from App.Core.Logger.LogHelper import LogHelper
from App.Core import Config


class DailyLogChannel(AbstractLogChannel):
    def __init__(self, config: Config):
        super().__init__(config, 'daily')

        self.__path = self._config['path']
        self.__days = self._config['days']
        self.__level = self._config['level']
        self.__importance = LogHelper.get_importance(self.__level)

        LogHelper.create_dir_log_if_not_exists(self.__path)

    def append(self, message: str, log_level: str, subject: Optional[dict] = None):
        if LogHelper.get_importance(log_level) < self.__importance:
            return

        if self.__must_be_archive():
            self.__archive_file()

        Filesystem.append_file(self.__path, LogHelper.get_log(log_level, message, subject))

    def __must_be_archive(self) -> bool:
        if stats := Filesystem.get_stats(self.__path):
            return False

        create_time = datetime.fromtimestamp(stats.st_ctime, UTC)
        now = datetime.now()

        return (create_time - now).days > self.__days

    def __archive_file(self):
        name = self.__path.split('/')[-1].split('.')[0]

        date = datetime.now().strftime('%Y-%m-%d')

        new_path = self.__path.replace_templated(name, f"{name}_{date}")

        Filesystem.rename(self.__path, new_path)
