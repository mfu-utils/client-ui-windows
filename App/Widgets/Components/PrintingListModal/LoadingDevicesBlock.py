from PySide6.QtWidgets import QWidget, QLabel

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.Components.LoadingAnimation import LoadingAnimation
from App.Widgets.UIHelpers import UIHelpers


class LoadingDevicesBlock(DrawableWidget):
    def __init__(self, message: str, parent: QWidget = None):
        super(LoadingDevicesBlock, self).__init__(parent)

        self.setObjectName("PrintingListLoadingDevicesWidget")

        self.__loading_devices_layout = UIHelpers.h_layout((0, 0, 0, 0), 5)
        self.__loading_devices_layout.addWidget(LoadingAnimation((24, 24), (4, 4), self))

        self.__loading_devices_label = QLabel(self)
        self.__loading_devices_label.setObjectName("PrintingListLoadingDevicesLabel")
        self.__loading_devices_label.setText(message)

        self.__loading_devices_layout.addWidget(self.__loading_devices_label)

        self.setLayout(self.__loading_devices_layout)
