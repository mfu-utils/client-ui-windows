import os
import subprocess

from App.Core import Filesystem
from App.helpers import platform


class FileManagerService:
    @staticmethod
    def show(path: str) -> bool:
        if not Filesystem.exists_file(path):
            return False

        getattr(FileManagerService, f"show_{platform().name.lower()}")(path)

        return True

    @staticmethod
    def show_linux(path: str):
        subprocess.run(["xdg-open", path])

    @staticmethod
    def show_darwin(path: str):
        subprocess.run(["open", "-R", path])

    @staticmethod
    def show_windows(path: str):
        subprocess.run([os.path.join(os.getenv('WINDIR'), 'explorer.exe'), '/select,', os.path.normpath(path)])
