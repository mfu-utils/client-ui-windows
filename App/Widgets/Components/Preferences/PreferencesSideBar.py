from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QScrollArea

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.Components.Preferences.PreferencesSideBarItem import PreferencesSideBarItem
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles


class PreferencesSideBar(DrawableWidget):
    def __init__(self, parent: QWidget = None):
        super(DrawableWidget, self).__init__(parent)
        self.setObjectName('PreferencesSideBarContainer')
        self.setStyleSheet(styles('preferencesSideBarContainer scrollBar'))

        self.setFixedWidth(210)

        self.__sidebar_items: Dict[str, PreferencesSideBarItem] = {}

        self.__layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        self.__scroll_area = UIHelpers.create_scroll(self, 'PreferencesSideBarScrollArea')

        self.__scroll_area_widget = QWidget(self.__scroll_area)
        self.__scroll_area_widget.setObjectName('PreferencesSideBar')

        self.__scroll_area_layout = UIHelpers.v_layout((5, 5, 5, 5), 0)

    def create_item(self, key: str, name: str, callback: callable):
        item = PreferencesSideBarItem(name, callback)

        self.__sidebar_items.update({key: item})
        self.__scroll_area_layout.addWidget(item)
        self.__scroll_area_widget.update()

    def __clear_primary_items(self):
        for item in self.__sidebar_items.values():
            item.set_enabled(False)

    def enable(self, key: str):
        self.__clear_primary_items()
        self.__sidebar_items[key].set_enabled(True)

    def generate(self):
        self.__scroll_area_widget.setLayout(self.__scroll_area_layout)

        self.__scroll_area.setWidget(self.__scroll_area_widget)

        self.__layout.addWidget(self.__scroll_area)

        self.__scroll_area_layout.addStretch()

        self.setLayout(self.__layout)
