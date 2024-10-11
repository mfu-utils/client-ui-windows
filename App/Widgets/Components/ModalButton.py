from PySide6.QtWidgets import QPushButton, QWidget

from App.helpers import icon


class ModalButton(QPushButton):
    def __init__(self, parent: QWidget, name: str, title: str = None, icon_name: str = None, callback: callable = None):
        super(ModalButton, self).__init__(parent)

        if title is not None:
            self.setText(title)

        self.setObjectName(name)

        if icon_name:
            self.setIcon(icon(icon_name))

        if callback:
            self.clicked.connect(callback)

