from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QPushButton

from App.Core.Utils import MimeType
from App.Core.Utils.OfficeSuite import OfficeSuite
from App.Services.MimeConvertor import MimeConvertor
from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.Components.LoadingAnimation import LoadingAnimation
from App.DTO.Client import PrintingDocumentDTO
from App.Widgets.Modals.PrintingFileParametersModal import PrintingFileParametersModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import icon, mime_convertor, ini, styles, in_thread, lc, logger


class PrintingFileItem(DrawableWidget):
    converting_stopped = Signal()
    deleted = Signal()

    PARAMETER_TYPE_ERROR = "type_error"
    PARAMETER_PATH = "path"
    PARAMETER_MIME = "mime"
    PARAMETER_TYPE = "type"
    PARAMETER_SEND_CONVERTED = "send_converted"

    printing_doc = PrintingDocumentDTO()

    def __init__(self, parameters: dict, parent: QWidget = None):
        super(PrintingFileItem, self).__init__(parent)
        self.setObjectName('PrintingFileItem')

        self.printing_doc.send_converted = parameters[self.PARAMETER_SEND_CONVERTED]

        self.__parameters = parameters
        self.__devices = {}
        self.__converted_path: Optional[str] = self.__parameters[self.PARAMETER_PATH][:]

        self.__type_error = parameters.get(self.PARAMETER_TYPE_ERROR) or False
        self.__has_error = bool(self.__type_error)

        self.__need_converting = False

        if (not self.__type_error) and (ini('printing.view_tool') in MimeConvertor.suites_values(False)):
            self.__need_converting = True

        self.__central_layout = UIHelpers.h_layout((10, 3, 10, 3), 5)

        self.__content_layout = UIHelpers.v_layout((0, 0, 0, 0), 5)

        self.__title = QLabel(parameters[self.PARAMETER_PATH], self)
        self.__title.setObjectName('PrintingFileItemTitle')

        if self.__has_error:
            self.__title.setDisabled(True)

        self.__content_layout.addWidget(self.__title)

        self.__parameters_layout = UIHelpers.h_layout((0, 0, 0, 0), 2)

        if self.__has_error:
            self.__error_type_icon = UIHelpers.image("error_sign_16x16@2x.png")
            self.__error_type_icon.setObjectName("PrintingFileItemErrorTypeIcon")
            self.__error_type_icon.setDisabled(True)
            self.__parameters_layout.addWidget(self.__error_type_icon)

            self.__parameters_layout.addSpacing(5)

            self.__error_type_message = QLabel(parameters[self.PARAMETER_TYPE_ERROR], self)
            self.__error_type_message.setObjectName("PrintingFileItemErrorTypeMessage")
            self.__error_type_message.setDisabled(True)
            self.__parameters_layout.addWidget(self.__error_type_message)
            self.__loading_block = None
        else:
            self.__loading_block = self.__create_loading_block()
            self.__parameters_layout.addWidget(self.__loading_block)

            self.__mime_widget = QLabel(parameters[self.PARAMETER_TYPE], self)
            self.__mime_widget.setObjectName('PrintingFileItemMime')
            self.__parameters_layout.addWidget(self.__mime_widget)

        self.__parameters_layout.addStretch()

        self.__content_layout.addLayout(self.__parameters_layout)
        self.__central_layout.addLayout(self.__content_layout)
        self.__central_layout.addStretch()

        if not self.__has_error:
            self.__parameters_button = self.__create_button(
                "PrintingFileItemParametersButton", "gear.png", self.__open_parameters_modal
            )
            self.__central_layout.addWidget(self.__parameters_button)

        self.__delete_button = self.__create_button("PrintingFileItemDeleteButton", "bin.png", self.deleteLater)
        self.__central_layout.addWidget(self.__delete_button)

        self.setLayout(self.__central_layout)

        self.enable_warning(self.__has_error)

        if not self.__has_error:
            self.setDisabled(True)

            if self.__need_converting:
                self.__start_converting()

            UIHelpers.update_style(self)

        self.__must_be_enabled = True
        self.__enabling_lock = self.__need_converting
        self.__ready_to_print = not self.__has_error

    def enable_warning(self, enable: bool):
        self.setProperty("warning", enable)
        UIHelpers.update_style(self)

    def get_path(self) -> str:
        return self.__parameters[self.PARAMETER_PATH][:]

    def get_converted_path(self) -> Optional[str]:
        return self.__converted_path

    def get_ready_to_print(self) -> bool:
        return self.__ready_to_print

    def set_enabled(self, enable: bool):
        if not self.__enabling_lock:
            self.__set_parameters_button_enabled(enable)

        self.__must_be_enabled = enable

    def get_need_converting(self) -> bool:
        return self.__need_converting

    def set_devices(self, devices: dict):
        self.__devices = devices

        if len(self.__devices) > 0:
            self.printing_doc.device = list(self.__devices.keys())[0]

    def get_mime(self) -> MimeType:
        return self.__parameters[self.PARAMETER_MIME]

    def __create_loading_block(self) -> QWidget:
        widget = DrawableWidget(self)
        widget.setStyleSheet(styles("printingLoading"))

        layout = UIHelpers.h_layout((0, 0, 10, 0), 5)

        animation = LoadingAnimation((16, 16), (4, 4), widget)
        layout.addWidget(animation)

        layout.setSpacing(5)

        label = QLabel(self)
        label.setObjectName("PrintingFileItemLoadingText")
        label.setText(lc("printingFileParametersModal.prepare_file"))
        layout.addWidget(label)

        widget.setLayout(layout)

        return widget

    def __open_parameters_modal(self):
        path = self.__parameters[self.PARAMETER_PATH]

        modal = PrintingFileParametersModal(
            path,
            self.__converted_path,
            self.__parameters[self.PARAMETER_MIME],
            self.__devices,
            self.printing_doc,
            self
        )

        def save(data: PrintingDocumentDTO):
            self.printing_doc = data
            logger().debug(f"Saved parameters ({path}) {self.printing_doc.as_dict()}")

        modal.saved.connect(save)

    def path(self) -> str:
        return self.__parameters[self.PARAMETER_PATH]

    def error(self) -> bool:
        return bool(self.__parameters[self.PARAMETER_TYPE_ERROR])

    def __create_button(self, name: str, _icon: str, callback: callable = None) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(30, 30)
        button.setObjectName(name)
        button.setIcon(icon(_icon))

        if callback:
            button.clicked.connect(callback)

        return button

    def __set_parameters_button_enabled(self, enable: bool):
        if not self.__type_error:
            self.__parameters_button.setEnabled(enable)

    def __start_converting(self):
        self.__ready_to_print = False

        def _worker():
            suite = OfficeSuite(ini("printing.view_tool"))

            self.__converted_path = mime_convertor().get_pdf(self.__parameters[self.PARAMETER_PATH], suite)

            if self.__converted_path:
                self.__ready_to_print = True

            self.setEnabled(True)

            self.__set_parameters_button_enabled(self.__must_be_enabled)

            self.__loading_block.deleteLater()

            self.converting_stopped.emit()

            UIHelpers.update_style(self)

            self.__enabling_lock = False

        in_thread(_worker)

    def deleteLater(self):
        super().deleteLater()
        self.deleted.emit()
