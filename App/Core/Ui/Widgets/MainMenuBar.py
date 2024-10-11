from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QMenu, QWidget

from App.helpers import config, lc, icon, shortcut, platform, styles


def determinate_shortcut(action_name: str) -> Union[str, None]:
    _shortcut = shortcut(action_name)

    if _shortcut is None:
        return None

    if '|' in _shortcut:
        segments = _shortcut.split('|')

        for segment in segments:
            if ':' in segment:
                _platform, sc = segment.split(':')

                if platform().current(_platform):
                    return sc

    return _shortcut


class MainMenuBar:
    def __init__(self, parent: QWidget = None):
        self.parent = parent
        self.menu_bar = QMenuBar(parent)

        if not platform().is_darwin():
            self.menu_bar.setStyleSheet(styles(['qMenuBar', 'qMenu']))

        for menu in config('menu'):
            name = menu.get('name')
            submenu = self.__create_menu(lc(name[1:]) if name[0] == "$" else name)

            if icon_name := menu.get('icon'):
                submenu.setIcon(icon(icon_name))

            for action_data in menu.get('actions'):
                self.generate_action(submenu, action_data)

    def __create_menu(self, name: str) -> QMenu:
        menu = self.menu_bar.addMenu(lc(name[1:]) if name[0] == "$" else name)

        menu.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )

        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        return menu

    @staticmethod
    def __create_action(submenu: QMenu, name: str) -> QAction:
        return submenu.addAction(name)

    def generate_action(self, submenu: QMenu, action_data: dict):
        if not platform().current(action_data.get('platforms')):
            return

        if action_data.get('separator'):
            submenu.addSeparator()
            return

        name = action_data.get('name')
        action = self.__create_action(submenu, lc(name[1:]) if name[0] == "$" else name)

        if disabled := action_data.get('disabled'):
            action.setDisabled(disabled)

        if icon_name := action_data.get('icon'):
            action.setIcon(icon(icon_name))

        if callback := action_data.get('action'):
            func = self.parent.__getattribute__(callback)
            action.triggered.connect(func)

            if shortcut_keys := determinate_shortcut(callback):
                action.setShortcut(shortcut_keys)

    def get_manu_bar(self) -> QMenuBar:
        return self.menu_bar
