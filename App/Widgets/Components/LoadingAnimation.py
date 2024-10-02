from typing import Tuple

import math
from PySide6.QtCore import QVariantAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget

from App.Widgets.Components.DrawableWidget import DrawableWidget


class LoadingAnimation(DrawableWidget):
    def __init__(self, size: Tuple[int, int], movable_size: Tuple[int, int], parent: QWidget = None):
        super(LoadingAnimation, self).__init__(parent)

        self.setObjectName('LoadingContainer')
        self.setFixedSize(size[0], size[1])

        transformed_widget = QWidget(self)
        transformed_widget.setObjectName('LoadingTransformedWidget')
        transformed_widget.setFixedSize(movable_size[0], movable_size[1])

        self.__start_pos = (0, self.height() / 2 - movable_size[1])

        transformed_widget.move(int(self.__start_pos[0]), int(self.__start_pos[1]))

        self.__create_animation(transformed_widget)

        self.__center_pos = (self.width() / 2, self.height() / 2)

    def hideEvent(self, event):
        self.__animation.stop()

        super(LoadingAnimation, self).hideEvent(event)

    def showEvent(self, event):
        self.__animation.start()

        super(LoadingAnimation, self).showEvent(event)

    def __create_animation(self, widget: QWidget):
        self.__animation = QVariantAnimation(widget)
        self.__animation.setDuration(1000)
        self.__animation.setStartValue(360)
        self.__animation.setEndValue(0)
        self.__animation.valueChanged.connect(lambda x: self.__rotate_angle(widget, x))
        self.__animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.__animation.setLoopCount(-1)
        self.__animation.start()

    def __rotate_angle(self, widget: QWidget, angle: int):
        pos = self.__start_pos

        x = pos[0] * math.cos(math.radians(angle)) - pos[1] * math.sin(math.radians(angle))
        y = pos[0] * math.sin(math.radians(angle)) + pos[1] * math.cos(math.radians(angle))

        widget.move(int(self.__center_pos[0] + x), int(self.__center_pos[1] - y))
