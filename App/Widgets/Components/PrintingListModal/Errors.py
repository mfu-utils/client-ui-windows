from PySide6.QtWidgets import QWidget, QLabel

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers


class Errors(DrawableWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setObjectName("PrintingListErrorsWidget")

        self.__errors_layout = UIHelpers.h_layout((10, 0, 10, 0), 10)

        self.__error_image = UIHelpers.image("error_sign_16x16@2x.png")
        self.__error_image.setObjectName("PrintingFileItemErrorTypeIcon")
        self.__errors_layout.addWidget(self.__error_image)

        self.__error_message = QLabel(self)
        self.__error_message.setObjectName("PrintingListErrorMessage")
        self.__errors_layout.addWidget(self.__error_message)

        self.__errors_layout.addStretch()

        self.setLayout(self.__errors_layout)

    def set_message(self, message: str):
        self.__error_message.setText(message)
