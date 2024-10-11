from App.Core.Logger import Log
from typing import Any
from PySide6.QtCore import Signal, QObject


class QSignalObject(QObject):
    triggered = Signal(Any)

    def __init__(self):
        super(QSignalObject, self).__init__()

    def trigger(self, value: Any):
        self.triggered.emit(value)


def get_namespace(obj: object) -> str:
    return '.'.join([obj.__module__,  obj.__class__.__name__])


class Event:
    metadata = {}

    def __init__(self, log: Log):
        self.log = log

    def register(self, name: str, recipient: object, callback: callable):
        if not (callbacks := self.metadata.get(name)):
            self.metadata[name] = callbacks = {}

        obj = get_namespace(recipient)

        callbacks.update({obj: callback})
        self.log.debug(f"Registered event '{obj}.{name}'", {'object': self})

    def unregister(self, name: str, recipient: object = None):
        if not self.metadata.get(name):
            return

        if recipient is None:
            self.metadata.pop(name)
            return

        self.metadata[name].pop(get_namespace(recipient))
        self.log.debug(f"Unregistered event '{name}'", {'object': self})

    def fire(self, name: str, *args, **kw):
        if not self.metadata.get(name):
            return

        for key, item in self.metadata[name].items():
            item(*args, **kw)
            self.log.debug(f"Fire event '{name}' to '{key}'", {'object': self})

    def register_signal(self, name: str, recipient: QObject, callback: str):
        signal = QSignalObject()

        signal.triggered.connect(lambda x: recipient.__getattribute__(callback)(*x[0], **x[1]))

        self.register(name, recipient, lambda *args, **kw: signal.trigger([args, kw]))
