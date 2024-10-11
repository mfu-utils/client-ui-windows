import math
from typing import Optional

from PySide6.QtCore import Qt, QVariantAnimation, QSize, QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel

from App.Widgets.Components.LoadingAnimation import LoadingAnimation
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles
from App.Widgets.Modals.AbstractModal import AbstractModal


class LoadingModal(AbstractModal):
    def __init__(self, text: Optional[str] = None, parent: QWidget = None):
        super(LoadingModal, self).__init__(parent)
        self._frameless_window(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self._d8d(False)

        if not parent:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.Tool)

        self.setObjectName('LoadingModal')
        self.setStyleSheet(styles('loadingModal'))

        self.centralWidget().setObjectName('Loading')

        self.__central_layout = UIHelpers.h_layout()
        self.__central_layout.addStretch()

        self.__content_layout = UIHelpers.v_layout()

        self.__container_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)
        self.__container_layout.addStretch()
        self.__container_layout.addWidget(LoadingAnimation((60, 60), (6, 6), self))
        self.__container_layout.addStretch()

        self.__content_layout.addLayout(self.__container_layout)

        if text:
            label = QLabel(text, self)
            label.setObjectName('LoadingText')

            self.__content_layout.addWidget(label)

            self.__central_layout.addLayout(self.__content_layout)

        self.__central_layout.addStretch()

        self.centralWidget().setLayout(self.__central_layout)

        self.show()

        if not parent:
            UIHelpers.to_center_screen(self)
        else:
            UIHelpers.to_center(self)
