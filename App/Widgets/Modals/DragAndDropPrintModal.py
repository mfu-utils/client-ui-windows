from typing import List

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDropEvent, QDragLeaveEvent, QDragEnterEvent
from PySide6.QtWidgets import QWidget, QLabel, QPushButton

from App.Services.Client.MimeFilters import MimeService
from App.Widgets.Components.Tools.PrintingTools import PrintingTools
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import styles, lc


class DragAndDropPrintModal(AbstractModal):
    closed = Signal()

    def __init__(self, parent: QWidget = None):
        super(DragAndDropPrintModal, self).__init__(parent)
        self._frameless_window(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self._d8d(False)
        self.set_shadow_enabled(False)
        self.setFixedSize(200, 200)
        self.centralWidget().setObjectName("PrintModal")
        self.setStyleSheet(styles("printModal"))

        self.__central_Layout = UIHelpers.v_layout((5, 5, 5, 5), spacing=0)

        self.__headers = UIHelpers.h_layout((0, 0, 0, 0), 3)

        self.__close_button = QPushButton("\u2715")
        self.__close_button.setFixedSize(16, 16)
        self.__close_button.setObjectName("PrintModalCloseButton")
        self.__close_button.clicked.connect(self.close)

        self.__headers.addStretch()
        self.__headers.addWidget(self.__close_button)

        self.__central_Layout.addLayout(self.__headers)

        self.__central_Layout.addStretch()

        self.__box_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)
        self.__box_layout.addStretch()

        self.__content_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)

        self.__image_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)
        self.__image_layout.addStretch()

        self.__upload_image = UIHelpers.image('upload_64x64@2x.png')
        self.__upload_image.setObjectName("PrintModalImage")
        self.__upload_image.hide()
        self.__image_layout.addWidget(self.__upload_image)

        self.__cross_image = UIHelpers.image('cross_64x64@2x.png')
        self.__cross_image.setObjectName("PrintModalImage")
        self.__cross_image.hide()
        self.__image_layout.addWidget(self.__cross_image)

        self.__image_layout.addStretch()
        self.__content_layout.addLayout(self.__image_layout)

        self.__instruction = lc("printingModal.instruction")
        self.__upload_message = lc("printingModal.upload_message")
        self.__error_message = lc("printingModal.error_message")

        self.__message = QLabel(self.__instruction, self)
        self.__message.setObjectName("PrintModalMessage")
        self.__message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__content_layout.addWidget(self.__message)

        self.__box_layout.addLayout(self.__content_layout)

        self.__box_layout.addStretch()

        self.__central_Layout.addLayout(self.__box_layout)

        self.__central_Layout.addStretch()

        self.centralWidget().setLayout(self.__central_Layout)

        self.__urls: List[QUrl] = []
        self.__accepted_urls: List[QUrl] = []
        self.setAcceptDrops(True)

        self.show()

    def closeEvent(self, event):
        self.closed.emit()

        super(DragAndDropPrintModal, self).closeEvent(event)

    def __show_accept_drop_message(self):
        if self.__urls:
            self.__upload_image.show()
            self.__message.setText(self.__upload_message)

            return

        self.__cross_image.show()
        self.__message.setText(self.__error_message)

    def __hide_accept_drop_message(self):
        self.__upload_image.hide()
        self.__cross_image.hide()
        self.__message.setText(self.__instruction)
        self.__urls = []
        self.__accepted_urls = []

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.__urls = event.mimeData().urls()
            self.__accepted_urls = MimeService.filter_printing_types(self.__urls)
            self.__show_accept_drop_message()

            if self.__accepted_urls:
                event.acceptProposedAction()

        super(DragAndDropPrintModal, self).dragEnterEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.__hide_accept_drop_message()

        super(DragAndDropPrintModal, self).dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        PrintingTools.open_printing_parameters_modal(self.__urls, self.__accepted_urls, self)

        self.__hide_accept_drop_message()
        self.hide()

        super(DragAndDropPrintModal, self).dropEvent(event)
