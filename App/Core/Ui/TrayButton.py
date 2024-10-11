from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QWidget, QSystemTrayIcon, QMenu
from App.helpers import icon, platform, styles


class TrayButton(QObject):
    def __init__(self, _icon: str, parent: QWidget = None):
        super().__init__(parent)

        self._tray = QSystemTrayIcon(icon(_icon), parent)
        self._tray.setVisible(True)

        self._menu = QMenu()

        if not platform().is_darwin():
            self._menu.setStyleSheet(styles("qMenu"))

        if platform().is_windows():
            self._tray.activated.connect(lambda reason: self.on_left_click(reason))

    def on_left_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._tray.contextMenu().popup(QCursor.pos())

    def add_action(self, title: str, _icon: str = None, callback: callable = None):
        action = QAction(title, self._menu)

        if _icon:
            action.setIcon(icon(_icon))

        if callback:
            action.triggered.connect(callback)

        self._menu.addAction(action)

        return action

    def add_separator(self):
        self._menu.addSeparator()

    def show(self):
        self._tray.setContextMenu(self._menu)
