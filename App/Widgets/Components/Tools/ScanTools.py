from typing import Optional

from PySide6.QtWidgets import QWidget, QFileDialog

from App.Core.Utils import DocumentMediaType
from App.Models.Client.Scan import Format
from App.Services.Client.DocConvertorService import DOC_PATHS
from App.Widgets.Helpers.ScanHelpers import ScanHelpers
from App.Widgets.Modals.DevicesModal import DevicesModal
from App.Widgets.Modals.DocumentModal import DocumentModal
from App.helpers import ini, config, platform, notification, lc


class ScanTools:
    def __init__(self, parent: QWidget):
        self.parent = parent

        self.__scan_helpers = ScanHelpers(parent)

        self.__devices_modal: Optional[DevicesModal] = None

        self.__debug_mode = config('ocr_convertor.debug')

    def select(self, device: Optional[str] = None):
        if not ini('devices.auto_choose_device', bool):
            self.__devices_modal.close()
            self.__devices_modal.deleteLater()
            self.__devices_modal = None

        if self.__debug_mode:
            self.open_document_modal_debug()
            return

        self.__scan_helpers.load_document(device, DocumentMediaType.A4, lambda x: self.open_document_modal(x, Format.TIFF))

    def open_document_modal(self, image: bytes, _format: Format):
        DocumentModal(self.__debug_mode, _format, image, self.parent)

    def open_document_modal_debug(self):
        with open(config('ocr_convertor.debug_image'), 'rb') as img:
            self.open_document_modal(img.read(), Format.TIFF)

    def create_devices_modal(self, devices: list):
        modal = DevicesModal(devices, self.parent)

        modal.selected.connect(lambda x: self.select(x))

        self.__devices_modal = modal

    def create_scan(self):
        if ini('devices.auto_choose_device', bool):
            self.select()
            return

        ScanHelpers(self.parent).get_devices(self.create_devices_modal)

    def image_scan(self):
        paths = QFileDialog.getOpenFileName(
            self.parent,
            lc('fileDialog.title'),
            str(DOC_PATHS[platform().name]),
            lc('fileDialog.filter') % ' '.join(list(map(lambda x: f"*.{x.name.lower()}", Format))),
            options=QFileDialog.Option.DontResolveSymlinks | QFileDialog.Option.ReadOnly
        )

        path = paths[0]

        if not path:
            return

        try:
            _format = Format[path.upper()]
        except KeyError:
            notification().error(lc('load_image_title'), lc('load_image_msg') % path)
            return

        with open(path, 'rb') as img:
            self.open_document_modal(img.read(), _format)
