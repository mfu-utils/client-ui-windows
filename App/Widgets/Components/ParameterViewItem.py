from typing import Union

from PySide6.QtWidgets import QWidget, QLabel

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles, lc


class ParameterViewItem(DrawableWidget):
    def __init__(self, name: str, value: Union[str, int, float, list], parent: QWidget = None):
        super(ParameterViewItem, self).__init__(parent)
        self.setObjectName('DeviceParameterItem')
        self.setStyleSheet(styles('deviceParameterItem'))
        self.setFixedHeight(30)

        self.__layout = UIHelpers.v_layout((0, 0, 0, 0), 0)

        name = QLabel(lc(f'deviceParametersModal.{name}'), self)
        name.setObjectName('DeviceParameterName')
        name.setFixedHeight(11)

        value = QLabel(self.__parse_value(value), self)
        value.setObjectName('DeviceParameterValue')
        name.setFixedHeight(15)

        self.__layout.addWidget(name)
        self.__layout.addWidget(value)

        self.setLayout(self.__layout)

    @staticmethod
    def __parse_value(value: Union[int, float, list, str]) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return str(value)
        elif isinstance(value, list):
            return ', '.join(map(lambda x: str(x), value))

        raise TypeError(f'Unsupported type {type(value)}')
