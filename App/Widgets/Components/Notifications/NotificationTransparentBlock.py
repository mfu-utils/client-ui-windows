from typing import Union

from PySide6.QtWidgets import QWidget

from App.Widgets.Components.Notifications.Notification import Notification
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import later, events, styles, ini


class NotificationTransparentBlock(QWidget):
    spacing = 3

    def __init__(self, parent: QWidget = None):
        super(NotificationTransparentBlock, self).__init__(parent)
        self.setStyleSheet(styles(["notification"]))
        self.setMinimumWidth(200)

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 0), self.spacing)

        self.setLayout(self.__central_layout)

        events().register_signal('notification-popup', self, 'add')
        events().register_signal('notification-popup-hide', self, 'hide')

    def update_pos(self):
        self.move(
            self.parentWidget().width() - self.width() - 10,
            self.parentWidget().height() - self.height() - 10
        )

    def __disable_notify(self, notify: Notification):
        if notify not in self.findChildren(Notification):
            return

        self.__central_layout.removeWidget(notify)
        notify.deleteLater()

        if not self.__central_layout.count():
            self.hide()

        self.update_rect()

    def update_rect(self):
        cnt = self.__central_layout.count()

        items_height = 45 * cnt

        if (cnt := cnt - 1) < 1:
            cnt = 0

        self.setFixedHeight(items_height + self.spacing * cnt)
        self.update_pos()

    def add(self, _type: Union[Notification.Type, str], text: str):
        notify = Notification(_type, text, self)
        notify.deleted.connect(lambda: self.__disable_notify(notify))

        self.__central_layout.addWidget(notify)
        self.show()
        self.adjustSize()

        later(ini('notifications.timeout', float) * 1000, lambda: self.__disable_notify(notify))

        self.update_rect()
