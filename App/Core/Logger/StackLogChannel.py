from App.Core.Abstract import AbstractLogChannel
from App.Core import Config
from typing import List, Optional


class StackLogChannel(AbstractLogChannel):
    def __init__(self, app, config: Config):
        super().__init__(config, "stack")

        self.__channels: List[AbstractLogChannel] = []

        for channel in self._config.get('channels'):
            self.__channels.append(app.get(f"log.{channel}"))

    def append(self, message: str, log_level: str, subject: Optional[dict] = None):
        for channel in self.__channels:
            channel.append(message, log_level, subject)
