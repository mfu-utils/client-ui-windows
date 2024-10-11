from typing import Optional

from PySide6.QtWidgets import QWidget, QSizePolicy

from App.Core.Network.Client import ResponseDataPromise, ClientConfig
from App.Core.Network.Protocol.Responses import AbstractResponse
from App.Core.Utils import DocumentMediaType
from App.Services.Client.DeviceService import DeviceService
from App.Widgets.Helpers.QSignalObject import QSignalObject
from App.Widgets.Modals.ErrorModal import ErrorModal
from App.Widgets.Modals.LoadingModal import LoadingModal
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import lc, notification

# TODO: Delete signals and move to event system


class ScanHelpers:
    def __init__(self, widget: QWidget):
        self.__widget = widget

        self.__promise: Optional[ResponseDataPromise] = None

        self.__loading: Optional[LoadingModal] = None

        self.__main_window = UIHelpers.find_parent_recursive(self.__widget, 'MainWindow')

        self.__config = _config = ClientConfig.client_ui()

    def __create_loading_modal(self, loadig_text: Optional[str] = None):
        self.__loading = LoadingModal(loadig_text, UIHelpers.find_parent_recursive(self.__widget, 'MainWindow'))
        self.__loading.show()
        self.__loading.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def __delete_loading_modal(self):
        if not self.__loading:
            return

        self.__loading.close()
        self.__loading.deleteLater()
        self.__loading = None

    def __on_success(self, response: AbstractResponse, on_success: callable):
        self.__delete_loading_modal()
        on_success(response.data())

    def __on_error(self, text: str, widget: QWidget):
        self.__delete_loading_modal()
        self.__main_window.setDisabled(False)

        title = lc('errorModal.titles.network')
        text = text.strip()

        ErrorModal(title, text, UIHelpers.find_parent_recursive(widget, "MainWindow"))
        notification().error(title, text)

    def __create_success_signal_callback(self, on_success) -> callable:
        success_obj = QSignalObject()
        success_obj.triggered.connect(lambda x: self.__on_success(x[0], x[1]))

        def success_trigger(res): success_obj.trigger([res, on_success])

        return success_trigger

    def __create_error_signal_callback(self) -> callable:
        error_obj = QSignalObject()
        error_obj.triggered.connect(lambda x: self.__on_error(x[0], x[1]))

        def error_trigger(msg): error_obj.trigger([msg, self.__widget])

        return error_trigger

    def get_devices(self, on_success: callable, update: bool = False):
        self.__create_loading_modal(lc('loading.getDevicesList'))

        return DeviceService(self.__config).get_devices(
            self.__create_success_signal_callback(on_success),
            self.__create_error_signal_callback(),
            update
        )

    def load_document(self, device: Optional[str], media: DocumentMediaType, on_success: callable):
        self.__create_loading_modal(lc('loading.scanDocument'))

        return DeviceService(self.__config).get_document(
            self.__create_success_signal_callback(on_success),
            self.__create_error_signal_callback(),
            media,
            device
        )
