from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy

from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import lc, styles


class ConfirmModal(AbstractModal):
    confirmed = Signal()
    cancelled = Signal()

    def __init__(self, disabled_object_name: str, title: str, ask: str, parent: QWidget = None):
        super(ConfirmModal, self).__init__(parent)
        self._frameless_window()
        self.setStyleSheet(styles(["confirmModal", "windowlessTitle"]))
        self.centralWidget().setObjectName("ConfirmModal")

        self.__central_layout = UIHelpers.v_layout()
        self.__central_layout.addWidget(self._create_title(title, 'WindowlessTitle'))

        self.__content_layout = UIHelpers.v_layout((0, 0, 0, 0), 10)

        self.__ask = QLabel(ask, self)
        self.__ask.setObjectName("ConfirmModalAsk")
        self.__ask.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__content_layout.addWidget(self.__ask)

        self.__buttons_layout = UIHelpers.h_layout((0, 0, 0, 0), 10)
        self.__buttons_layout.addWidget(self._create_button("cancel", "ConfirmModalCancelButton", self._on_cancel))
        self.__buttons_layout.addWidget(self._create_button("confirm", "ConfirmModalConfirmButton", self._on_confirm))

        self.__content_layout.addLayout(self.__buttons_layout)

        self.__central_layout.addLayout(self.__content_layout)

        self.centralWidget().setLayout(self.__central_layout)

        self.show()

        UIHelpers.to_center(self, UIHelpers.find_parent_recursive(self, "MainWindow"))

        self._disable_all_parents(disabled_object_name)

    def _on_confirm(self):
        self.confirmed.emit()
        self.close()

    def _on_cancel(self):
        self.cancelled.emit()
        self.close()

    def _create_button(self, _lc: str, name: str, callback: callable) -> QPushButton:
        button = QPushButton(lc(f"confirmModal.{_lc}"), self)
        button.setFixedHeight(30)
        button.setObjectName(name)
        button.clicked.connect(callback)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        return button
