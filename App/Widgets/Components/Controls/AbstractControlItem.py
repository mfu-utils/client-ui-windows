import copy
from typing import List, Any, Optional, Dict, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout

from App.Core.Utils.Str import Str
from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import cache, styles, config
from hashlib import md5

import json


class AbstractControlItem(DrawableWidget):
    def __init__(self, parent: QWidget, title: str, value: Any, callback: Optional[callable] = None):
        super(AbstractControlItem, self).__init__(parent)
        self.setObjectName("AbstractControlItem")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._widget: Optional[QWidget] = None

        self._title_widget = QLabel(title, self)
        self._title_widget.setObjectName("AbstractControlItemLabel")
        self._title_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._error_widget: Optional[QLabel] = None

        self._error_messages = {}
        self._current_error: Optional[str] = None

        self._indent = 0
        self._value = copy.deepcopy(value)
        self._new_value = copy.deepcopy(value)
        self._callback = callback
        self._check_prev_value_enabled = True

        self._setups_layouts: Dict[str, Dict[str, Union[List[str], str]]] = self._setups()
        self._grid_layout = UIHelpers.g_layout((10, 0, 0, 0), 0)
        self._grid_items = self._grid()

        self.__description_widget: Optional[QLabel] = None
        self.__description: Optional[str] = None

        self._init_widget()
        self.__cache_styles = not config('ui.non-cache-styles-for-debug')

    def _register_callback(self):
        pass

    def set_checking_prev_value_enabled(self, enabled: bool):
        self._check_prev_value_enabled = enabled

    def __create_description_widget(self) -> QLabel:
        self.__description_widget = QLabel(self.__description, self)
        self.__description_widget.setContentsMargins(0, 5, 0, 0)
        self.__description_widget.setObjectName("AbstractControlItemDescription")

        return self.__description_widget

    def set_description(self, description: str):
        self.__description = description

    def __create_error_widget(self) -> QLabel:
        self._error_widget = QLabel(self)
        self._error_widget.setObjectName("AbstractControlItemError")
        self._error_widget.hide()

        return self._error_widget

    def target(self) -> QWidget:
        return self._widget

    def label(self) -> QLabel:
        return self._title_widget

    def error_add(self, key: str, message: str):
        self._error_messages[key] = message

    def error_enable(self, message_key: Optional[str]):
        if self._current_error == message_key:
            return

        if enable := bool(message_key):
            self._error_widget.setText(self._error_messages[message_key])

        self._error_widget.setHidden(not enable)

        self._widget.setProperty('danger', enable)
        self._current_error = message_key

        UIHelpers.update_style(self._widget)

    def error_disable(self):
        self.error_enable(None)

    def _check_prev_value(self):
        if not self._check_prev_value_enabled:
            return

        enable = self._value != self._new_value

        self._set_primary_enabled(enable)

    def _set_primary_enabled(self, enable: bool):
        self._widget.setProperty('primary', enable)
        UIHelpers.update_style(self._widget)

        if self._title_widget:
            self._title_widget.setProperty('primary', enable)
            UIHelpers.update_style(self._title_widget)

    # noinspection PyMethodMayBeStatic
    def __create_style(self, params: dict) -> str:
        style = styles(params['styles'])

        if replaces := params.get('replaces'):
            style = Str.replace_templated(style, replaces)

        return style

    def __resolve_style_sheet(self) -> str:
        params = self._get_style_sheet()

        if not self.__cache_styles:
            return self.__create_style(params)

        _cache = cache()

        key = md5(json.dumps(params).encode()).hexdigest()

        if not cache().has(key):
            cache().set(key, self.__create_style(params))

        return cache().get(key)

    def generate(self):
        self._register_callback()
        self._widget.setContentsMargins(0, 0, 0, 0)
        self._widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.__fill_grid()

        self.setLayout(self._grid_layout)

        self.setStyleSheet(self.__resolve_style_sheet())

        self.verify()

    def completed(self):
        return not self._current_error

    def verify(self):
        pass

    def __fill_grid(self):
        for i, row in enumerate(self._grid_items):
            for j, item in enumerate(row):
                parameters = item.split('|')

                _type = parameters[0]

                if _type == '':
                    continue

                if _type == 'widget':
                    self._grid_layout.addWidget(self._widget, i, j)

                if _type == 'title':
                    self._grid_layout.addWidget(self._title_widget, i, j)

                if _type == 'label':
                    self._grid_layout.addWidget(QLabel(parameters[1], self), i, j)

                if _type == 'errorWidget':
                    self._grid_layout.addWidget(self.__create_error_widget(), i, j)

                if _type == 'setup':
                    self._grid_layout.addLayout(self.__fill_layout(parameters[1]), i, j)

                if _type == 'description' and self.__description:
                    self._grid_layout.addWidget(self.__create_description_widget(), i, j)

                if _type == 'spacing':
                    self._grid_layout.addLayout(UIHelpers.spacing_for_grid(int(parameters[1]), parameters[2]), i, j)

                if _type == 'stretch':
                    self._grid_layout.addLayout(UIHelpers.stretch_for_grid(parameters[1]), i, j)

    def __fill_layout(self, name) -> QHBoxLayout:
        setup = self._setups()[name]

        layout = UIHelpers.layout_for_grid(setup['direction'])

        for item in setup['layout']:
            parameters = item.split('|')

            _type = parameters[0]

            if _type == 'indent':
                layout.addSpacing(self._indent)

            if _type == 'widget':
                layout.addWidget(self._widget)

            if _type == 'title':
                layout.addWidget(self._title_widget)

            if _type == 'stretch':
                layout.addStretch()

            if _type == 'spacing':
                layout.addSpacing(int(parameters[1]))

            if _type == 'label':
                layout.addWidget(QLabel(parameters[1], self))

            if _type == 'description' and self.__description:
                layout.addWidget(self.__create_description_widget())

        return layout

    def _init_widget(self):
        raise NotImplementedError()

    def _get_style_sheet(self) -> dict:
        return {}

    # noinspection PyMethodMayBeStatic
    def _setups(self) -> Dict[str, Dict[str, Union[List[str], str]]]:
        return {}

    def set_grid_items(self, items: List[List[str]]):
        self._grid_items = items

    # noinspection PyMethodMayBeStatic
    def _grid(self) -> List[List[str]]:
        return [
            ["title", "spacing|10|horizontal", "widget"],
            ["", "", "description"],
            ["", "", "errorWidget"],
        ]
