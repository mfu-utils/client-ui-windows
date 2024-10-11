from typing import Optional, List

from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QKeyEvent, Qt, QMouseEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel

from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles, config


class AbstractModal(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super(AbstractModal, self).__init__(parent)
        UIHelpers.setup_modal(self)

        self.__disabled_widget: Optional[QWidget] = None

        self.__frameless = False
        self.__central_widget = QWidget(self)
        self.setCentralWidget(self.__central_widget)
        self.__central_widget.setStyleSheet(styles('modal'))

        self.__central_widget.setObjectName('AbstractModal')

        self.__shadow_size = config('ui.shadow-offset')
        self.__movable_offset = config('ui.frameless-drawable-top-offset')

        self.__shadow_enable = True
        self.__prev_pos = None
        self.__movable = False
        self.__dd = False

    def set_shadow_enabled(self, enable: bool):
        self.__shadow_enable = enable

    def _create_title(self, title: str, name: str):
        title = QLabel(title, self)
        title.setObjectName(name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return title

    def show(self):
        self.__create_central_widget()
        super(AbstractModal, self).show()

    def _d8d(self, enabled: bool = False):
        self.__dd = enabled

    def _frameless_window(self, flags: int = Qt.WindowType.FramelessWindowHint, attributes: List[Qt.WidgetAttribute] = None):
        self.__frameless = True
        self.__dd = True

        self.setWindowFlags(self.windowFlags() | flags)

        for attr in (attributes if attributes is not None else [Qt.WidgetAttribute.WA_TranslucentBackground]):
            self.setAttribute(attr)

    def __create_central_widget(self):
        if self.__frameless and config('ui.shadow-enabled') and self.__shadow_enable:
            self.setCentralWidget(UIHelpers.create_shadow_container(self, self.__central_widget, self.__shadow_size))

            return

        self.setCentralWidget(self.__central_widget)

    def _disable_all_parents(self, object_name: str = 'MainWindow'):
        self.__disabled_widget = UIHelpers.find_parent_recursive(self, object_name)
        self.__disabled_widget.setDisabled(True)
        self.setDisabled(False)

    def _do_cancel(self):
        self.close()

    def _do_ok(self):
        self.close()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self:
            if event.type() == QKeyEvent:
                event: QKeyEvent

                if event.key() == Qt.Key.Key_Escape:
                    self._do_cancel()
                    return True

                if event.key() == Qt.Key.Key_Return:
                    self._do_ok()
                    return True

        return super(AbstractModal, self).eventFilter(watched, event)

    def closeEvent(self, event):
        if self.__disabled_widget:
            self.__disabled_widget.setDisabled(False)

        super(AbstractModal, self).closeEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self.__dd:
            return

        pos = event.pos()
        check_pos = self.__central_widget.mapFrom(self, pos)

        if self.__central_widget.rect().contains(check_pos) and check_pos.y() <= self.__movable_offset:
            self.__prev_pos = pos
            self.__movable = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.__dd:
            return

        if not self.__movable:
            return

        self.move(self.pos() + event.pos() - self.__prev_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.__dd:
            self.__movable = False
            self.__prev_pos = None
