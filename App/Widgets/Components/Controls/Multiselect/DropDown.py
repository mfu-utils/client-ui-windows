from typing import Dict, List, Optional

from PySide6.QtCore import Signal, Qt, QEvent, QObject
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QScrollArea, QApplication

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import styles, config, platform


class DropDown(DrawableWidget):
    selected = Signal(str)

    item_height = 24
    padding = 10
    spacing = 1

    def __init__(self, parent: QWidget = None):
        super(DrawableWidget, self).__init__(parent)
        self.setObjectName("MultiselectControlDropDown")
        self.setStyleSheet(styles(["multiselectControlDropDown", "scrollBar"]))

        self.__return_focus_widget: Optional[QWidget] = None
        self.__fixed_max_height: Optional[int] = None
        self.__min_width = 100

        self.__items: List[QPushButton] = []
        self.__indexes: Dict[int, str] = {}
        self.__focus_index: Optional[int] = None

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)

        self.__scroll_area = UIHelpers.create_scroll(self, 'MultiselectScrollArea')
        self.__scroll_area.setContentsMargins(0, 0, 0, 0)
        self.__scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.__scroll_area_widget = QWidget(self.__scroll_area)
        self.__scroll_area_widget.setContentsMargins(0, 0, 0, 0)
        self.__scroll_area_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.__scroll_area_widget.setObjectName('MultiselectList')

        self._list_layout = UIHelpers.v_layout(
            (self.padding, self.padding, self.padding + 5, self.padding),
            spacing=self.spacing
        )

        self.__scroll_area_widget.setLayout(self._list_layout)
        self.__scroll_area.setWidget(self.__scroll_area_widget)
        self.__central_layout.addWidget(self.__scroll_area)

        self.setLayout(self.__central_layout)

        UIHelpers.create_shadow(self, 20 if platform().is_windows() else 0, 0, config('ui.shadow-offset'))

        self.installEventFilter(self)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def set_height_restriction(self, height: int):
        self.__fixed_max_height = height

    def disable_height_restriction(self):
        self.__fixed_max_height = None

    def set_return_focus_widget(self, widget: QWidget):
        self.__return_focus_widget = widget

    def hide(self):
        self.__drop_all_items()
        self.__focus_index = None

        super(DrawableWidget, self).hide()

    def __selected_signal(self, idx: int):
        self.selected.emit(self.__indexes[idx])
        self.hide()

    def __drop_all_items(self):
        while item := self._list_layout.takeAt(0):
            item.widget().deleteLater()

        self.__items = []
        self.__indexes = {}

    def __create_item(self, idx: int, key: str, name: str) -> QPushButton:
        button = QPushButton(name, self)
        button.setObjectName("MultiselectChooseListItem")
        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        button.clicked.connect(lambda: self.__selected_signal(idx))
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus | Qt.FocusPolicy.ClickFocus)
        button.setFixedHeight(self.item_height)
        button.installEventFilter(self)

        self.__indexes.update({idx: key})
        self._list_layout.addWidget(button)
        self.__items.append(button)

        button.adjustSize()

        return button

    def __un_focus_all(self):
        for button in self.__items:
            button.clearFocus()

    def __update_scroll_position(self):
        self.__scroll_area.verticalScrollBar().setValue(
            int(self.__items[self.__focus_index].pos().y() - self.__scroll_area.height() / 2 - self.item_height / 2)
        )

        UIHelpers.update_style(self)

    def next_focus_item(self):
        if len(self.__items) == 0:
            return

        if self.__focus_index is None or self.__focus_index == len(self.__items) - 1:
            self.__focus_index = 0
        else:
            self.__focus_index += 1

        self.__un_focus_all()
        self.__items[self.__focus_index].setFocus()
        self.__update_scroll_position()

    def prev_focus_item(self):
        if len(self.__items) == 0:
            return

        if self.__focus_index is None or self.__focus_index == 0:
            self.__focus_index = len(self.__items) - 1
        else:
            self.__focus_index -= 1

        self.__un_focus_all()
        self.__items[self.__focus_index].setFocus()
        self.__update_scroll_position()

    def update_list(self, value: List[str], items: Dict[str, str], _filter: Optional[str] = None):
        self.__drop_all_items()
        self.__fill_list(value, items, _filter)

    def __calc_fixed_size(self, cnt: int, width: int):
        width += self.padding * 2

        self.__scroll_area_widget.setFixedHeight(self.item_height * cnt + (cnt - 1) * self.spacing + self.padding * 2)

        if (self.__fixed_max_height is not None) and cnt > self.__fixed_max_height:
            cnt = self.__fixed_max_height
            width += 5

        self.setFixedHeight(self.item_height * cnt + (cnt - 1) * self.spacing + self.padding * 2)

        self.setFixedWidth(width if width > self.__min_width else self.__min_width)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.KeyPress:
            event: QKeyEvent

            if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                self.__selected_signal(self.__focus_index)

            if event.key() == Qt.Key.Key_Escape:
                self.hide()

                if self.__return_focus_widget:
                    self.__return_focus_widget.setFocus()

            if event.key() == Qt.Key.Key_Down:
                self.next_focus_item()

            if event.key() == Qt.Key.Key_Up:
                self.prev_focus_item()

            return True

        if event.type() == QEvent.Type.FocusOut and QApplication.focusWidget():
            if QApplication.focusWidget().objectName() != 'MultiselectChooseListItem':
                self.hide()

        return super(DrawableWidget, self).eventFilter(watched, event)

    def __fill_list(self, value: List[str], items: Dict[str, str], _filter: Optional[str] = None):
        cnt = 0
        width = 0

        for key, item in items.items():
            if key in value:
                continue

            if _filter and _filter.lower() not in item.lower():
                continue

            item = self.__create_item(cnt, key, item)
            width = item.width() if item.width() > width else width

            cnt += 1

        if cnt == 0:
            self.hide()
            return

        self.__calc_fixed_size(cnt, width)
        self.show()
        self.raise_()
