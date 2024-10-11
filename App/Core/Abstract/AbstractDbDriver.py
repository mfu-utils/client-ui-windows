from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy import create_engine, Engine

from App.Core.Logger import Log


class AbstractDbDriver(ABC):
    def __init__(self, log: Log):
        self._log = log
        self._engine: Optional[Engine] = self.create_engine()

    @abstractmethod
    def creds(self) -> str:
        pass

    def engine(self) -> Engine:
        return self._engine

    def create_engine(self) -> Optional[Engine]:
        try:
            return create_engine(self.creds())
        except BaseException as e:
            self.db_error(f'Failed to create engine: {str(e)}')

    def db_error(self, message: str):
        self._log.error(f"DB driver error. {message}")
