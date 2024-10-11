from re import compile, Pattern
from typing import Optional, Dict

from PySide6.QtWidgets import QWidget, QLineEdit

from App.Widgets.Components.Controls.AbstractControlItem import AbstractControlItem


class LineEditControl(AbstractControlItem):
    def __init__(self, parent: QWidget, title: str, value: str = "", callback: Optional[callable] = None):
        self.__pattern: Optional[Pattern] = None
        self.__pattern_key: Optional[str] = None
        self.__patterns: Dict[str, Pattern] = {}

        super(LineEditControl, self).__init__(parent, title, value, callback)

    def verify(self):
        if self.__pattern and self.__pattern.match(self._new_value) is None:
            self._set_primary_enabled(False)
            self.error_enable(self.__pattern_key)
            self._new_value = self._value
            return

        self.error_disable()
        self._check_prev_value()

    def __edit(self, text: str):
        self._new_value = text

        self.verify()

        if self._callback:
            self._callback(self._new_value)

    def pattern_disable(self):
        self.__pattern = None
        self.__pattern_key = None

    def pattern_enable(self, key: str):
        self.__pattern = self.__patterns[key]
        self.__pattern_key = key

    def _init_widget(self):
        self._widget = QLineEdit(self)
        self._widget.setFixedHeight(30)
        self._widget.setObjectName('ControlLineEdit')
        self._widget.setText(self._value)

    def _register_callback(self):
        self._widget.textEdited.connect(self.__edit)

    def pattern_set(self, key: str, pattern: str, invalid_message: str):
        self.__patterns.update({key: compile(pattern)})
        self._error_messages.update({key: invalid_message})

    def _get_style_sheet(self) -> dict:
        return {"styles": ["abstractControlItem", "controlLineEdit", "contextMenu"]}
