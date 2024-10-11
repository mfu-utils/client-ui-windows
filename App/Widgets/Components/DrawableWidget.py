from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QStyleOption, QStyle


class DrawableWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super(DrawableWidget, self).__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        opt = QStyleOption()

        opt.initFrom(self)

        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
