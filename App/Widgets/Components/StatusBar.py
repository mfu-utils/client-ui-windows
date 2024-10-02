from PySide6.QtWidgets import QWidget, QLabel

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import styles

from config import VERSION_DETAILED


class StatusBar(DrawableWidget):
    def __init__(self, parent: QWidget = None):
        super(StatusBar, self).__init__(parent)
        self.setFixedHeight(20)
        self.setObjectName('StatusBar')
        self.setStyleSheet(styles(['statusBar']))

        self.__central_layout = UIHelpers.h_layout((10, 2, 10, 2), 2)

        self.__version_widget = QLabel(f"v. {VERSION_DETAILED}", self)
        self.__version_widget.setObjectName('StatusBarVersion')
        self.__central_layout.addWidget(self.__version_widget)

        self.__central_layout.addStretch()

        self.setLayout(self.__central_layout)
