from PySide6.QtWidgets import QPushButton, QWidget

from App.helpers import events


class NotificationButton(QPushButton):
    def __init__(self, parent: QWidget = None):
        super(NotificationButton, self).__init__(parent)

        self.__indicator = QWidget(self)
        self.__indicator.setObjectName("Indicator")
        self.__indicator.setFixedSize(8, 8)
        self.__indicator.hide()
        self.__indicator.raise_()

        events().register_signal("notify_indicate", self.__indicator, "show")
        events().register_signal("notify_indicate_disable", self.__indicator, "hide")

    def indicator(self):
        return self.__indicator

    def set_indicator_state(self, state: bool):
        self.__indicator.setVisible(state)

    # noinspection PyMethodOverriding
    def setFixedSize(self, arg__1: int, arg__2: int):
        super().setFixedSize(arg__1, arg__2)
        self.__indicator.move(self.width() - self.__indicator.width() - 5, 5)
