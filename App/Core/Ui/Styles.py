from typing import List, Union
import re

from App.Core import Filesystem
from App.Core.Ui import Ini
from config import STYPES_PATH


class Styles:
    LINES_SPACES_PATTERN = re.compile(r"\n\s*")
    KEY_VALUE_SPACES_PATTERN = re.compile(r":\s*")
    HEADER_ITEMS_SPACES_PATTERN = re.compile(r",\s*")
    HEADER_END_SPACES_PATTERN = re.compile(r"\s*{")

    cache = {}

    def __init__(self, ini: Ini):
        self.__styles_path = f"{STYPES_PATH}/{ini.get('theme.style')}"

    def __prepared(self, styles: List[str]) -> str:
        content = ''.join(list(map(lambda x: self.cache[x], styles)))

        content = Styles.LINES_SPACES_PATTERN.sub("", content)
        content = Styles.KEY_VALUE_SPACES_PATTERN.sub(":", content)
        content = Styles.HEADER_ITEMS_SPACES_PATTERN.sub(",", content)
        content = Styles.HEADER_END_SPACES_PATTERN.sub("{", content)

        return content

    def get(self, names: Union[str, List[str]]) -> str:
        if isinstance(names, str):
            names = names.split(' ')

        for segment in names:
            if segment not in self.cache:
                self.cache[segment] = Filesystem.read_file(f"{self.__styles_path}/{segment}.qss")

        return self.__prepared(names)
