from App.Core.Abstract import AbstractDataFile
from App.Core import Filesystem


class YamlDataFile(AbstractDataFile):
    def __init__(self, yaml_path: str):
        super().__init__(yaml_path)

    def _load(self) -> dict:
        return Filesystem.read_yaml(self._path)

    def write(self):
        Filesystem.write_json(self._path, self._data)
