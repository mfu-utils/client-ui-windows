from abc import ABC, abstractmethod
from App.Core import Config
from typing import Optional


class AbstractLogChannel(ABC):
    def __init__(self, config: Config, channel: str):
        self._config = config.get(f'logger.channels.{channel}')

    @abstractmethod
    def append(self, message: str, log_level: str, subject: Optional[dict] = None) -> None:
        pass
