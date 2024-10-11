from PySide6.QtWidgets import QWidget

from App.Widgets.Components.ParameterViewItem import ParameterViewItem
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import lc


class DeviceParametersModal(AbstractModal):
    def __init__(self, parameters: dict, parent: QWidget = None):
        super(DeviceParametersModal, self).__init__(parent)
        self.setFixedSize(300, 400)

        self.setWindowTitle(lc('deviceParametersModal.title'))
        self.setObjectName('DeviceParametersModal')

        self.__parameters = parameters

        self.__parameters_layout = UIHelpers.v_layout((20, 10, 20, 20), 15)

        image_layout = UIHelpers.h_layout()
        image_layout.addStretch()
        image_layout.addWidget(UIHelpers.image('device_128x128@2x.png', self))
        image_layout.addStretch()

        self.__parameters_layout.addLayout(image_layout)

        for key, value in self.__parameters.items():
            self.create_parameter(key, value)

        self.centralWidget().setLayout(self.__parameters_layout)

        self._disable_all_parents('DevicesModal')

        self.show()

        UIHelpers.to_center(self, UIHelpers.find_parent_recursive(self, "MainWindow"))

    def create_parameter(self, name: str, value: str):
        self.__parameters_layout.addWidget(ParameterViewItem(name, value, self))
