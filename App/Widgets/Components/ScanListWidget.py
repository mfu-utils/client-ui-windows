from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy

from App.Core import Filesystem
from App.Models.Client.Scan import Scan
from App.Services.Client.Ui.FileManagerService import FileManagerService
from App.Services.Client.Ui.UiScanService import UiScanService
from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.Components.ScanItem import ScanItem
from App.Widgets.Helpers.WindowsHelpers import WindowsHelpers
from App.Widgets.Modals.ShowDocumentModal import ShowDocumentModal
from App.Widgets.UIHelpers import UIHelpers


class ScanListWidget(DrawableWidget):
    def __init__(self, name: str, items_callback: callable = None, parameters: dict = None, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName(name)

        self.__parameters = parameters or {}

        self.__items_callback = items_callback

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)
        self.__items_layout = UIHelpers.v_layout((5, 5, 5, 5), 0)

        self.update_items()

        self.__central_layout.addLayout(self.__items_layout)
        self.__central_layout.addStretch()

        self.setLayout(self.__central_layout)

    def __add_item(self, _id: int, parameters: dict) -> ScanItem:
        item = ScanItem(parameters, self)

        self.__items_layout.addWidget(item)

        return item

    def __create_empty_stub(self):
        lbl = QLabel(self.__parameters['stub_title'], self)
        lbl.setObjectName("ScanListEmptyStub")
        lbl.setFixedHeight(30)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.__items_layout.addWidget(lbl)

    def update_items(self, items: List[Scan] = None):
        while item := self.__items_layout.takeAt(0):
            item.widget().deleteLater()

        self.__init_items(items or self.__items_callback())

    def __create_delete_callback(self, scan: Scan):
        def callback():
            UiScanService.delete(scan)
            self.update_items()

        return callback

    def __create_not_found_file_error(self, path: str):
        WindowsHelpers.file_not_found(path, parent=UIHelpers.find_parent_recursive(self, 'MainWindow'))

    def __create_link_callback(self, scan: Scan):
        def callback():
            if not FileManagerService.show(scan.path):
                self.__create_not_found_file_error(scan.path)

        return callback

    def __create_show_callback(self, scan: Scan):
        def callback():
            if not Filesystem.exists_file(scan.path):
                self.__create_not_found_file_error(scan.path)
                return

            ShowDocumentModal(scan.title, scan.path, self)

        return callback

    def __init_items(self, items: List[Scan]):
        scans = {}

        for scan in items:
            scans.update({scan.id: scan})

            # noinspection PyUnresolvedReferences,PyTypeChecker
            self.__add_item(scan.id, {
                ScanItem.PARAMETER_TYPE: scan.type.name if scan.type else None,
                ScanItem.PARAMETER_TITLE: scan.title,
                ScanItem.PARAMETER_DATETIME: scan.created_at.strftime('%Y-%m-%d %H:%M'),
                ScanItem.PARAMETER_FORMAT: scan.format,
                ScanItem.PARAMETER_PATH: scan.path,
                ScanItem.PARAMETER_TAGS: list(map(lambda x: x.name, scan.tags)),
                ScanItem.PARAMETER_ACTION_ON_SHOW: self.__create_show_callback(scan),
                ScanItem.PARAMETER_ACTION_ON_DELETE: self.__create_delete_callback(scan),
                ScanItem.PARAMETER_ACTION_ON_LINK: self.__create_link_callback(scan),
                ScanItem.PARAMETER_DOCUMENTS_LIST: scan.documents,
            })

        if not len(scans):
            self.__create_empty_stub()
