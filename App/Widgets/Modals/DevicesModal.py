from typing import List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from App.Widgets.Components.DevicePreview import DevicePreview
from App.Widgets.Components.NoDevicesStub import NoDevicesStub
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles


class DevicesModal(AbstractModal):
    selected = Signal(str)

    def __init__(self, devices: List[dict], parent: QWidget = None):
        super(DevicesModal, self).__init__(parent)
        self.setMinimumSize(300, 300)
        self.setObjectName('DevicesModal')
        self.setStyleSheet(styles('devicesModal'))

        self.__central_layout = UIHelpers.h_layout()
        self.__devices: List[DevicePreview] = []

        if devices is not None and len(devices):
            for device in devices:
                self.__create_device(device)
        else:
            self.__central_layout.addWidget(NoDevicesStub(self))

        self.centralWidget().setLayout(self.__central_layout)

        self._disable_all_parents()

        self.show()

        UIHelpers.to_center(self, UIHelpers.find_parent_recursive(self, "MainWindow"))

    def __create_device(self, params: dict) -> DevicePreview:
        device = DevicePreview(params, self)

        self.__devices.append(device)
        self.__central_layout.addWidget(device)
        device.selected.connect(lambda: self.selected.emit(params['device']))

        return device
