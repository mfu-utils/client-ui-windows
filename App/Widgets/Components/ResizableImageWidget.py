from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy


class ResizableImageWidget(QLabel):
    def __init__(self, image: Union[str, bytes], parent: QWidget = None):
        super().__init__(parent)
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap()

        if isinstance(image, str):
            pixmap.load(image)
        else:
            pixmap.loadFromData(image)

        self.setPixmap(pixmap)
