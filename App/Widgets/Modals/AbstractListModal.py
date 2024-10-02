from typing import Any

from PySide6.QtCore import Qt, QEvent, QObject
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QScrollArea, QLineEdit, QPushButton, QSizePolicy, QLabel

from App.Widgets.Components.ListItem import ListItem
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import styles, icon, lc
from App.Widgets.Modals.ConfirmModal import ConfirmModal


class AbstractListModal(AbstractModal):
    def __init__(self, title: str, parent: QWidget = None):
        super(AbstractListModal, self).__init__(parent)
        self.setObjectName("ListContainer")
        self.setMinimumSize(300, 500)
        self.setWindowTitle(title)
        self.setStyleSheet(styles(["listContainer", "listItem", "contextMenu", "scrollBar"]))

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)

        self.__add_item_layout = UIHelpers.h_layout((10, 10, 10, 10), 5)

        self.__create_name_line_edit = QLineEdit(self)
        self.__create_name_line_edit.setFixedHeight(24)
        self.__create_name_line_edit.setObjectName("ListCreateNameLineEdit")
        self.__create_name_line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.__create_name_line_edit.textChanged.connect(self.drop_error)
        self.__add_item_layout.addWidget(self.__create_name_line_edit)

        self.__create_name_confirm_button = QPushButton(self)
        self.__create_name_confirm_button.setIcon(icon("plus.png"))
        self.__create_name_confirm_button.setObjectName("ListCreateNameConfirmButton")
        self.__create_name_confirm_button.setFixedSize(24, 24)
        self.__create_name_confirm_button.clicked.connect(self._save_new_item)

        self.__add_item_layout.addWidget(self.__create_name_confirm_button)

        self.__central_layout.addLayout(self.__add_item_layout)

        self.__error_widget = QLabel(self)
        self.__error_widget.setObjectName('ListErrorLabel')
        self.__error_widget.setHidden(True)
        self.__error_widget.setContentsMargins(10, 0, 10, 10)
        self.__central_layout.addWidget(self.__error_widget)

        self.__scroll_area = QScrollArea()
        self.__scroll_area.setObjectName('ListScrollArea')
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.__scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.__scroll_area_widget = QWidget(self.__scroll_area)
        self.__scroll_area_widget.setObjectName('List')

        self._list_layout = UIHelpers.v_layout((5, 5, 5, 5), 0)
        self._init_list()
        self._list_layout.addStretch()

        self.__scroll_area_widget.setLayout(self._list_layout)
        self.__scroll_area.setWidget(self.__scroll_area_widget)
        self.__central_layout.addWidget(self.__scroll_area)

        self.centralWidget().setLayout(self.__central_layout)
        self.centralWidget().adjustSize()

        self.installEventFilter(self)

        self.show()

        self._disable_all_parents()

        UIHelpers.to_center(self, UIHelpers.find_parent_recursive(self, "MainWindow"))

    def set_error(self, text: str):
        self.__error_widget.setText(text)
        self.__error_widget.setHidden(False)

    def drop_error(self):
        self.__error_widget.setHidden(True)
        self.__error_widget.setText("")

    def _on_delete(self, model: Any, text: str):
        pass

    def _on_rename(self, model: Any, text: str):
        pass

    def _on_create(self, text: str):
        pass

    def _do_ok(self):
        pass

    def _do_cancel(self):
        pass

    def __open_confirm_modal(self, list_item: ListItem):
        text = list_item.text()
        modal = ConfirmModal("ListContainer", f"«{text}»", lc("listModal.deleteModal.text"), self)
        modal.setMinimumWidth(500)
        modal.confirmed.connect(lambda: self._on_delete(list_item.model(), text))
        modal.confirmed.connect(list_item.deleteLater)

    def __changed_mod(self, list_item: ListItem, mode: ListItem.Mode):
        disabled = ListItem.Mode.EDIT == mode

        self.__error_widget.setDisabled(disabled)
        self.__create_name_line_edit.setDisabled(disabled)
        self.__create_name_confirm_button.setDisabled(disabled)

        for child in self.findChildren(ListItem):
            child.setDisabled(disabled)

        list_item.setDisabled(False)

    def __register_connects(self, list_item: ListItem):
        list_item.deleted.connect(lambda: self.__open_confirm_modal(list_item))
        list_item.changedName.connect(lambda new_name: self._on_rename(list_item.model(), new_name))
        list_item.changedMode.connect(lambda mode: self.__changed_mod(list_item, mode))

    def _save_new_item(self):
        text = self.__create_name_line_edit.text()
        self.__create_name_line_edit.clear()

        if not text:
            return

        self._on_create(text)

    def _create_item(self, model: Any, text: str) -> ListItem:
        item = ListItem(text, model, self)
        self.__register_connects(item)

        return item

    def _init_list(self):
        pass

    def eventFilter(self, widget: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyRelease:
            event: QKeyEvent

            if event.key() == Qt.Key.Key_Return:
                if widget.objectName() == self.objectName():
                    self._save_new_item()
                    return True

        return super(AbstractModal, self).eventFilter(widget, event)
