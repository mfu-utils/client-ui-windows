from abc import abstractmethod

from App.Core.Utils import DotPathAccessor


class AbstractDataFile(DotPathAccessor):
    def __init__(self, path: str):
        self._path = path

        super().__init__(self._load())

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def _load(self) -> dict:
        pass
