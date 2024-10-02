from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QPushButton

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers


class Item(DrawableWidget):
    deleted = Signal()

    def __init__(self, key: str, value: str, parent: QWidget = None):
        super(Item, self).__init__(parent)
        self.setObjectName("MultiselectItem")

        self.__key = key
        self.__value = value

        self.__central_layout = UIHelpers.h_layout((2, 2, 2, 2), 2)

        self.__label = QLabel(value, self)
        self.__label.setObjectName("MultiselectItemLabel")
        self.__label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.__central_layout.addWidget(self.__label)

        self.__delete_button = QPushButton("\u2715", self)
        self.__delete_button.setObjectName("MultiselectItemDeleteButton")
        self.__delete_button.setFixedSize(16, 16)
        self.__delete_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.__delete_button.clicked.connect(self.deleted.emit)
        self.__central_layout.addWidget(self.__delete_button)

        self.setLayout(self.__central_layout)

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus | Qt.FocusPolicy.TabFocus)

        self.show()

    def keyReleaseEvent(self, event):
        if event.key() in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace]:
            self.deleted.emit()
            return

        super(Item, self).keyReleaseEvent(event)

    def key(self) -> str:
        return self.__key

    def value(self) -> str:
        return self.__value
