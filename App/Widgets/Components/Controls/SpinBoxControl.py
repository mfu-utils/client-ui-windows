from typing import Tuple, Optional, List, Dict, Union

from PySide6.QtWidgets import QWidget, QSpinBox

from App.Widgets.Components.Controls.AbstractControlItem import AbstractControlItem

from App.helpers import image_path


class SpinBoxControl(AbstractControlItem):
    def __init__(self, parent: QWidget, title: str, _range: Optional[Tuple[int, int]] = None, value: int = 0, callback: Optional[callable] = None):
        self._range = _range

        super(SpinBoxControl, self).__init__(parent, title, value, callback)

    def __edit(self, value: int):
        self._new_value = value

        self._check_prev_value()

        if self._callback:
            self._callback(value)

    def _init_widget(self):
        self._widget = QSpinBox(self)
        self._widget.setFixedHeight(30)
        self._widget.setObjectName('ControlSpinBox')

        if self._range is not None:
            self._widget.setRange(self._range[0], self._range[1])

        self._widget.setValue(self._value)

    def _register_callback(self):
        self._widget.valueChanged.connect(self.__edit)

    def _get_style_sheet(self) -> dict:
        return {
            "styles": ["abstractControlItem", "controlSpinBox", "contextMenu"],
            "replaces": {
                "upButton": image_path("up_arrow.png"),
                "downButton": image_path("down_arrow.png"),
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
        return [["title", "spacing|10|horizontal", "widget", "spacing|10|horizontal", "setup|default", "stretch|horizontal"]]
