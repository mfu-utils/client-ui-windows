import platform
from typing import List


class Platform:
    WINDOWS = 'Windows'
    LINUX = 'Linux'
    DARWIN = "Darwin"

    def __init__(self):
        self.name = platform.system()

    @staticmethod
    def system_is(name: str) -> bool:
        return platform.system() == name

    def list(self) -> List[str]:
        return [self.WINDOWS, self.LINUX, self.DARWIN]

    def is_windows(self):
        return self.name == self.WINDOWS

    def is_linux(self):
        return self.name == self.LINUX

    def is_darwin(self):
        return self.name == self.DARWIN

    def current(self, names: str) -> bool:
        if names is None:
            return True

        if names[0] == "~":
            return not (self.name == names[1:])

        return self.name in names.split(',')
