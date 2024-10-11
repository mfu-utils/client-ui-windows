from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QTextBrowser, QPushButton

from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles
from App.Widgets.Modals.AbstractModal import AbstractModal


class ErrorModal(AbstractModal):
    def __init__(self, title: str, text: str, widget: QWidget = None, disabled: str = "MainWindow"):
        super(ErrorModal, self).__init__(widget)
        self._frameless_window(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(styles(['errorModal', 'contextMenu', 'windowlessTitle']))

        self.centralWidget().setObjectName('ErrorModal')

        self.__central_layout = UIHelpers.v_layout()

        self.__central_layout.addWidget(self._create_title(title, "WindowlessTitle"))

        self.__content_layout = UIHelpers.h_layout((0, 0, 0, 0), 10)

        self.__icon_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)
        self.__icon_layout.addWidget(UIHelpers.image('error_32x32@2x.png', self))
        self.__icon_layout.addStretch()
        self.__content_layout.addLayout(self.__icon_layout)

        text_browser = QTextBrowser(self)
        text_browser.setObjectName('ErrorModalTextBrowser')
        text_browser.setText(text)

        self.__content_layout.addWidget(text_browser)

        self.__central_layout.addLayout(self.__content_layout)

        self.__button_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        close_button = QPushButton('Close')
        close_button.setObjectName('ErrorModalCloseButton')
        close_button.clicked.connect(self.close)

        self.__button_layout.addStretch()
        self.__button_layout.addWidget(close_button)

        self.__central_layout.addLayout(self.__button_layout)

        self.centralWidget().setLayout(self.__central_layout)

        self.show()

        UIHelpers.to_center_screen(self)

        self._disable_all_parents(disabled)
