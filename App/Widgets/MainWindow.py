from typing import Optional

from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QApplication
from App.Core.Ui.Widgets import MainMenuBar
from App.Widgets.Components.History import History
from App.Widgets.Components.Notifications.NotificationTransparentBlock import NotificationTransparentBlock
from App.Widgets.Components.StatusBar import StatusBar
from App.Widgets.Components.ToolBar import ToolBar
from App.Widgets.Modals.AboutModal import AboutModal
from App.Widgets.Modals.PreferencesModal import PreferencesModal
from App.Widgets.Modals.ScanListModal import ScanListModal
from App.Widgets.Modals.ScanTypesListModal import ScanTypesListModal
from App.Widgets.Modals.TagsListModal import TagsListModal
from App.Widgets.Tray import Tray
from App.Widgets.UIHelpers import UIHelpers
from App.Widgets.Components.Tools.ScanTools import ScanTools
from App.Widgets.Components.Notifications.NotificationList import NotificationList

from App.helpers import config, ini, styles, icon, screens, events


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        self.__notify_block: Optional[NotificationTransparentBlock] = None

        super(MainWindow, self).__init__(None)
        self.setWindowTitle(config("app.name"))
        self.setObjectName('MainWindow')
        self.setStyleSheet(styles('main'))
        self.setWindowIcon(icon('logo.png'))
        self.setMenuBar(MainMenuBar(self).get_manu_bar())

        rect = config('ui.rect')

        self.resize(ini('app.width', int), ini('app.height', int))
        self.setMinimumSize(rect['min-width'], rect['min-height'])

        self.__central_widget = QWidget(self)

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 0), 0)

        self.__content_layout = UIHelpers.h_layout((0, 0, 0, 0), 0)

        # ToolBar
        self.__content_layout.addWidget(ToolBar(self.__central_widget))
        # Notifications
        self.__notifications_widget = NotificationList(250, self.__central_widget)
        self.__notifications_widget.hide()
        self.__content_layout.addWidget(self.__notifications_widget)
        events().register("notification-widget-checkout", self, self.__checkout_notifications)
        # History
        self.__content_layout.addWidget(History(self.__central_widget))

        self.__central_layout.addLayout(self.__content_layout)
        self.__central_layout.addWidget(StatusBar(self.__central_widget))
        self.__central_widget.setLayout(self.__central_layout)

        self.setCentralWidget(self.__central_widget)

        self.__notify_block = NotificationTransparentBlock(self)
        self.__notify_block.hide()

        if not self.__reset_screen_parameters():
            UIHelpers.to_center_screen(self)

        self.__moved = False
        self.__pressed = False

        self.installEventFilter(self)

        self.__tray = Tray(app, self)
        self.__tray.show()

    def __checkout_notifications(self):
        visible = self.__notifications_widget.isVisible()

        if not visible:
            events().fire('notify_indicate_disable')

        self.__notifications_widget.setVisible(not visible)
        self.resize(self.width() + (-1 if visible else 1) * self.__notifications_widget.width(), self.height())

        self.__update_screen_parameters()

    def __update_screen_parameters(self):
        primary_screen = QApplication.primaryScreen()

        for screen in QApplication.screens():
            if screen.availableGeometry().contains(self.pos()):
                primary_screen = screen

                break

        geometry = primary_screen.geometry()

        notifications = self.__notifications_widget

        width = self.width() - (notifications.width() if notifications.isVisible() else 0)

        screens().set_screen_parameters(
            primary_screen.name(),
            (self.x() - geometry.x(), self.y() - geometry.y()), (width, self.height())
        )

    def __reset_screen_parameters(self) -> bool:
        primary_screen = None
        current_name = screens().get_current_screen_name()

        for screen in QApplication.screens():
            if screen.name() == current_name:
                primary_screen = screen
                break

        if not primary_screen:
            return False

        geometry = primary_screen.availableGeometry()

        if parameters := screens().get_screen_parameters(current_name):
            pos = parameters['pos']
            size = parameters['size']

            self.move(pos[0] + geometry.x(), pos[1] + geometry.y())
            self.resize(size[0], size[1])

            return True

        return False

    def open_settings(self):
        PreferencesModal(self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # print(urls)
            # print(event.mimeData().formats())
        # TODO: Create transparent layer with info
        super(MainWindow, self).dragEnterEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        # TODO: Hide transparent layer
        super(MainWindow, self).dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            # urls = event.mimeData().urls()
            # print(urls)
            pass
        # TODO: Determinate image and get path for open document modal
        super(MainWindow, self).dropEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self:
            if event.type() == QEvent.Type.Close:
                event.ignore()
                self.__tray.close_tray_modals()
                self.hide()
                return True

            if event.type() == QEvent.Type.NonClientAreaMouseButtonPress:
                self.__pressed = True

            if event.type() == QEvent.Type.NonClientAreaMouseMove and self.__pressed:
                self.__moved = True

            if event.type() == QEvent.Type.Leave:
                self.__update_screen_parameters()

            if event.type() == QEvent.Type.NonClientAreaMouseButtonRelease:
                if self.__moved:
                    self.__update_screen_parameters()

                self.__pressed = False
                self.__moved = False

            if event.type() == QEvent.Type.Resize:
                if self.__notify_block:
                    self.__notify_block.update_pos()

        return super(MainWindow, self).eventFilter(watched, event)

    def open_scan_types_modal(self):
        ScanTypesListModal(self)

    def open_tags_modal(self):
        TagsListModal(self)

    def open_scan_new(self):
        ScanTools(self).create_scan()

    def open_scan_list_modal(self):
        ScanListModal(self)

    def open_about_modal(self):
        AboutModal(self)
