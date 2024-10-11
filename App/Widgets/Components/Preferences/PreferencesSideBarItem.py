from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles


class PreferencesSideBarItem(DrawableWidget):
    def __init__(self, name: str, callback: callable, parent: QWidget = None):
        super(PreferencesSideBarItem, self).__init__(parent)
        self.setObjectName('PreferencesSideBarItem')
        self.setFixedHeight(26)

        self.setStyleSheet(styles('preferencesSideBarItem'))

        self.__callback = callback

        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(10, 2, 10, 2)

        self.__label = QLabel(name, self)
        self.__label.setObjectName('PreferencesSideBarItemLabel')

        self.__layout.addWidget(self.__label)
        self.__layout.addStretch()

        self.setLayout(self.__layout)

    def set_enabled(self, enabled: bool):
        self.setProperty('primary', enabled)
        UIHelpers.update_style(self)
        UIHelpers.update_style(self.__label)

    def mouseReleaseEvent(self, event):
        self.__callback()

        super(PreferencesSideBarItem, self).mouseReleaseEvent(event)

