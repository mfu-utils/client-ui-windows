from typing import Optional, Tuple, List, Dict

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel

from App.Core.Utils.Ui import Casts
from App.Widgets.Components.Controls.AbstractControlItem import AbstractControlItem
from App.Widgets.Components.Controls.CheckBoxControl import CheckBoxControl
from App.Widgets.Components.Controls.LineEditControl import LineEditControl
from App.Widgets.Components.Controls.MultiselectControl import MultiselectControl
from App.Widgets.Components.Controls.SpinBoxControl import SpinBoxControl
from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles
from App.Widgets.Components.Controls.ComboBoxControl import ComboBoxControl


class PreferencesControls(DrawableWidget):
    def __init__(self, name: str, parent: QWidget = None):
        super(PreferencesControls, self).__init__(parent)
        self.setObjectName('ControlsContainer')
        self.setStyleSheet(styles(['controlsContainer', 'scrollBar']))

        self.__get_value_callback: Optional[callable] = None
        self.__set_value_callback: Optional[callable] = None

        self.__items: List[AbstractControlItem] = []

        self.__layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        self.__scroll_area = UIHelpers.create_scroll(self, 'ControlsScrollArea')

        self.__scroll_area_widget = QWidget(self.__scroll_area)
        self.__scroll_area_widget.setObjectName('Controls')

        self.__scroll_area_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)
        label = QLabel(name, self)
        label.setFont(UIHelpers.font(16, QFont.Weight.DemiBold))
        label.setObjectName('ControlsTitle')
        label.setContentsMargins(10, 10, 10, 10)
        self.__scroll_area_layout.addWidget(label)

        self.__widgets_layout = UIHelpers.v_layout()

    def completed(self) -> bool:
        for control in self.__items:
            if not control.completed():
                return False

        return True

    def set_checking_prev_value_enabled(self, enabled: bool):
        for item in self.__items:
            item.set_checking_prev_value_enabled(enabled)

    def add_set_value_callback(self, callback: callable):
        self.__set_value_callback = callback

    def add_get_value_callback(self, callback: callable):
        self.__get_value_callback = callback

    def __get_insert_func(self, name: str) -> Optional[callable]:
        if self.__set_value_callback:
            return lambda x: self.__set_value_callback(name, x)

        return None

    @staticmethod
    def __cast_from_string(value: str, _type: type):
        if _type == bool and value is not None:
            return Casts.str2bool(value)

        if _type == str and value is None:
            return ''

        return _type(value)

    def __create_control_item(self, _type: type, value_type: type, name: str, parameters: list, callback: callable):
        value = self.__cast_from_string(self.__get_value_callback(name) if self.__get_value_callback else None, value_type)

        if set_value_func := self.__get_insert_func(name):
            widget = _type(self.__scroll_area_widget, *parameters, value, set_value_func)
            set_value_func(value)
        else:
            widget = _type(self, *parameters, value)

        self.__widgets_layout.addWidget(widget)

        if callback:
            callback(widget)

        self.__items.append(widget)

        return widget

    def create_line_edit(self, name: str, title: str, callback: Optional[callable] = None) -> LineEditControl:
        return self.__create_control_item(LineEditControl, str, name, [title], callback)

    def create_spinbox(self, name: str, title: str, _range: Optional[Tuple[int, int]], callback: Optional[callable] = None) -> SpinBoxControl:
        return self.__create_control_item(SpinBoxControl, int, name, [title, _range], callback)

    def create_check_box(self, name: str, title: str, callback: Optional[callable] = None) -> CheckBoxControl:
        return self.__create_control_item(CheckBoxControl, bool, name, [title], callback)

    def create_combo_box(self, name: str, title: str, items: Dict[str, str], callback: Optional[callable] = None) -> ComboBoxControl:
        return self.__create_control_item(ComboBoxControl, str, name, [title, items], callback)

    def create_multiselect(self, name: str, title: str, items: Dict[str, str], callback: Optional[callable] = None) -> MultiselectControl:
        return self.__create_control_item(MultiselectControl, str, name, [title, items], callback)

    def generate(self):
        for item in self.__items:
            item.generate()

        self.__widgets_layout.addStretch()

        self.__scroll_area_layout.addLayout(self.__widgets_layout)

        self.__scroll_area_widget.setLayout(self.__scroll_area_layout)

        self.__scroll_area.setWidget(self.__scroll_area_widget)

        self.__layout.addWidget(self.__scroll_area)

        self.setLayout(self.__layout)
