from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.Modals.DeviceParametersModal import DeviceParametersModal
from App.helpers import pixmap, styles


class DevicePreview(DrawableWidget):
    selected = Signal()

    def __init__(self, parameters: dict, parent: QWidget = None):
        super(DevicePreview, self).__init__(parent)
        self.setObjectName('DevicePreview')
        self.setFixedSize(130, 190)

        self.__parameters = parameters

        self.__icon = QLabel(self)
        self.__icon.setPixmap(pixmap('device_128x128@2x.png'))

        central = QVBoxLayout()
        central.setContentsMargins(0, 0, 0, 5)
        central.setSpacing(0)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 3, 3, 0)
        button_layout.addStretch()

        info_button = QPushButton('!')
        info_button.setObjectName('DevicePreviewInfoButton')
        info_button.setFixedSize(16, 16)
        info_button.clicked.connect(self.open_scaner_info)

        button_layout.addStretch()
        button_layout.addWidget(info_button)

        central.addLayout(button_layout)
        central.addWidget(self.__icon)
        central.addSpacing(5)

        content_layout = QVBoxLayout()

        content_layout.addWidget(self.create_label(parameters['model'], 'TitleLabel'))
        content_layout.addWidget(self.create_label(parameters['vendor'], 'SubtitleLabel'))

        central.addLayout(content_layout)

        self.setLayout(central)

        self.setStyleSheet(styles('devicePreview'))

    def mouseReleaseEvent(self, event):
        self.selected.emit()
        super(DevicePreview, self).mouseReleaseEvent(event)

    def create_label(self, text: str, name: str) -> QLabel:
        label = QLabel(text, self)
        label.setObjectName(name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return label

    def open_scaner_info(self):
        DeviceParametersModal(self.__parameters, self)
