import os
import json
import tempfile

import yaml
from typing import Union, Optional

try:
    from yaml import CLoader as YLoader
    from yaml import CDumper as YDumper
except ImportError:
    from yaml import Loader as YLoader
    from yaml import Dumper as YDumper


class Filesystem:
    @staticmethod
    def _prepare_path(path: str) -> str:
        return os.path.expanduser(path)

    @staticmethod
    def get_stats(path: str) -> Optional[os.stat_result]:
        if not Filesystem.exists(path):
            return None

        return os.stat(Filesystem._prepare_path(path))

    @staticmethod
    def get_tmp_path() -> str:
        return tempfile.gettempdir()

    @staticmethod
    def create_tmp_path(path: str) -> str:
        tmp_path = Filesystem.get_tmp_path()

        if path[0] == '/':
            path = path[1:]

        return os.path.join(tmp_path, path)

    @staticmethod
    def write_tmp(path: str, content: Union[str, bytes]) -> bool:
        return Filesystem.write_file(Filesystem.create_tmp_path(path), content)

    @staticmethod
    def write_file(path: str, content: Union[str, bytes]) -> bool:
        is_bytes = isinstance(content, bytes)

        with open(Filesystem._prepare_path(path), 'w' + ('b' if is_bytes else '')) as file:
            file.write(content)

        return Filesystem.exists(path)

    @staticmethod
    def read_file(path: str, is_bytes: bool = False, encoding: str = 'utf-8') -> Union[str, bytes]:
        with open(
                Filesystem._prepare_path(path),
                'r' + ('b' if is_bytes else ''),
                encoding=None if is_bytes else encoding
        ) as file:
            return file.read()

    @staticmethod
    def append_file(path: str, content: Union[str, bytes]) -> bool:
        path = Filesystem._prepare_path(path)

        if not Filesystem.exists(path):
            Filesystem.write_file(path, content)

            return Filesystem.exists(path)

        is_bytes = isinstance(content, bytes)

        with open(path, 'a' + ('b' if is_bytes else '')) as file:
            file.write(f"\n{content}")

        return True

    @staticmethod
    def _raise_is_not_a_file(path: str, action: str):
        if os.path.isdir(path):
            raise Exception(f"Cannot {action} '{Filesystem._prepare_path(path)}'. Is not a file")

    @staticmethod
    def create_file(path: str):
        Filesystem.write_file(path, "")

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(Filesystem._prepare_path(path))

    @staticmethod
    def exists_file(path: str) -> bool:
        if not os.path.exists(Filesystem._prepare_path(path)):
            return False

        if not os.path.isfile(path):
            return False

        return True

    @staticmethod
    def delete(path: str) -> bool:
        Filesystem._raise_is_not_a_file(path, 'delete')

        os.remove(Filesystem._prepare_path(path))

        return not Filesystem.exists(path)

    @staticmethod
    def copy(path_from: str, path_to: str) -> bool:
        Filesystem._raise_is_not_a_file(path_from, 'find')

        Filesystem.write_file(path_to, Filesystem.read_file(path_from, True))

        return Filesystem.exists(path_to)

    @staticmethod
    def move(path_from: str, path_to: str) -> bool:
        Filesystem._raise_is_not_a_file(path_from, 'move')

        os.replace(Filesystem._prepare_path(path_from), Filesystem._prepare_path(path_to))

        return True

    @staticmethod
    def rename(path: str, new_name: str) -> bool:
        Filesystem._raise_is_not_a_file(path, 'rename')

        path = Filesystem._prepare_path(path)

        segments = path.split('/')
        segments[-1] = new_name

        os.rename(path, '/'.join(segments))

        return True

    @staticmethod
    def read_json(path: str) -> Union[dict, list]:
        return json.loads(Filesystem.read_file(path))

    @staticmethod
    def write_json(path: str, data: Union[dict, list], indent=4, ensure_ascii=False) -> bool:
        return Filesystem.write_file(path, json.dumps(data, indent=indent, ensure_ascii=ensure_ascii))

    @staticmethod
    def read_yaml(path: str) -> Union[dict, list]:
        return yaml.load(Filesystem.read_file(path), Loader=YLoader)

    @staticmethod
    def write_yaml(path: str, data: Union[dict, list]) -> bool:
        return Filesystem.write_file(path, yaml.dump(data, Dumper=YDumper))
