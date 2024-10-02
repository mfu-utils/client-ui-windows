from typing import Any

from PySide6.QtCore import Signal, QObject


class QSignalObject(QObject):
    triggered = Signal(Any)

    def __init__(self):
        super(QSignalObject, self).__init__()

    def trigger(self, value: Any):
        self.triggered.emit(value)
