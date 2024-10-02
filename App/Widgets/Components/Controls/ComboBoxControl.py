from typing import Dict, Optional, List, Union

from PySide6.QtWidgets import QWidget, QComboBox, QListView, QAbstractItemView

from App.Widgets.Components.Controls.AbstractControlItem import AbstractControlItem

from App.helpers import image_path, platform


class ComboBoxControl(AbstractControlItem):
    def __init__(self, parent: QWidget, title: str, items: Dict[str, str], value: Optional[str] = None, callback: Optional[callable] = None):
        self.__items = items

        super(ComboBoxControl, self).__init__(parent, title, value, callback)

    def __edit(self, value: int):
        self._new_value = list(self.__items.keys())[value]

        self._check_prev_value()

        if self._callback:
            self._callback(self._new_value)

    def _init_widget(self):
        self._widget = QComboBox(self)
        self._widget.setObjectName("ControlComboBox")

        self.__list_view = QListView(self._widget)

        self.__list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.__list_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)

        self._widget.setView(self.__list_view)

        self._widget.setFixedSize(200, 30)

        for key, value in self.__items.items():
            self._widget.addItem(value, key)

        self._widget.setCurrentIndex(self._widget.findData(self._value) if self._value else 0)

    def _register_callback(self):
        self._widget.currentIndexChanged.connect(self.__edit)

    def _get_style_sheet(self) -> dict:
        c_box_styles = ["controlComboBox"]

        if platform().is_darwin():
            c_box_styles.append("controlComboBoxMacFix")

        return {
            "styles": ["abstractControlItem", *c_box_styles, "scrollBar"],
            "replaces": {
                "downArrow": image_path("down_arrow.png"),
            }
        }

    def _setups(self) -> Dict[str, Dict[str, Union[List[str], str]]]:
        return {
            "default": {
                "direction": "vertical",
                "layout": ["description", "errorMessage"],
            },
        }

    def _grid(self) -> List[List[str]]:
        return [
            ["title", "spacing|10|horizontal", "widget", "stretch|horizontal"],
            ["", "", "setup|default", ""],
        ]
