from typing import Optional

from sqlalchemy.event import Events

from App import Application


class UiNotificationService:
    @staticmethod
    def __events() -> Events:
        return Application().get('events')

    @staticmethod
    def notify(_type: str, title: str, text: Optional[str] = None):
        UiNotificationService.__events().fire("notify", _type=_type, title=title, text=text)
        UiNotificationService.notify_popup(_type, title)

    @staticmethod
    def notify_popup(_type: str, text: str):
        UiNotificationService.__events().fire("notification-popup", _type=_type, text=text)

    @staticmethod
    def error(title: str, text: Optional[str] = None):
        UiNotificationService.notify("error", title, text)

    @staticmethod
    def success(title: str, text: Optional[str] = None):
        UiNotificationService.notify("success", title, text)

    @staticmethod
    def warning(title: str, text: Optional[str] = None):
        UiNotificationService.notify("warning", title, text)
