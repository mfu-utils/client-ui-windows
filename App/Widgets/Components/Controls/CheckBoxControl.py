from typing import Optional, List, Dict, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QCheckBox

from App.Widgets.Components.Controls.AbstractControlItem import AbstractControlItem

from App.helpers import image_path


class CheckBoxControl(AbstractControlItem):
    def __init__(self, parent: QWidget, title: str, value: bool = False, callback: Optional[callable] = None):
        super(CheckBoxControl, self).__init__(parent, title, value, callback)

        self.__enabled = False
        self.__enable(self._value)

    def __enable(self, state: int):
        self.__enabled = state == 2

    def __edit(self, state: int):
        self._new_value = state

        self.__enable(state)

        self._check_prev_value()

        if self._callback:
            self._callback(self.__enabled)

    def _init_widget(self):
        self._widget = QCheckBox(self)
        self._widget.setFixedSize(18, 18)
        self._widget.setObjectName('ControlCheckBox')
        self._widget.setCheckState(Qt.CheckState.Checked if self._value else Qt.CheckState.Unchecked)

    def _register_callback(self):
        self._widget.stateChanged.connect(self.__edit)

    def _get_style_sheet(self) -> dict:
        return {
            "styles": ["abstractControlItem", "controlCheckBox"],
            "replaces": {'checked': image_path('check.png')}
        }

    def _setups(self) -> Dict[str, Dict[str, Union[List[str], str]]]:
        return {
            "default": {
                "direction": "vertical",
                "layout": ["description", "errorMessage"],
            }
        }

    def _grid(self) -> List[List[str]]:
        return [["widget", "spacing|10|horizontal", "title", "spacing|10|horizontal", "setup|default", "stretch|horizontal"]]
