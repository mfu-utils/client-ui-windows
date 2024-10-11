from PySide6.QtWidgets import QWidget

from App.Widgets.Modals.ErrorModal import ErrorModal
from App.helpers import notification, lc


class WindowsHelpers:
    @staticmethod
    def error(title: str, message: str, notify: bool = True, parent: QWidget = None):
        ErrorModal(title, message, parent)

        if notify:
            notification().error(title, message)

    @staticmethod
    def file_not_found(path: str, notify: bool = True, parent: QWidget = None):
        WindowsHelpers.error(lc('errors.file_not_found_title'), lc('errors.file_not_found_msg') % path, notify, parent)
