from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget, QApplication

from App.Core.Ui.TrayButton import TrayButton
from App.Widgets.Components.Tools.ScanTools import ScanTools
from App.Widgets.Modals.DragAndDropPrintModal import DragAndDropPrintModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import lc, config


class Tray(TrayButton):
    MARGIN = 20

    def __init__(self, app: QApplication, parent: QWidget = None):
        self.__parent_widget = parent
        self.__light = app.styleHints().colorScheme() != Qt.ColorScheme.Dark

        self.__modals = {}

        super(Tray, self).__init__("printer_dark" if self.__light else "printer", parent)

        self.add_action(config('app.name'), callback=self.show_main_window)
        self.add_action(lc('tray.print'), callback=self.open_printing_modal)
        self.add_separator()
        self.add_action(lc('tray.scan'), callback=lambda: ScanTools(parent).create_scan())
        self.add_separator()
        self.add_action(lc('tray.quit'), callback=app.quit)

    def show_main_window(self):
        main_window = UIHelpers.get_main_window(self.__parent_widget)

        main_window.show()
        main_window.raise_()

    def close_modal(self, win_id: int):
        if win := self.__modals.get(win_id):
            win: QWidget

            if win.isVisible():
                win.close()
                self.__modals.pop(win_id)

    def close_tray_modals(self):
        for modal in self.__modals.copy().values():
            modal: QWidget
            modal.close()

        self.__modals = {}

    def open_printing_modal(self):
        modal = DragAndDropPrintModal(self.__parent_widget)
        modal.closed.connect(lambda: self.close_modal(modal.winId()))

        self.__modals.update({modal.winId(): modal})

        tray_geometry = self._tray.geometry()
        screen_geometry = QApplication.primaryScreen().geometry()

        for screen in QApplication.screens():
            tray_pos = QPoint(tray_geometry.x(), tray_geometry.y())

            if screen.geometry().contains(tray_pos):
                screen_geometry = screen.availableGeometry()

                break

        bottom = screen_geometry.height() + screen_geometry.y()
        max_right_pos = screen_geometry.x() + screen_geometry.width() - self.MARGIN
        right_pos = tray_geometry.x() + modal.width()

        is_top = (bottom / 2) > tray_geometry.y()

        x = (max_right_pos if right_pos > max_right_pos else right_pos) - modal.width()
        y = self.MARGIN + screen_geometry.y() if is_top else bottom - self.MARGIN - modal.height()

        modal.move(x, y)
