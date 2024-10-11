from datetime import datetime
from enum import Enum

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QSizePolicy

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers


class NotificationItem(DrawableWidget):
    class Type(Enum):
        SUCCESS = 'success'
        ERROR = 'error'
        WARNING = 'warning'

    TYPE_ICON = {
        Type.SUCCESS: "success_sign_16x16@2x.png",
        Type.ERROR: "error_sign_16x16@2x.png",
        Type.WARNING: "warning_sign_16x16@2x.png",
    }

    deleted = Signal()

    def __init__(self, _type: Type, title: str, text: str, parent: QWidget = None):
        super(NotificationItem, self).__init__(parent)
        self.setObjectName("NotificationItem")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.__central_layout = UIHelpers.v_layout((5, 5, 5, 5), 5)

        self.__header_layout = UIHelpers.h_layout((0, 0, 0, 0), 1)

        self.__sign = UIHelpers.image(self.TYPE_ICON[_type], self, (20, 20))
        self.__sign.setObjectName("NotificationItemSign")
        self.__header_layout.addWidget(self.__sign)

        self.__header_layout.addSpacing(5)

        self.__title_widget = QLabel(title, self)
        self.__title_widget.setObjectName("NotificationItemTitle")
        self.__title_widget.setFixedHeight(20)
        self.__header_layout.addWidget(self.__title_widget)

        self.__header_layout.addStretch()

        self.__close_button = QPushButton("\u2715")
        self.__close_button.setObjectName("NotificationItemCloseButton")
        self.__close_button.setFixedSize(16, 16)
        self.__close_button.clicked.connect(self.deleted.emit)
        self.__header_layout.addWidget(self.__close_button)

        self.__central_layout.addLayout(self.__header_layout)

        if text:
            self.__text_browser = QLabel(self)
            self.__text_browser.setObjectName('NotificationItemTextBrowser')
            self.__text_browser.setWordWrap(True)
            self.__text_browser.setText(text)
            self.__central_layout.addWidget(self.__text_browser)

        _now = datetime.now()

        self.__time_widget = QLabel(_now.strftime("%H:%M"), self)
        self.__time_widget.setToolTip(_now.strftime("%Y-%m-%d %H:%M:%S"))
        self.__time_widget.setObjectName("NotificationItemTime")
        self.__time_widget.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__central_layout.addWidget(self.__time_widget)

        self.setLayout(self.__central_layout)

        self.adjustSize()

