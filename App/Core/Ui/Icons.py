from typing import Dict

from PySide6.QtGui import QIcon, QImage, QPixmap

from App.Core.Logger import Log
from config import ICONS_PATH


class Icons:
    images_buffer: Dict[str, QImage] = {}
    icons_buffer: Dict[str, QIcon] = {}

    def __init__(self, log: Log):
        self.__log = log

    def load(self, name: str, is_icon: bool = False) -> bool:
        try:
            if is_icon:
                self.icons_buffer[name] = QIcon(self.path(name))
            else:
                self.images_buffer[name] = QImage(self.path(name))
        except Exception as e:
            self.__log.error(f'Cannot load asset icon: {name}. \n {e}')
            return False

        return True

    @staticmethod
    def path(name: str) -> str:
        return f'{ICONS_PATH}/{name}'.replace('\\', '/')

    def get_image(self, name: str) -> QImage:
        if not self.images_buffer.get(name):
            self.load(name)

        return self.images_buffer[name]

    def get_pixmap(self, name: str) -> QPixmap:
        return QPixmap(self.get_image(name))

    def get_icon(self, name: str) -> QIcon:
        if not self.icons_buffer.get(name):
            self.load(name, True)

        return self.icons_buffer[name]
