from abc import ABC, abstractmethod
from typing import List, Type

from App import Application


class AbstractSeeder(ABC):
    def __init__(self, app: Application) -> None:
        self.__app = app

    @abstractmethod
    def run(self):
        pass

    def _group(self, many: List[Type['AbstractSeeder']]):
        for item in many:
            self.__app.call(item(self.__app).run)
