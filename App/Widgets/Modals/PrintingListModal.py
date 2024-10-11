from typing import List, Dict

from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragLeaveEvent, QCloseEvent
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import QUrl, Qt, Signal

from App.Core.Network.Client import ClientConfig
from App.Core.Network.Protocol.Responses.AbstractResponse import AbstractResponse
from App.Core.Utils import MimeType
from App.Services import PDFService
from App.Services.Client.MimeFilters import MimeService
from App.Services.Client.Ui.UiPrinterService import UiPrinterService
from App.Widgets.Components.ModalButton import ModalButton
from App.Widgets.Components.PrintingFileItem import PrintingFileItem
from App.Widgets.Components.PrintingListModal.Errors import Errors
from App.Widgets.Components.PrintingListModal.LoadingDevicesBlock import LoadingDevicesBlock
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.Modals.ErrorModal import ErrorModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import styles, mime, lc, platform, network_manager, later, ini


class PrintingListModal(AbstractModal):
    error_loading_devices_signal = Signal(str)
    checkout_loading_animation_signal = Signal(bool)
    set_visible_errors_widget_signal = Signal(bool)
    set_enabled_file_signal = Signal(bool)
    update_view = Signal()

    def __init__(self, files: List[QUrl], accepted: List[QUrl], parent: QWidget = None):
        super().__init__(parent)
        self.setWindowFlag(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle(self._lc("title"))
        self.setMinimumSize(800, 600)
        self.setObjectName("PrintingFileParametersModal")
        self.setStyleSheet(styles(["printingListModal", "printingFileItem", "printingLoading"]))

        self.__send_converted_icons_by_default = ini('printing.send_converted_icons_by_default', bool)
        self.__send_converted_docs_by_default = ini('printing.send_converted_docs_by_default', bool)

        self.__urls = []
        self.__accepted = accepted
        self.__loading_items: int = 0
        self.__devices_loaded = False
        self.__devices: Dict = {}
        self.__printers_service = UiPrinterService()

        self.__error_type_message = self._lc("unsupported_type_file")

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 10), 5)

        # Empty stub >>>
        self.__stub = QWidget(self)
        self.__stub.setDisabled(True)
        self.__stub.setObjectName("PrintingListModalStub")

        self.__stub_h_layout = UIHelpers.h_layout()
        self.__stub_v_layout = UIHelpers.v_layout()

        self.__stub_v_layout.addStretch()
        self.__stub_v_layout.addWidget(QLabel(lc("printingModal.instruction"), self.__stub))
        self.__stub_v_layout.addStretch()

        self.__stub_h_layout.addStretch()
        self.__stub_h_layout.addLayout(self.__stub_v_layout)
        self.__stub_h_layout.addStretch()

        self.__stub.setLayout(self.__stub_h_layout)

        self.__central_layout.addWidget(self.__stub)
        # <<< Empty stub

        self.__scroll_area = UIHelpers.create_scroll(self, "PrintingListScrollArea")

        self.__scroll_widget = QWidget(self)
        self.__scroll_widget.setObjectName("PrintingListScrollWidget")

        self.__content_layout = UIHelpers.v_layout((10, 10, 10, 10), 0)

        self.__files_layout = UIHelpers.v_layout((0, 0, 0, 0), 5)

        self.__fill_items(files)

        self.__content_layout.addLayout(self.__files_layout)
        self.__content_layout.addStretch()

        self.__scroll_widget.setLayout(self.__content_layout)

        self.__scroll_area.setWidget(self.__scroll_widget)

        self.__central_layout.addWidget(self.__scroll_area)
        self.__scroll_area.setHidden(True)

        # Errors >>>
        self.__errors_widget = Errors(self)
        self.__errors_widget.set_message(self._lc("cannot_load_printers_message"))
        self.__errors_widget.hide()

        self.__central_layout.addWidget(self.__errors_widget)
        # <<< Errors

        self.__buttons_layout = UIHelpers.h_layout((10, 10, 10, 0), 5)

        # Loading devices block >>>
        self.__loading_devices_widget = LoadingDevicesBlock(self._lc("loading_devices_label"), self)
        self.__buttons_layout.addWidget(self.__loading_devices_widget)
        # <<< Loading devices block

        # Reload devices button >>>
        self.__reload_devices_button = ModalButton(
            self,
            "PrintingListReloadDevicesButton",
            self._lc("reload_devices_button"),
            callback=lambda: self.__start_loading_devices(True)
        )
        self.__reload_devices_button.hide()
        self.__buttons_layout.addWidget(self.__reload_devices_button)
        # <<< Reload devices button

        self.__buttons_layout.addStretch()

        self.__cancel_button = ModalButton(self, "PrintingListCancelButton", self._lc("cancel_button"), None, self.close)
        self.__buttons_layout.addWidget(self.__cancel_button)

        self.__send_button = ModalButton(self, "PrintingListSendButton", self._lc("send_button"), None, self.__send_to_print)
        self.__buttons_layout.addWidget(self.__send_button)

        self.__central_layout.addLayout(self.__buttons_layout)

        self.centralWidget().setLayout(self.__central_layout)

        self.__update_view()
        self.update_view.connect(self.__update_view)

        self.show()

        UIHelpers.to_center_screen(self)

        self.raise_()

        if (self.__loading_items > 0) or not self.__devices_loaded:
            self.__send_button.setDisabled(True)

        self.__start_loading_devices()

        UIHelpers.set_disabled_parent_recursive(self, "MainWindow", True)
        self.setEnabled(True)

    @staticmethod
    def _lc(name: str) -> str:
        return lc(f"printingListModal.{name}")

    def __update_view(self):
        enable = bool(len(list(self.findChildren(PrintingFileItem))) > 0)

        self.__stub.setHidden(enable)
        self.__scroll_area.setVisible(enable)

    def closeEvent(self, event: QCloseEvent):
        UIHelpers.set_disabled_parent_recursive(self, "MainWindow", False)

        super(PrintingListModal, self).closeEvent(event)

    def __fill_devices(self):
        for file_item in self.findChildren(PrintingFileItem):
            file_item: PrintingFileItem
            file_item.set_devices(self.__devices)

    def __set_enabled_devices(self, enable: bool):
        for file_item in self.findChildren(PrintingFileItem):
            file_item: PrintingFileItem
            file_item.set_enabled(enable)

    def __open_error_loading_devices(self, message: str):
        if hasattr(self, '__err_modal') and self.__getattribute__('__err_modal'):
            return

        title = lc("errorModal.titles.network")
        message = self._lc("error_loading_devices") % message
        self.__err_modal = ErrorModal(title, message, self, self.objectName())

    def __set_enable_loading_animation(self, enable: bool):
        self.__loading_devices_widget.setVisible(enable)
        self.__reload_devices_button.setVisible(not enable)

    def __set_visible_errors_widget(self, enable: bool):
        self.__errors_widget.setVisible(enable)

    def __start_loading_devices(self, update_server_cache: bool = False):
        self.__set_enable_loading_animation(True)

        promise = UiPrinterService.get_printers_promise(ClientConfig.client_ui(), network_manager(), update_server_cache)

        def stop_loading_devices():
            self.checkout_loading_animation_signal.emit(False)

            if (self.__loading_items == 0) and self.__devices_loaded:
                self.__send_button.setEnabled(True)

            self.__fill_devices()

            self.error_loading_devices_signal.disconnect()
            self.checkout_loading_animation_signal.disconnect()
            self.set_visible_errors_widget_signal.disconnect()

        def success_loading_devices(response: AbstractResponse):
            self.__devices_loaded = True

            self.__devices = dict(map(
                lambda x: (x[UiPrinterService.PRINTER_PARAMETER_NAME], x[UiPrinterService.PRINTER_PARAMETER_DISPLAY_NAME]),
                UiPrinterService.filter_hidden_devices(response.data() or [])
            ))

            self.set_visible_errors_widget_signal.emit(False)

            stop_loading_devices()

            self.set_enabled_file_signal.emit(True)
            self.set_enabled_file_signal.disconnect()

        def error_loading_devices(message: str):
            self.error_loading_devices_signal.emit(message)
            self.set_visible_errors_widget_signal.emit(True)

            stop_loading_devices()

            self.set_enabled_file_signal.emit(False)
            self.set_enabled_file_signal.disconnect()

        self.error_loading_devices_signal.connect(self.__open_error_loading_devices)
        self.checkout_loading_animation_signal.connect(self.__set_enable_loading_animation)
        self.set_visible_errors_widget_signal.connect(self.__set_visible_errors_widget)
        self.set_enabled_file_signal.connect(self.__set_enabled_devices)

        promise.then(success_loading_devices)
        promise.catch(error_loading_devices)

    def __add_loading_item(self):
        self.__loading_items += 1

        if hasattr(self, "__send_button"):
            self.__send_button.setDisabled(True)

    def __pop_loading_item(self):
        self.__loading_items -= 1

        if (not self.__loading_items) and self.__devices_loaded:
            self.__send_button.setDisabled(False)

    def __create_item(self, file: QUrl) -> PrintingFileItem:
        is_windows = platform().is_windows()
        path = file.toLocalFile()
        mime_type = mime().get_mime_enum(path)
        send_converted = False

        if mime_type in MimeType.image_group():
            send_converted = self.__send_converted_icons_by_default

        if mime_type in MimeType.doc_group():
            send_converted = self.__send_converted_docs_by_default

        item = PrintingFileItem({
            PrintingFileItem.PARAMETER_PATH: path.replace(":/", ":\\").replace("/", "\\") if is_windows else path,
            PrintingFileItem.PARAMETER_MIME: mime_type,
            PrintingFileItem.PARAMETER_TYPE: MimeType.alias(mime_type),
            PrintingFileItem.PARAMETER_TYPE_ERROR: False if file in self.__accepted else self.__error_type_message,
            PrintingFileItem.PARAMETER_SEND_CONVERTED: send_converted,
        }, self)

        if item.get_need_converting():
            self.__add_loading_item()
            item.converting_stopped.connect(lambda: self.__pop_loading_item())

        if not self.__devices_loaded:
            item.set_enabled(False)

        item.deleted.connect(lambda: later(50, self.update_view.emit))

        return item

    def __fill_items(self, files: List[QUrl]):
        for file in files:
            self.__files_layout.addWidget(self.__create_item(file))

    def __clear_urls(self):
        self.__urls = []
        self.__accepted = []

    def __send_to_print(self):
        for file in self.__scroll_widget.findChildren(PrintingFileItem):
            file: PrintingFileItem
            mime_type = file.get_mime()
            file.enable_warning(False)

            if not file.get_ready_to_print():
                continue

            if mime_type == MimeType.UNDEFINED:
                continue

            count_pages = 1

            if (converted := file.get_converted_path()) and (mime_type in MimeType.doc_group()):
                count_pages = PDFService.count_pages(converted)

            file.printing_doc.mime_type = mime_type

            self.__printers_service.send_to_print(
                file.printing_doc,
                count_pages,
                file.get_path(),
                converted,
                file.deleteLater,
                lambda: file.enable_warning(True)
            )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.__urls = event.mimeData().urls()
            self.__accepted = MimeService.filter_printing_types(self.__urls)

            if self.__accepted:
                event.acceptProposedAction()

        super(PrintingListModal, self).dragEnterEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.__clear_urls()

        super(PrintingListModal, self).dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        for file in self.__urls:
            item = self.__create_item(file)
            item.set_devices(self.__devices)

            self.__files_layout.addWidget(item)

        self.__update_view()

        self.__clear_urls()

        super(PrintingListModal, self).dropEvent(event)
