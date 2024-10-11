from enum import Enum
from typing import Any, Optional

from PySide6.QtCore import Signal, Qt, QEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, QLineEdit

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import icon, lc


class ListItem(DrawableWidget):
    class Mode(Enum):
        VIEW = 1
        EDIT = 2

    deleted = Signal()
    changedName = Signal(str)
    changedMode = Signal(Mode)

    def __init__(self, text: str, model: Any, parent: QWidget = None):
        super(DrawableWidget, self).__init__(parent)
        self.setObjectName("ListItem")

        self.__text = text
        self.__model = model
        self.__mode = self.Mode.VIEW
        self.__error: Optional[str] = None

        self.__central_layout = UIHelpers.h_layout((10, 3, 3, 3), 5)

        self.__content_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)

        self.__label = QLabel(text, self)
        self.__label.setObjectName("ListItemLabel")
        self.__label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.__content_layout.addWidget(self.__label)

        self.__label_editor = QLineEdit(self)
        self.__label_editor.setObjectName("ListItemEditor")
        self.__label_editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.__label_editor.setHidden(True)
        self.__label_editor.textChanged.connect(self.__drop_error)
        self.__content_layout.addWidget(self.__label_editor)

        self.__error_widget = QLabel(self)
        self.__error_widget.setObjectName("ListItemError")
        self.__error_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.__error_widget.setHidden(True)
        self.__content_layout.addWidget(self.__error_widget)

        self.__central_layout.addLayout(self.__content_layout)

        self.__rename_button = self.__create_button("rename.png", "ListItemRenameButton", lambda: self.__change_mode(self.Mode.EDIT))
        self.__central_layout.addWidget(self.__rename_button)

        self.__delete_button = self.__create_button("bin.png", "ListItemDeleteButton", self.deleted)
        self.__central_layout.addWidget(self.__delete_button)

        self.__ok_rename_button = self.__create_button("check-mark.png", "ListItemOkRenameButton", self.__rename_signal)
        self.__ok_rename_button.setHidden(True)
        self.__central_layout.addWidget(self.__ok_rename_button)

        self.__cancel_button = self.__create_button("cross.png", "ListItemCancelButton", lambda: self.__change_mode(self.Mode.VIEW))
        self.__cancel_button.setHidden(True)
        self.__central_layout.addWidget(self.__cancel_button)

        self.setLayout(self.__central_layout)

        self.installEventFilter(self)

    def rename(self, text: str):
        self.__text = text
        self.__label.setText(text)
        self.__change_mode(self.Mode.VIEW)

    def __change_mode(self, mode: Mode):
        self.__mode = mode

        if mode == self.Mode.VIEW:
            self.__label_editor.setText("")
            self.__label.setVisible(True)
            self.__label_editor.setHidden(True)
            self.__drop_error()
            self.__delete_button.setVisible(True)
            self.__rename_button.setVisible(True)
            self.__ok_rename_button.setHidden(True)
            self.__cancel_button.setHidden(True)
            self.setProperty('primary', False)

        if mode == self.Mode.EDIT:
            self.__label.setHidden(True)
            self.__label_editor.setText(self.__text)
            self.__label_editor.selectAll()
            self.__label_editor.setVisible(True)
            self.__delete_button.setHidden(True)
            self.__rename_button.setHidden(True)
            self.__ok_rename_button.setVisible(True)
            self.__cancel_button.setVisible(True)
            self.setProperty('primary', True)

        UIHelpers.update_style(self)
        self.changedMode.emit(mode)

    def __drop_error(self):
        self.__error = None
        self.__error_widget.setHidden(True)
        self.__error_widget.setText("")

    def set_error(self, error: str):
        self.__error = error
        self.__error_widget.setText(error)
        self.__error_widget.setVisible(True)

    def __rename_signal(self):
        text = self.__label_editor.text()

        if text == self.__text:
            self.__change_mode(self.Mode.VIEW)

            return

        if not text:
            self.set_error(lc('listModal.errors.empty'))

            return

        self.changedName.emit(text)

    def set_text(self, text: str):
        self.__text = text
        self.__label.setText(text)

    def set_model(self, model: Any):
        self.__model = model

    def text(self) -> str:
        return self.__label.text()

    def model(self) -> Any:
        return self.__model

    def __create_button(self, _icon: str, name: str, handle: callable) -> QPushButton:
        button = QPushButton(self)
        button.setIcon(icon(_icon))
        button.setObjectName(name)
        button.setFixedSize(26, 26)
        button.clicked.connect(handle)

        return button

    def eventFilter(self, watched: QWidget, event: QEvent):
        if event.type() == QEvent.Type.KeyRelease:
            event: QKeyEvent

            if self.__mode == self.Mode.EDIT:
                if event.key() == Qt.Key.Key_Return:
                    self.__rename_signal()

                    return True

                if event.key() == Qt.Key.Key_Escape:
                    self.__change_mode(self.Mode.VIEW)

        return super(ListItem, self).eventFilter(watched, event)
