from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QMenu

from App.Models.Client.Document import Document
from App.Services.Client.DocConvertorService import DocConvertorService
from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.Helpers.WindowsHelpers import WindowsHelpers
from App.Widgets.Modals.ConfirmModal import ConfirmModal
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import icon, lc, ini
from App.Services.Client.Ui.FileManagerService import FileManagerService


class ScanItem(DrawableWidget):
    PARAMETER_ACTION_ON_DELETE = "on_delete"
    PARAMETER_DOCUMENTS_LIST = "documents"
    PARAMETER_ACTION_ON_LINK = "on_link"
    PARAMETER_ACTION_ON_SHOW = "on_show"
    PARAMETER_DATETIME = "datetime"
    PARAMETER_FORMAT = "format"
    PARAMETER_TITLE = "title"
    PARAMETER_TYPE = "type"
    PARAMETER_TAGS = "tags"
    PARAMETER_PATH = "tags"
    PARAMETER_MENU = "menu"

    def __init__(self, parameters: dict, parent: QWidget = None):
        super(ScanItem, self).__init__(parent)
        self.setObjectName("ScanItem")

        self.__parameters = parameters
        self.__title = parameters[self.PARAMETER_TITLE]
        self.__on_delete = self.__parameters.get(self.PARAMETER_ACTION_ON_DELETE)

        self.__central_layout = UIHelpers.h_layout((5, 3, 5, 3), 5)

        self.__central_layout.addWidget(UIHelpers.image("scan_32x32@2x.png", self))

        self.__text_layout = UIHelpers.v_layout((0, 0, 0, 0), 3)

        self.__headers_layout = UIHelpers.h_layout((0, 0, 0, 0), 3)

        if parameters[self.PARAMETER_TYPE]:
            self.__type = self.__create_label(parameters[self.PARAMETER_TYPE], "ScanItemType")
            self.__headers_layout.addWidget(self.__type)

        self.__title_widget = self.__create_label(self.__title, "ScanItemTitle")
        self.__headers_layout.addWidget(self.__title_widget)

        self.__headers_layout.addStretch()

        self.__text_layout.addLayout(self.__headers_layout)

        self.__params_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        self.__datetime = self.__create_label(parameters[self.PARAMETER_DATETIME], "ScanItemDatetime")
        self.__datetime.setFixedWidth(102)
        self.__params_layout.addWidget(self.__datetime)
        self.__params_layout.addSpacing(10)

        self.__format = self.__create_label(parameters[self.PARAMETER_FORMAT].name, "ScanItemFormat")
        self.__params_layout.addWidget(self.__format)
        self.__params_layout.addSpacing(10)

        self.__tags = []

        for tag in parameters[self.PARAMETER_TAGS]:
            tag = self.__create_label(tag, "ScanItemTag")
            self.__params_layout.addWidget(tag)
            self.__tags.append(tag)

        self.__params_layout.addStretch()

        self.__text_layout.addLayout(self.__params_layout)

        self.__central_layout.addLayout(self.__text_layout)
        self.__central_layout.addStretch()

        self.__buttons_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        if on_link := self.__parameters.get(self.PARAMETER_ACTION_ON_LINK):
            self.__create_button("link.png", "ScanItemLinkButton", on_link)

        if on_show := self.__parameters.get(self.PARAMETER_ACTION_ON_SHOW):
            self.__create_button("visible.png", "ScanItemShowButton", on_show)

        if self.__on_delete:
            self.__create_button("bin.png", "ScanItemDeleteButton", self._deleted_button_clicked)

        self.__central_layout.addLayout(self.__buttons_layout)

        self.setLayout(self.__central_layout)

    def __create_link_callback(self, doc: Document):
        def callback():
            if not FileManagerService.show(doc.path):
                WindowsHelpers.file_not_found(doc.path, parent=UIHelpers.find_parent_recursive(self, "MainWindow"))

        return callback

    def contextMenuEvent(self, event):
        convert_enabled = ini('ocr.enable', bool)

        menu = QMenu(self)
        menu.setObjectName("ScanItemContextMenu")
        menu.setMinimumWidth(200)
        menu.move(self.mapToGlobal(event.pos()))

        convertors = DocConvertorService.TYPES
        documents = self.__parameters[self.PARAMETER_DOCUMENTS_LIST]

        docs_menu = QMenu(menu)
        docs_action = menu.addAction('Documents')
        docs_action.setMenu(docs_menu)

        if not documents:
            docs_action.setDisabled(True)
            docs_action.setText('Documents (Empty)')

        for document in documents:
            document: Document

            action = docs_menu.addAction(
                f"(.{convertors[document.type]['extension']}) {self.__parameters[self.PARAMETER_TITLE]}"
            )
            action.triggered.connect(self.__create_link_callback(document))

        convertors_menu = QMenu(menu)
        convertors_action = menu.addAction("Convert at" + ("" if convert_enabled else " (Disabled)"))
        convertors_action.setMenu(convertors_menu)

        _doc_types = list(map(lambda x: x.type, documents))

        if convert_enabled:
            for _type, convertor in convertors.items():
                c_item = convertors_menu.addAction(f"(.{convertor['extension']}) {convertor['name']}")

                if _type in _doc_types:
                    c_item.setIcon(icon('enabled.png'))

                c_item.triggered.connect(lambda: convertor['name'])
        else:
            convertors_action.setDisabled(True)

        menu.show()

        self.setProperty("primary", True)
        UIHelpers.update_style(self)
        menu.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched.objectName() == "ScanItemContextMenu":
            if event.type() == QEvent.Type.Close:
                self.setProperty("primary", False)
                UIHelpers.update_style(self)

        return super().eventFilter(watched, event)

    def __delete_callback(self):
        self.__on_delete()
        self.deleteLater()

    def _deleted_button_clicked(self):
        modal = ConfirmModal(
            "MainWindow",
            lc('history.deleteModal.header'),
            lc('history.deleteModal.ask') % self.__title,
            self
        )
        
        modal.confirmed.connect(self.__delete_callback)

    def __create_label(self, text: str, name: str):
        lbl = QLabel(text, self)
        lbl.setObjectName(name)

        return lbl

    def __create_button(self, _icon: str, name: str, handle: callable) -> QPushButton:
        button = QPushButton(self)
        button.setIcon(icon(_icon))
        button.setObjectName(name)
        button.setFixedSize(32, 32)
        button.clicked.connect(handle)

        self.__buttons_layout.addWidget(button)

        return button
