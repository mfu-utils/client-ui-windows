from enum import Enum
from typing import Union

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QPushButton

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import lc


class Notification(DrawableWidget):
    class Type(Enum):
        SUCCESS = 'success'
        ERROR = 'error'
        WARNING = 'warning'

    deleted = Signal()

    def __init__(self, _type: Union[Type, str], text: str, parent: QWidget = None):
        super(Notification, self).__init__(parent)
        self.setFixedHeight(45)

        if isinstance(_type, str):
            _type = Notification.Type(_type)

        self.setObjectName('Notification')
        self.setProperty(_type.value, True)

        self.__central_layout = UIHelpers.v_layout((5, 5, 5, 5), 0)

        self.__header_layout = UIHelpers.h_layout((0, 0, 0, 0), 1)

        self.__title = QLabel(lc("notifications.notify.title"), self)
        self.__title.setObjectName("NotificationTitle")
        self.__title.setFixedHeight(16)

        self.__header_layout.addWidget(self.__title)

        self.__header_layout.addStretch()

        self.__close_button = QPushButton("\u2715")
        self.__close_button.setObjectName("NotificationCloseButton")
        self.__close_button.setFixedSize(16, 16)
        self.__close_button.clicked.connect(self.deleted.emit)
        self.__header_layout.addWidget(self.__close_button)

        self.__central_layout.addLayout(self.__header_layout)

        self.__text_widget = QLabel(text, self)
        self.__text_widget.setObjectName("NotificationText")
        self.__text_widget.setFixedHeight(20)
        self.__central_layout.addWidget(self.__text_widget)

        self.setLayout(self.__central_layout)

        UIHelpers.update_style(self)
