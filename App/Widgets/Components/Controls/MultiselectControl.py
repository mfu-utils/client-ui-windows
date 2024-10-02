import json
from typing import Optional, List, Dict, Callable

from PySide6.QtCore import QPoint, QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QSizePolicy, QLineEdit, QPushButton, QApplication

from App.Widgets.Components.Controls.AbstractControlItem import AbstractControlItem
from App.Widgets.Components.Controls.Multiselect.Item import Item
from App.Widgets.Components.Controls.Multiselect.DropDown import DropDown
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import icon


class MultiselectControl(AbstractControlItem):
    def __init__(
        self,
        parent: QWidget,
        title: str,
        items: Dict[str, str],
        value: Optional[List[str]] = None,
        callback: Optional[callable] = None,
    ):
        self.__items = items

        self.__items_widgets: Dict[str, Item] = {}

        self.__creation_items_enable = False

        if isinstance(value, str) and len(value) > 0:
            value = json.loads(value)

        super(MultiselectControl, self).__init__(parent, title, value or [], callback)

        self.__drop_down = DropDown(self.parentWidget())
        self.__drop_down.selected.connect(self.__append_item)
        self.__drop_down.hide()

        self.__drop_down.set_return_focus_widget(self.__line_edit)

        self.__create_button.setHidden(True)

        self.__key_new_callback: Callable[[str], str] = lambda x: x

    def set_creation_items_enable(self, enable: bool):
        self.__create_button.setVisible(enable)
        self.__creation_items_enable = enable

    def set_key_new_callback(self, callback: Callable[[str], str]):
        self.__key_new_callback = callback

    def set_height_restriction(self, height: int):
        self.__drop_down.set_height_restriction(height)

    def disable_height_restriction(self):
        self.__drop_down.disable_height_restriction()

    def __get_modal_pos(self) -> QPoint:
        pos = self.parentWidget().pos() + self.pos() + self._widget.pos()
        pos.setY(pos.y() + self.__line_edit.height() + 5)

        return pos

    def __find(self, text: str = None):
        self.__drop_down.move(self.__get_modal_pos())
        self.__drop_down.update_list(self._new_value, self.__items, text)

    def __edit(self):
        self._check_prev_value()

        if self._callback:
            self._callback(json.dumps(self._new_value))

    def __new_item(self):
        value = self.__line_edit.text()

        if not value:
            return

        for key, val in self.__items.items():
            if value == val:
                self.__append_item(key)
                return

        # self.__line_edit.clear()
        key = self.__key_new_callback(value)

        self.__items.update({key: value})
        self._new_value.append(value)

        self.__add_item(key, value)
        self.__edit()

    def __append_item(self, key: str):
        text = self.__items[key]
        self._new_value.append(key)

        self.__add_item(key, text)
        self.__edit()

        self.__line_edit.setFocus()

    def __delete_item(self, key: str):
        item = self.__items_widgets[key]
        item.hide()
        item.deleteLater()

        self._new_value.pop(self._new_value.index(key))
        self.__items_widgets.pop(key)
        self.__edit()

    def __add_item(self, key: str, value: str) -> Item:
        item = Item(key, value, self)
        item.deleted.connect(lambda: self.__delete_item(key))
        self.__items_widgets.update({key: item})

        self.__content_layout.addWidget(item)
        self._widget.adjustSize()

        return item

    def hideEvent(self, event):
        self.__drop_down.hide()
        super(MultiselectControl, self).hideEvent(event)

    def _init_widget(self):
        self._widget = QWidget(self)
        self._widget.setObjectName("MultiselectControl")
        self._widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

        self.__widget_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)

        self.__controls_layout = UIHelpers.h_layout((4, 4, 4, 4), 2)

        self.__line_edit = QLineEdit(self)
        self.__line_edit.setObjectName("MultiselectLineEdit")
        self.__line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.__line_edit.textChanged.connect(self.__find)
        self.__line_edit.setFixedHeight(25)
        self.__line_edit.installEventFilter(self)
        self.__controls_layout.addWidget(self.__line_edit)

        self.__create_button = QPushButton(self)
        self.__create_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.__create_button.setObjectName("MultiselectCreateButton")
        self.__create_button.setIcon(icon("plus.png"))
        self.__create_button.setFixedSize(30, 25)
        self.__create_button.clicked.connect(self.__new_item)
        self.__controls_layout.addWidget(self.__create_button)

        self.__widget_layout.addLayout(self.__controls_layout)

        self.__content_layout = UIHelpers.v_layout((5, 5, 5, 5), 0)

        for key, value in self.__items.items():
            if key in self._value:
                self.__add_item(key, value)

        self.__widget_layout.addLayout(self.__content_layout)

        self._widget.setLayout(self.__widget_layout)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.__line_edit:
            if event.type() == QEvent.Type.KeyPress:
                event: QKeyEvent

                if event.key() == Qt.Key.Key_Return and self.__creation_items_enable:
                    self.__new_item()
                    return True

                if event.key() == Qt.Key.Key_Down:
                    if self.__drop_down.isHidden():
                        self.__find()

                    self.__drop_down.next_focus_item()
                    return True

                if event.key() == Qt.Key.Key_Up:
                    if self.__drop_down.isHidden():
                        self.__find()

                    self.__drop_down.prev_focus_item()
                    return True

                if self.__drop_down.isVisible() and event.key() == Qt.Key.Key_Escape:
                    self.__drop_down.hide()
                    return True

            if event.type() == QEvent.Type.FocusOut and QApplication.focusWidget():
                if QApplication.focusWidget().objectName() != 'MultiselectChooseListItem':
                    self.__drop_down.hide()

            if event.type() == QEvent.Type.MouseButtonPress:
                if self.__drop_down.isHidden():
                    self.__find()

        return super(MultiselectControl, self).eventFilter(watched, event)

    def _register_callback(self):
        pass

    def _get_style_sheet(self) -> dict:
        return {
            "styles": ["abstractControlItem", "multiselectControl", "contextMenu"],
        }

    def _grid(self) -> List[List[str]]:
        return [
            ["title"],
            ["spacing|5|vertical"],
            ["widget"],
            ["description"],
        ]
