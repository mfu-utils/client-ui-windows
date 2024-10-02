from typing import Any

from PySide6.QtWidgets import QWidget

from App.Core.Utils.OfficeSuite import OfficeSuite
from App.Core.Utils.Ui import Patterns, Casts
from App.Services.Client.Ui.UiDocConvertorService import UiDocConvertorService
from App.Services.Client.Ui.UiScanService import UiScanService
from App.Services.MimeConvertor import MimeConvertor
from App.Widgets.Components.Controls.CheckBoxControl import CheckBoxControl
from App.Widgets.Modals.AbstractSettingsModal import AbstractSettingsModal
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import lc, ini, config, platform


class PreferencesModal(AbstractSettingsModal):
    def __init__(self, parent: QWidget = None):
        self._convertor_service = UiDocConvertorService.convertor()

        super(PreferencesModal, self).__init__(parent)

        self.resize(800, 500)

        self.setWindowTitle(lc("preferencesModal.title"))
        self.setObjectName("PreferencesModal")

        UIHelpers.to_center(self, UIHelpers.find_parent_recursive(self, 'MainWindow'))

        self._disable_all_parents()

    def _get_value(self, key: str) -> Any:
        _dir = ini('scans.dir')

        if key == "scans.dir":
            return UiScanService.get_scan_dir(_dir)

        if key == "recognition.dir":
            return self._convertor_service.get_doc_dir()

        if key == "printing.view_tool":
            if (suite := super(PreferencesModal, self)._get_value(key)) not in MimeConvertor.suites_values():
                return OfficeSuite.NONE.value

            return suite

        return super(PreferencesModal, self)._get_value(key)

    @staticmethod
    def __dir_pattern() -> str:
        return Patterns.DIRECTORY_WINDOWS if platform().is_windows() else Patterns.DIRECTORY_NON_WINDOWS

    @staticmethod
    def __lc(name: str):
        return lc(f"preferencesModal.{name}")

    @staticmethod
    def net_lc(name: str) -> str:
        return PreferencesModal.__lc(f"network.{name}")

    @staticmethod
    def ocr_lc(name: str) -> str:
        return PreferencesModal.__lc(f"ocr.{name}")

    @staticmethod
    def devices_lc(name: str) -> str:
        return PreferencesModal.__lc(f"devices.{name}")

    @staticmethod
    def app_lc(name: str) -> str:
        return PreferencesModal.__lc(f"appearance.{name}")

    @staticmethod
    def rec_lc(name: str) -> str:
        return PreferencesModal.__lc(f"recognition.{name}")

    @staticmethod
    def scans_lc(name: str) -> str:
        return PreferencesModal.__lc(f"scans.{name}")

    @staticmethod
    def printing_lc(name: str) -> str:
        return PreferencesModal.__lc(f"printing.{name}")

    def app_tab(self):
        tab = self._create_tab('app', self.app_lc('title'))

        on_start = tab.create_check_box('app.show_on_start', self.app_lc('show_on_start.title'))
        on_start.set_description(self.app_lc('show_on_start.description'))
        on_start.set_grid_items([
            ['widget', 'spacing|10|horizontal', 'title', 'stretch|horizontal'],
            ['', '', 'description']
        ])

        tab.create_combo_box('app.lang', self.app_lc('lang.title'), config('langs'))

    def network_tab(self):
        tab = self._create_tab('net', self.net_lc('title'))
        labels_width = 60

        address = tab.create_line_edit('network.address', self.net_lc("address.title"))
        address.pattern_set('ip', Patterns.IP, self.net_lc("address.pattern_error"))
        address.pattern_enable('ip')
        address.set_description(self.net_lc("address.description"))
        address.label().setFixedWidth(labels_width)

        port = tab.create_spinbox('network.port', self.net_lc("port.title"), (0, 99999))
        port.target().setFixedWidth(90)
        port.label().setFixedWidth(labels_width)
        port.set_description(self.net_lc("port.description"))

        timeout = tab.create_spinbox('network.timeout', self.net_lc("timeout.title"), (0, 180))
        timeout.target().setFixedWidth(90)
        timeout.label().setFixedWidth(labels_width)
        timeout.set_description(self.net_lc("timeout.description"))

    def devices_tab(self):
        tab = self._create_tab("devices", self.devices_lc("title"))

        device_choose = tab.create_check_box("devices.auto_choose_device", self.devices_lc("device_choose.title"))
        device_choose.set_description(self.devices_lc("device_choose.description"))
        device_choose.set_grid_items([
            ["widget", "spacing|10|horizontal", "title", "stretch|horizontal"],
            ["", "", "setup|default"],
        ])

    def recognition_tab(self):
        tab = self._create_tab("recognition", self.rec_lc("title"))

        langs = tab.create_multiselect(
            "recognition.default_langs", self.rec_lc("default_langs.title"), self._convertor_service.langs()
        )
        langs.set_height_restriction(10)
        langs.set_description(self.rec_lc("default_langs.description"))

        save_dir = tab.create_line_edit("recognition.dir", self.rec_lc("save_dir.title"))

        description = self.rec_lc("save_dir.description")

        if not platform().is_windows():
            description = description.replace("\\", "/")

        save_dir.set_description(description)
        save_dir.pattern_set('dir', self.__dir_pattern(), self.rec_lc('save_dir.pattern_error'))
        save_dir.pattern_enable('dir')

    def ocr_tab(self):
        tab = self._create_tab("ocr", self.ocr_lc("title"))
        labels_width = 85
        enabled = ini("ocr.enable", bool)

        path_to_executable = None
        parameters = None
        langs_del = None

        def change_states(x):
            path_to_executable.setEnabled(x)
            parameters.setEnabled(x)
            langs_del.setEnabled(x)

            if x:
                path_to_executable.pattern_enable("exec")
            else:
                path_to_executable.pattern_disable()

            path_to_executable.verify()

        def post_creation_callback(x: CheckBoxControl):
            # noinspection PyUnresolvedReferences
            x.target().stateChanged.connect(change_states)

        enable = tab.create_check_box("ocr.enable", self.ocr_lc("enable.title"), post_creation_callback)
        enable.set_description(self.ocr_lc("enable.description"))

        path_to_executable = tab.create_line_edit("ocr.path_to_executable", self.ocr_lc("path.title"))
        path_to_executable.set_description(self.ocr_lc('path.description'))
        path_to_executable.pattern_set("exec", r"^(/[\w-]+)+$", self.ocr_lc("path.pattern_error"))
        path_to_executable.label().setFixedWidth(labels_width)
        path_to_executable.setEnabled(enabled)

        parameters = tab.create_line_edit("ocr.parameters", self.ocr_lc("parameters.title"))
        parameters.set_description(self.ocr_lc('parameters.description'))
        parameters.label().setFixedWidth(labels_width)
        parameters.pattern_set("params", r"^$|^[^%]+$", self.ocr_lc("parameters.pattern_error"))
        parameters.setEnabled(enabled)

        langs_del = tab.create_line_edit("ocr.langs_delimiter", self.ocr_lc('langs_delimiter.title'))
        langs_del.set_description(self.ocr_lc("langs_delimiter.description") % self._convertor_service.SPACE_DELIMITER)
        langs_del.label().setFixedWidth(labels_width)
        langs_del.setEnabled(enabled)

    def scans_tab(self):
        tab = self._create_tab("scans", self.scans_lc("title"))

        _dir = tab.create_line_edit("scans.dir", self.scans_lc("dir.title"))
        _dir.set_description(self.scans_lc("dir.description"))
        _dir.pattern_set("dir", self.__dir_pattern(), self.scans_lc("dir.pattern_error"))
        _dir.pattern_enable("dir")

    def printing_tab(self):
        tab = self._create_tab("printing", self.printing_lc("title"))

        view_tool = tab.create_combo_box(
            "printing.view_tool",
            self.printing_lc("view_tool.title"),
            Casts.enum2dict(MimeConvertor.suites(), {
                OfficeSuite.NONE.value: self.printing_lc("view_tool.none_item"),
                **MimeConvertor.OFFICE_SUITE_NAMES
            })
        )
        view_tool.set_description(self.printing_lc("view_tool.description"))
        view_tool.set_grid_items([
            ["title", "stretch|horizontal"],
            ["spacing|10|vertical"],
            ["widget"],
            ["description"],
        ])
        
        tab.create_check_box(
            "printing.send_converted_icons_by_default",
            self.printing_lc("send_converted_icons_by_default.title"),
        )

        tab.create_check_box(
            "printing.send_converted_docs_by_default",
            self.printing_lc("send_converted_docs_by_default.title"),
        )

    def controls(self):
        self.app_tab()
        self.network_tab()
        self.devices_tab()
        self.ocr_tab()
        self.recognition_tab()
        self.scans_tab()
        self.printing_tab()

        self.checkout_tab("app")
