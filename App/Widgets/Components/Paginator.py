from typing import Tuple

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QWidget

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import styles


class Paginator(DrawableWidget):
    changed = Signal(int)

    def __init__(self, total_pages: int, page: int = 1, parent: QWidget = None):
        super(Paginator, self).__init__(parent)
        self.setObjectName('Paginator')
        self.setStyleSheet(styles('paginator'))

        self.__start_range = 1
        self.__end_range = total_pages

        self.__current_page = (page or 1) if page < total_pages else self.__end_range

        self.__central_layout = UIHelpers.h_layout((0, 0, 0, 0), 2)

        self.__init_buttons()

        self.setLayout(self.__central_layout)

    def __create_button(self, i: int, name: str) -> QPushButton:
        btn = QPushButton(str(i), self)
        btn.setObjectName(name)
        btn.setFixedSize(30, 30)
        btn.clicked.connect(lambda: self.__clicked(i))
        btn.setProperty('primary', i == self.__current_page)

        UIHelpers.update_style(btn)

        self.__central_layout.addWidget(btn)

        return btn

    def __clicked(self, index: int):
        if index == self.__current_page:
            return

        self.__current_page = index

        self.__update_primary_page(index)

        self.changed.emit(index)

    def __clear_buttons(self):
        while itm := self.__central_layout.takeAt(0):
            itm.widget().deleteLater()

    def __init_buttons(self):
        i = self.__start_range

        while i <= self.__end_range:
            self.__create_button(i, 'PaginatorPageButton')
            i += 1

    def update_(self, total_pages: int, page: int):
        if self.__end_range == total_pages:
            self.__update_primary_page(page)
            return

        self.__update_page_set(total_pages, page)

    def __update_page_set(self, total_pages: int, page: int):
        self.__end_range = total_pages
        self.__current_page = (page or 1) if page < total_pages else self.__end_range

        self.__clear_buttons()
        self.__init_buttons()

    def __update_primary_page(self, page: int):
        i = 0

        while itm := self.__central_layout.itemAt(i):
            i += 1

            itm.widget().setProperty('primary', page == i)
            UIHelpers.update_style(itm.widget())

