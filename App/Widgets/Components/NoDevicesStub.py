from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from App.helpers import styles


class NoDevicesStub(QWidget):
    def __init__(self, parent: QWidget = None):
        super(NoDevicesStub, self).__init__(parent)

        self.__label = QLabel(self)
        self.__label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label.setStyleSheet(styles('noDevicesStub'))
        self.__label.setText("No devices")

        v_layout = QVBoxLayout()
        v_layout.addStretch()
        v_layout.addWidget(self.__label)
        v_layout.addStretch()

        self.setLayout(v_layout)
