from App.Core.Abstract import AbstractDataFile
from App.Core import Filesystem


class JsonDataFile(AbstractDataFile):
    def __init__(self, json_path: str):
        super().__init__(json_path)

    def _load(self) -> dict:
        return Filesystem.read_json(self._path)

    def write(self):
        Filesystem.write_yaml(self._path, self._data)
