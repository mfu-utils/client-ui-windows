from typing import Union, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QWidget

from App.Core.Utils import DocumentMediaType, DocumentOrder, MimeType
from App.Core.Utils.PaperTray import PaperTray
from App.Core.Utils.Ui import Patterns, Casts
from App.Core.Utils.Ui.PrintingPagePolicy import PrintingPagePolicy
from App.Widgets.Components.Controls.LineEditControl import LineEditControl
from App.Widgets.Components.ModalButton import ModalButton
from App.Widgets.Components.PreferencesControls import PreferencesControls
from App.Widgets.Components.PrintingFileParametersModal.DocStub import DocStub
from App.DTO.Client import PrintingDocumentDTO
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import lc, platform, styles


class PrintingFileParametersModal(AbstractModal):
    saved = Signal(PrintingDocumentDTO)
    canceled = Signal()

    PARAMETER_TRANSPARENCY = "transparency"
    PARAMETER_PAGES_POLICY = "pages_policy"
    PARAMETER_PAPER_SIZE = "paper_size"
    PARAMETER_PAPER_TRAY = "paper_tray"
    PARAMETER_LANDSCAPE = "landscape"
    PARAMETER_MIRROR = "mirror"
    PARAMETER_DEVICE = "device"
    PARAMETER_COPIES = "copies"
    PARAMETER_PAGES = "pages"
    PARAMETER_ORDER = "order"
    PARAMETER_SEND_CONVERTED = "send_converted"

    def __init__(
        self,
        path: str,
        tmp_path: Optional[str],
        mime_type: MimeType,
        devices: dict,
        doc: PrintingDocumentDTO,
        parent: QWidget = None
    ):
        super(PrintingFileParametersModal, self).__init__(parent)
        self.setWindowFlag(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("PrintingFileParametersModal")
        self.setMinimumSize(800, 570)
        self.setStyleSheet(styles(["printingFileParametersModal", "scrollBar"]))

        self.__doc = PrintingDocumentDTO(**doc.as_dict())
        self.__devices = devices
        self.__tmp_path = tmp_path
        self.__mime_type = mime_type

        self.setWindowTitle(self.__lc("title") % path)

        self.__central_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        if tmp_path:
            self.__create_document(tmp_path)
        else:
            self.__central_layout.addWidget(DocStub(self.__lc('no_view'), self))

        self.__parameters_layout = UIHelpers.v_layout((0, 0, 0, 0), 5)

        self.__scroll_area = UIHelpers.create_scroll(self, "PrintingFileParametersScrollArea")
        self.__scroll_area.setFixedWidth(400)

        self.__controls = PreferencesControls(path.split("\\" if platform().is_windows() else "/")[-1], self)
        self.__controls.setObjectName("PrintingFileParametersControls")
        self.__controls.add_get_value_callback(self.__get_value)
        self.__controls.add_set_value_callback(self.__set_value)
        self.__init_controls()
        self.__controls.generate()

        self.__scroll_area.setWidget(self.__controls)

        self.__parameters_layout.addWidget(self.__scroll_area)

        self.__buttons_layout = UIHelpers.h_layout(spacing=5)

        self.__cancel_button = ModalButton(
            self, "PrintingFileParametersCancelButton", self.__lc("cancel_button"), callback=self.__canceled
        )
        self.__buttons_layout.addWidget(self.__cancel_button)

        self.__save_button = ModalButton(
            self, "PrintingFileParametersSaveButton", self.__lc("save_button"), callback=self.__saved
        )
        self.__buttons_layout.addWidget(self.__save_button)

        self.__parameters_layout.addLayout(self.__buttons_layout)

        if not platform().is_windows():
            self.__parameters_layout.addSpacing(10)

        self.__central_layout.addLayout(self.__parameters_layout)

        self.centralWidget().setLayout(self.__central_layout)

        self.show()
        UIHelpers.set_disabled_parent_recursive(self, "MainWindow", True)
        self.setEnabled(True)

        UIHelpers.to_center_screen(self)

        self.raise_()

    def __create_document(self, path: str):
        self.__document = QPdfDocument()
        self.__document.load(path)

        self.__doc_view = QPdfView()
        self.__doc_view.setObjectName("PrintingFileParametersPDFView")
        self.__doc_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.__doc_view.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.__doc_view.setDocument(self.__document)

        self.__central_layout.addWidget(self.__doc_view)

    def get_count_pages(self) -> int:
        if hasattr(self, '__document'):
            return self.__document.pageCount()

        return -1

    def closeEvent(self, event):
        UIHelpers.set_disabled_parent_recursive(self, "MainWindow", False)

        super(PrintingFileParametersModal, self).closeEvent(event)

    def __canceled(self):
        self.canceled.emit()
        self.close()

    def __saved(self):
        self.saved.emit(self.__doc)
        self.close()

    def __get_value(self, name: str) -> str:
        return Casts.to_str(self.__doc.__getattribute__(name))

    def __set_value(self, name: str, value: str) -> None:
        if isinstance(value, str):
            nullable, _type = self.__doc.type_of(name)
            value = Casts.str_to(value, _type, nullable)

        self.__doc.__setattr__(name, value)

    @staticmethod
    def __lc(name: str) -> Union[str, Dict[str, str]]:
        return lc(f"printingFileParametersModal.{name}")

    @staticmethod
    def __clc(control: str, item: str) -> Union[str, Dict[str, str]]:
        return PrintingFileParametersModal.__lc(f"controls.{control}.{item}")

    def __init_controls(self):
        label_width = 140
        target_width = 200

        # DEVICE
        device = self.__controls.create_combo_box(
            self.PARAMETER_DEVICE,
            self.__clc(self.PARAMETER_DEVICE, "title"),
            self.__devices
        )
        device.label().setFixedWidth(label_width)
        device.target().setFixedWidth(target_width)

        # COPIES
        copies = self.__controls.create_spinbox(
            self.PARAMETER_COPIES, self.__clc(self.PARAMETER_COPIES, "title"), (1, 999)
        )
        copies.label().setFixedWidth(label_width)
        copies.target().setFixedWidth(target_width)

        # PAPER SIZE
        media = self.__controls.create_combo_box(
            self.PARAMETER_PAPER_SIZE,
            self.__clc(self.PARAMETER_PAPER_SIZE, "title"),
            Casts.enum2dict(DocumentMediaType)
        )
        media.label().setFixedWidth(label_width)
        media.target().setFixedWidth(target_width)

        # PAPER TRAY
        # noinspection PyTypeChecker
        paper_tray = self.__controls.create_combo_box(
            self.PARAMETER_PAPER_TRAY,
            self.__clc(self.PARAMETER_PAPER_TRAY, "title"),
            {
                None: self.__clc(self.PARAMETER_PAPER_TRAY, "default"),
                **Casts.enum2dict(PaperTray, self.__lc("paper_tray_items"))
            }
        )
        paper_tray.label().setFixedWidth(label_width)
        paper_tray.target().setFixedWidth(target_width)

        # ORDER
        order = self.__controls.create_combo_box(
            self.PARAMETER_ORDER,
            self.__clc(self.PARAMETER_ORDER, "title"),
            Casts.enum2dict(DocumentOrder, self.__lc("ordering_items")),
        )
        order.label().setFixedWidth(label_width)
        order.target().setFixedWidth(target_width)

        pages: Optional[LineEditControl] = None

        # PRINTING PAGES
        pages_policy = self.__controls.create_combo_box(
            self.PARAMETER_PAGES_POLICY,
            self.__clc(self.PARAMETER_PAGES_POLICY, "title"),
            printing_pages_policies := Casts.enum2dict(PrintingPagePolicy, self.__lc("pages_items"))
        )
        pages_policy.label().setFixedWidth(label_width)
        pages_policy.target().setFixedWidth(target_width)

        printing_pages_policies_keys = list(printing_pages_policies.keys())

        # noinspection PyUnresolvedReferences
        pages_policy.target().currentIndexChanged.connect(lambda x: pages.setVisible(
            printing_pages_policies_keys[x] == PrintingPagePolicy.Custom.value
        ))

        # PAGES
        pages = self.__controls.create_line_edit(self.PARAMETER_PAGES, "")
        pages.set_description(self.__clc(self.PARAMETER_PAGES, "description"))
        pages.pattern_set(
            "cups_format", Patterns.PRINTING_PAGE_PATTERN, self.__clc(self.PARAMETER_PAGES, "cups_format_error")
        )
        pages.pattern_enable("cups_format")
        pages.label().setFixedWidth(label_width)
        pages.target().setFixedWidth(target_width)
        pages.setVisible(self.__doc.pages_policy == PrintingPagePolicy.Custom.value)
        pages.set_grid_items([
            ["title", "spacing|10|horizontal", "widget", "stretch|horizontal"],
            ["", "", "description", ""],
            ["", "", "errorWidget", ""],
        ])

        # MIRROR
        self.__controls.create_check_box(self.PARAMETER_MIRROR, self.__clc(self.PARAMETER_MIRROR, "title"))

        # LANDSCAPE
        self.__controls.create_check_box(self.PARAMETER_LANDSCAPE, self.__clc(self.PARAMETER_LANDSCAPE, "title"))

        # TRANSPARENCY
        self.__controls.create_check_box(self.PARAMETER_TRANSPARENCY, self.__clc(self.PARAMETER_TRANSPARENCY, "title"))

        # SEND CONVERTED
        send_converted = self.__controls.create_check_box(
            self.PARAMETER_SEND_CONVERTED,
            self.__clc(self.PARAMETER_SEND_CONVERTED, "title")
        )
        send_converted.setEnabled(bool(self.__tmp_path))
        send_converted.setHidden(self.__mime_type == MimeType.PDF)
