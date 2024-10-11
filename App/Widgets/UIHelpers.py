from typing import Optional, Tuple

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QScrollArea
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QLayout, QVBoxLayout, QHBoxLayout, QGridLayout

from App.helpers import platform, pixmap


class UIHelpers:
    @staticmethod
    def setup_modal(widget: QMainWindow):
        if platform().is_darwin():
            return

        widget.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

    @staticmethod
    def get_main_window(widget: QWidget) -> QWidget:
        return UIHelpers.find_parent_recursive(widget, 'MainWindow')

    @staticmethod
    def find_parent_recursive(widget: QWidget, name: str) -> Optional[QWidget]:
        if widget.objectName() == name:
            return widget

        while widget.objectName() != name:
            try:
                widget = widget.parent()
            except AttributeError:
                return None

        return widget

    @staticmethod
    def set_disabled_parent_recursive(widget: QWidget, name: str, disabled: bool) -> bool:
        if widget := UIHelpers.find_parent_recursive(widget, name):
            widget.setDisabled(disabled)

        return bool(widget)

    @staticmethod
    def image(path: str, parent: QWidget = None, size: Optional[Tuple[int, int]] = None) -> QLabel:
        image = QLabel(parent)

        _pixmap = pixmap(path)

        if size is not None:
            scale = parent.devicePixelRatio()
            _pixmap.setDevicePixelRatio(scale)

            _pixmap = _pixmap.scaled(
                QSize(int(size[0] * scale), int(size[1] * scale)),
                mode=Qt.TransformationMode.SmoothTransformation
            )

        image.setPixmap(_pixmap)

        if size is not None:
            image.setFixedSize(size[0], size[1])

        return image

    @staticmethod
    def layout(ll: QLayout, margins: tuple, spacing: int = 0):
        ll.setContentsMargins(margins[0], margins[1], margins[2], margins[3])
        ll.setSpacing(spacing)

    @staticmethod
    def g_layout(margins: tuple = (10, 10, 10, 10), spacing: int = 10) -> QGridLayout:
        layout = QGridLayout()
        UIHelpers.layout(layout, margins, spacing)

        return layout

    @staticmethod
    def v_layout(margins: tuple = (10, 10, 10, 10), spacing: int = 10) -> QVBoxLayout:
        layout = QVBoxLayout()
        UIHelpers.layout(layout, margins, spacing)

        return layout

    @staticmethod
    def h_layout(margins: tuple = (10, 10, 10, 10), spacing: int = 10) -> QHBoxLayout:
        layout = QHBoxLayout()
        UIHelpers.layout(layout, margins, spacing)

        return layout

    @staticmethod
    def font(
            size: int,
            weight: QFont.Weight = QFont.Weight.Normal,
            style: QFont.Style = QFont.Style.StyleNormal
    ) -> QFont:
        font = QFont()

        font.setWeight(weight)
        font.setStyle(style)
        font.setPixelSize(size)

        return font

    @staticmethod
    def update_style(widget: QWidget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    @staticmethod
    def layout_for_grid(direction: str) -> QLayout:
        if direction == 'vertical':
            layout = UIHelpers.v_layout((0, 0, 0, 0))
        elif direction == 'horizontal':
            layout = UIHelpers.h_layout((0, 0, 0, 0))
        else:
            raise ValueError(f'Unknown direction: {direction}')

        return layout

    @staticmethod
    def spacing_for_grid(size: int, direction: str) -> QHBoxLayout:
        layout = UIHelpers.layout_for_grid(direction)
        layout.addSpacing(size)

        return layout

    @staticmethod
    def stretch_for_grid(direction: str) -> QHBoxLayout:
        layout = UIHelpers.layout_for_grid(direction)
        layout.addStretch()

        return layout

    @staticmethod
    def to_center_screen(widget: QWidget):
        gm = UIHelpers.get_main_window(widget).screen().geometry()

        widget.move(
            int(gm.x() + gm.width() / 2 - widget.width() / 2),
            int(gm.y() + gm.height() / 2 - widget.height() / 2)
        )

    @staticmethod
    def to_center(widget: QWidget, parent: QWidget = None):
        map_to = parent or widget.parentWidget()

        pos = map_to.pos() if map_to.objectName() == "MainWindow" else map_to.mapToGlobal(map_to.pos())

        widget.move(
            int(pos.x() + map_to.width() / 2 - widget.width() / 2),
            int(pos.y() + map_to.height() / 2 - widget.height() / 2),
        )

    @staticmethod
    def create_shadow(widget: QWidget, y_offset: float, x_offset: float, size: int):
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(size)
        shadow.setYOffset(y_offset)
        shadow.setXOffset(x_offset)
        shadow.setColor(QColor(0, 0, 0, 160))
        widget.setGraphicsEffect(shadow)

    @staticmethod
    def create_shadow_container(parent: QWidget, child: QWidget, size: int):
        if not platform().is_windows():
            return child

        UIHelpers.create_shadow(child, 20, 0, size)

        widget = QWidget(parent)
        layout = UIHelpers.v_layout((size, size, size, size), 0)

        layout.addWidget(child)

        widget.setLayout(layout)

        return widget

    @staticmethod
    def create_scroll(
            parent: QWidget,
            name: str,
            resizable: bool = True,
            scroll_policy: (Qt.ScrollBarPolicy, ...) = (
                    Qt.ScrollBarPolicy.ScrollBarAsNeeded,
                    Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
    ):
        scroll_area = QScrollArea(parent)
        scroll_area.setObjectName(name)
        scroll_area.setWidgetResizable(resizable)
        scroll_area.setVerticalScrollBarPolicy(scroll_policy[0])
        scroll_area.setHorizontalScrollBarPolicy(scroll_policy[1])

        return scroll_area
