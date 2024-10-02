from typing import Union, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton

from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.UIHelpers import UIHelpers
from App.Widgets.Components.Notifications.NotificationItem import NotificationItem
from App.helpers import events, styles, lc


class NotificationList(DrawableWidget):
    def __init__(self, width: int, parent: QWidget = None):
        super(NotificationList, self).__init__(parent)
        self.setObjectName("NotificationsListContainer")
        self.setStyleSheet(styles(["notificationsList", "scrollBar"]))
        self.setFixedWidth(width)

        self.__central_layout = UIHelpers.v_layout((5, 5, 2, 5), 5)

        self.__header_layout = UIHelpers.h_layout((2, 2, 2, 2), 1)

        self.__title = QLabel(lc("notifications.listWidget.title"), self)
        self.__title.setObjectName("NotificationsListTittle")
        self.__title.setFixedHeight(20)
        self.__header_layout.addWidget(self.__title)

        self.__header_layout.addStretch()

        self.__clear_all_button = QPushButton(lc("notifications.listWidget.clearAll"), self)
        self.__clear_all_button.setObjectName("NotificationsListClearAllButton")
        self.__clear_all_button.setFixedHeight(20)
        self.__clear_all_button.clicked.connect(self.__clear_all)
        self.__clear_all_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.__header_layout.addWidget(self.__clear_all_button)

        self.__central_layout.addLayout(self.__header_layout)

        self.__scroll_area = UIHelpers.create_scroll(self, 'NotificationsListScrollArea')

        self.__scroll_area_widget = QWidget(self.__scroll_area)
        self.__scroll_area_widget.setObjectName('NotificationsList')

        self.__scroll_area_layout = UIHelpers.v_layout((0, 0, 5, 0), 0)

        self.__content_layout = UIHelpers.v_layout((0, 0, 0, 0), 5)

        self.__scroll_area_layout.addLayout(self.__content_layout)

        self.__scroll_area_layout.addStretch()

        self.__scroll_area_widget.setLayout(self.__scroll_area_layout)
        self.__scroll_area.setWidget(self.__scroll_area_widget)
        self.__central_layout.addWidget(self.__scroll_area)

        events().register_signal("notify", self, "create_item")

        self.setLayout(self.__central_layout)

    def __clear_all(self):
        while item := self.__content_layout.takeAt(0):
            if item := item.widget():
                item.deleteLater()

        events().fire('notify_indicate_disable')

    def __delete_item(self, item: NotificationItem):
        item.deleteLater()
        self.__content_layout.removeWidget(item)

    def create_item(self, _type: Union[NotificationItem.Type, str], title: str, text: Optional[str] = None):
        if isinstance(_type, str):
            _type = NotificationItem.Type(_type)

        notify = NotificationItem(_type, title, text, self)
        notify.deleted.connect(lambda: self.__delete_item(notify))
        self.__content_layout.insertWidget(0, notify)

        notify.adjustSize()

        events().fire('notify_indicate')
