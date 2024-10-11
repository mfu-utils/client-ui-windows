from typing import Any

from PySide6.QtWidgets import QWidget, QPushButton

from App.Core.Utils.Ui import Casts
from App.Models.Client.Scan import Format
from App.Models.Client.Document import Type as DocumentType
from App.Services.Client.Ui.UiScanService import UiScanService
from App.Services.Client.ScanTypeService import ScanTypeService
from App.Widgets.Components.ResizableImageWidget import ResizableImageWidget
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.Modals.ErrorModal import ErrorModal
from App.Widgets.UIHelpers import UIHelpers
from App.Widgets.Components.PreferencesControls import PreferencesControls
from App.helpers import styles, lc, ini, in_thread, platform
from App.Services.Client.Ui.UiDocConvertorService import UiDocConvertorService
from App.Services.Client.DocConvertorService import DocConvertorService
from App.Services.Client.TagService import TagService


class DocumentModal(AbstractModal):
    DOC_WIDTH = 210
    DOC_HEIGHT = 297
    FACTOR = DOC_HEIGHT / DOC_WIDTH
    PARAMETERS_WIDTH = 500

    def __init__(self, debug: bool, _format: Format, image: bytes, parent: QWidget = None):
        super(DocumentModal, self).__init__(parent)
        self.setObjectName("DocumentModal")
        self.setStyleSheet(styles(["documentModal"]))
        self.setWindowTitle(("(DEBUG MODE) " if debug else "") + self.__lc("windowName"))
        self.setMinimumSize(self.DOC_WIDTH * 2 + self.PARAMETERS_WIDTH, self.DOC_HEIGHT * 2)

        self.__format = _format
        self.__image_bytes = image

        self.__central_layout = UIHelpers.h_layout()

        self.__image = ResizableImageWidget(image)
        self.__central_layout.addWidget(self.__image)

        self.c_name = None

        self.__settings = {
            "langs": ini("recognition.default_langs")
        }

        self.__ok_button = self.__create_button("DocumentModalOkButton", "Ok", self.__save)
        self.__ok_button.setDisabled(True)
        self.__ok_button.setFixedWidth(70)

        self.__controls_layout = UIHelpers.v_layout((0, 0, 0, 0), 10)

        self.__controls = PreferencesControls(self.__lc("title"), self)
        self.__controls.setFixedWidth(self.PARAMETERS_WIDTH)
        self.__controls.add_get_value_callback(self.__get_value)
        self.__controls.add_set_value_callback(self.__set_value)

        self.__fill_settings(self.__controls)

        self.__controls.generate()

        self.after_generate()

        self.__controls.set_checking_prev_value_enabled(False)

        self.__controls_layout.addWidget(self.__controls)

        self.__buttons_widget = QWidget(self)
        self.__buttons_widget.setFixedWidth(self.PARAMETERS_WIDTH)
        self.__buttons_layout = UIHelpers.h_layout((0, 0, 0, 0), 10)
        self.__buttons_layout.addStretch()

        self.__buttons_layout.addWidget(self.__ok_button)

        self.__buttons_widget.setLayout(self.__buttons_layout)

        self.__controls_layout.addWidget(self.__buttons_widget)

        self.__central_layout.addLayout(self.__controls_layout)

        self.centralWidget().setLayout(self.__central_layout)

        self.show()

        UIHelpers.to_center(self, UIHelpers.find_parent_recursive(self, "MainWindow"))

    def __create_button(self, name: str, title: str, callback: callable) -> QPushButton:
        button = QPushButton(title, self)
        button.setObjectName(name)
        button.clicked.connect(callback)
        button.setMinimumWidth(70)
        button.setFixedHeight(30)

        return button

    def resizeEvent(self, event):
        if not platform().is_linux():
            self.setFixedWidth(int(self.height() / self.FACTOR) + self.PARAMETERS_WIDTH)

        super(DocumentModal, self).resizeEvent(event)

        if not platform().is_linux():
            return

        h = int((self.width() - self.PARAMETERS_WIDTH - 30) * self.FACTOR)

        if h > (max_h := self.height() - 20):
            h = max_h

        self.__image.setFixedSize(int(h / self.FACTOR), h)

    def __get_value(self, key: str) -> Any:
        return self.__settings.get(key)

    def __set_value(self, key: str, value: Any):
        self.__settings.update({key: value})

        if self.__ok_button:
            empty = not bool(self.__settings.get("name"))
            self.__ok_button.setDisabled(empty)

            if not self.c_name:
                return

            if empty:
                self.c_name.error_enable("empty_err")
            else:
                self.c_name.error_disable()

    def __save(self):
        name = self.__settings['name']
        _dir = ini('scans.dir')

        err = UiScanService.save(_dir, self.__image_bytes, name, self.__format)

        if err:
            ErrorModal(err[0], err[1], self)
            return

        scan = UiScanService.store(
            name,
            Casts.str2int(self.__settings['scan_type']) or None,
            UiScanService.get_scan_path(_dir, name, self.__format),
            self.__format,
            Casts.str2list(self.__settings["tags"])
        )

        if not scan:
            self.close()
            return

        if _types := Casts.str2int_list(self.__settings.get('converts') or []):
            langs = Casts.str2list(self.__settings.get("langs") or [])
            _types = list(map(lambda x: DocumentType(x), _types))

            # Move convert logic to another thread
            in_thread(lambda: UiDocConvertorService.convert_many(scan, _types, langs))

        self.close()

    @staticmethod
    def __lc(key: str) -> str:
        return lc(f"documentModal.{key}")

    def __fill_settings(self, pc: PreferencesControls):
        labels_width = 70

        if ini("ocr.enable", bool):
            converts = pc.create_multiselect(
                "converts",
                self.__lc("convert.title"),
                DocConvertorService.get_convertors()
            )

            converts.set_height_restriction(10)

            langs = pc.create_multiselect("langs", self.__lc("langs.title"), DocConvertorService.langs())
            langs.set_height_restriction(10)

        tags = pc.create_multiselect("tags", self.__lc("tags.title"), TagService.for_select())
        tags.set_creation_items_enable(True)
        tags.set_height_restriction(10)

        _type_items = ScanTypeService.for_select("* " + self.__lc("scanType.nullable"))
        _type = pc.create_combo_box("scan_type", self.__lc("scanType.title"), _type_items)
        _type.label().setFixedWidth(labels_width)

        self.c_name = pc.create_line_edit("name", self.__lc("name.title"))
        self.c_name.label().setFixedWidth(labels_width)
        self.c_name.pattern_set("has_name", "^(?:[\\w._0-9- ]+|)$", self.__lc("name.pattern_err"))
        self.c_name.pattern_enable("has_name")
        self.c_name.error_add("empty_err", self.__lc("name.empty_err"))

    def after_generate(self):
        self.c_name.error_enable("empty_err")
