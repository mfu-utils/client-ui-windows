from typing import Union

from PySide6.QtWidgets import QWidget

from App.Widgets.Components.ResizableImageWidget import ResizableImageWidget
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import platform


class ShowDocumentModal(AbstractModal):
    DOC_WIDTH = 210
    DOC_HEIGHT = 297
    FACTOR = DOC_HEIGHT / DOC_WIDTH

    def __init__(self, title: str, image: Union[bytes, str], parent: QWidget = None):
        self.__resizable = False

        super(ShowDocumentModal, self).__init__(parent)

        self.setObjectName('ShowDocumentModal')
        self.setWindowTitle(title)
        self.setMinimumSize(self.DOC_WIDTH * 2, self.DOC_HEIGHT * 2)

        self.__central_layout = UIHelpers.h_layout()

        self.__image = ResizableImageWidget(image)
        self.__central_layout.addWidget(self.__image)

        self.centralWidget().setLayout(self.__central_layout)

        self.show()

        self._disable_all_parents()

        self.__resizable = True

    def resizeEvent(self, event):
        if not self.__resizable:
            return

        if not platform().is_linux():
            self.setFixedWidth(int(self.height() / self.FACTOR))

        super(ShowDocumentModal, self).resizeEvent(event)

        if not platform().is_linux():
            return

        self.__image.setFixedWidth(int(self.__image.height() / self.FACTOR))
