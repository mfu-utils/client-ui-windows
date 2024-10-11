from PySide6.QtWidgets import QWidget

from App.Services.Client.Ui.UiScanService import UiScanService
from App.Widgets.Components.DrawableWidget import DrawableWidget
from App.Widgets.Components.ScanListWidget import ScanListWidget
from App.Widgets.UIHelpers import UIHelpers

from App.helpers import styles, events, platform, lc


class History(DrawableWidget):
    def __init__(self, parent: QWidget = None):
        super(History, self).__init__(parent)
        self.setObjectName("HistoryContainer")

        _styles = ["historyContainer", "scrollBar", "scanItem", "qMenu", "scanListEmptyStub", "qMenu"]

        if platform().is_darwin():
            _styles.append("qMenuMacFix")

        self.setStyleSheet(styles(_styles))

        self.__central_layout = UIHelpers.v_layout((0, 0, 0, 0), 10)

        self.__scroll_area = UIHelpers.create_scroll(self, "HistoryScrollArea")

        self.__history_list = ScanListWidget("History", self.__get_last, {"stub_title": lc("history.empty")}, self)

        self.__scroll_area.setWidget(self.__history_list)

        self.__central_layout.addWidget(self.__scroll_area)

        self.setLayout(self.__central_layout)

        events().register_signal("update-history", self, "update_history")

    @staticmethod
    def __get_last():
        return UiScanService.last(10)

    def update_history(self):
        self.__history_list.update_items()
