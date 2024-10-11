from typing import Dict, Optional, Any

from PySide6.QtWidgets import QWidget, QPushButton

from App.Widgets.Components.PreferencesControls import PreferencesControls
from App.Widgets.Components.Preferences.PreferencesSideBar import PreferencesSideBar
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import ini, lc, styles


class AbstractSettingsModal(AbstractModal):
    BUTTON_ROLE_OK = 1
    BUTTON_ROLE_CANCEL = 2
    BUTTON_ROLE_APPLY = 3

    BUTTON_ROLES = [
        BUTTON_ROLE_OK,
        BUTTON_ROLE_CANCEL,
        BUTTON_ROLE_APPLY,
    ]

    def __init__(self, parent: QWidget = None):
        super(AbstractSettingsModal, self).__init__(parent)
        self.setObjectName('AbstractSettingsModal')

        self._new_settings = {}
        self.__roles_buttons: Dict[int, QPushButton] = {}

        self._controls_tabs: Dict[str, PreferencesControls] = {}
        self.__sidebar_widget = PreferencesSideBar(self)

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)
        self.__content_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        self.__content_layout.addWidget(self.__sidebar_widget)

        self.controls()

        for tab in self._controls_tabs.values():
            tab.generate()

        self.__sidebar_widget.generate()

        self.__central_layout.addLayout(self.__content_layout)

        self.__buttons_layout = UIHelpers.h_layout((10, 10, 10, 10), 10)
        self.__buttons_layout.addStretch()

        self.buttons()

        self.__central_layout.addLayout(self.__buttons_layout)

        self.centralWidget().setLayout(self.__central_layout)
        self.centralWidget().adjustSize()

        self._settings = self._new_settings.copy()

        self.__can_apply = None

        self.show()

    def __update_setting(self, key: str, value):
        self._new_settings[key] = value
        self.__change_can_apply()

    def __hide_tabs(self):
        for control in self._controls_tabs.values():
            control.hide()

    def checkout_tab(self, key: str):
        self.__hide_tabs()
        self._controls_tabs[key].show()
        self.__sidebar_widget.enable(key)

    def _do_ok(self):
        self._do_apply()

        self.close()

    def _do_apply(self):
        if not self.__can_apply:
            return

        for key, value in self._new_settings.items():
            ini(key, value)

        ini().write()

        self._settings = self._new_settings.copy()
        self.__change_can_apply()

    def __change_can_apply(self):
        apply_button = self.__roles_buttons.get(self.BUTTON_ROLE_APPLY)

        if not apply_button:
            return

        self.__can_apply = self._settings != self._new_settings

        if self.__can_apply:
            for tab in self._controls_tabs.values():
                if not tab.completed():
                    self.__can_apply = False
                    break

        apply_button.setEnabled(self.__can_apply)

    def _get_value(self, key: str) -> Any:
        return ini(key)

    def _create_button(self, name: str, title: str, role: Optional[int] = None) -> QPushButton:
        button = QPushButton(title)
        button.setObjectName(name)
        button.setStyleSheet(styles('modalButton'))
        button.setFixedHeight(30)
        button.setMinimumWidth(70)

        self.__buttons_layout.addWidget(button)

        if role not in self.BUTTON_ROLES:
            raise Exception('Role must be one of: ' + ', '.join(map(str, self.BUTTON_ROLES)))

        if role:
            self.__roles_buttons[role] = button

        return button

    def _add_cancel_button(self, title: str) -> QPushButton:
        return self._create_button('SettingModalButtonCancel', title, self.BUTTON_ROLE_CANCEL)

    def _add_ok_button(self, title: str) -> QPushButton:
        return self._create_button('SettingModalButtonOk', title, self.BUTTON_ROLE_OK)

    def _add_apply_button(self, title: str) -> QPushButton:
        return self._create_button('SettingModalButtonApply', title, self.BUTTON_ROLE_APPLY)

    def _create_tab(self, key: str, tab_name: str) -> PreferencesControls:
        tab = PreferencesControls(tab_name, self)
        tab.add_get_value_callback(self._get_value)
        tab.add_set_value_callback(self.__update_setting)
        tab.setStyleSheet(tab.styleSheet() + styles("preferencesControlsContainer"))

        self.__content_layout.addWidget(tab)
        self.__hide_tabs()
        self._controls_tabs[key] = tab

        self.__sidebar_widget.create_item(key, tab_name, lambda: self.checkout_tab(key))

        return tab

    def controls(self):
        raise NotImplementedError()

    def buttons(self):
        ok = self._add_ok_button(lc("settingsModal.buttons.ok"))
        ok.clicked.connect(self._do_ok)

        cancel = self._add_cancel_button(lc("settingsModal.buttons.cancel"))
        cancel.clicked.connect(self._do_cancel)

        apply = self._add_apply_button(lc("settingsModal.buttons.apply"))
        apply.setEnabled(False)
        apply.clicked.connect(self._do_apply)
