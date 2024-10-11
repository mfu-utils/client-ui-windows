from PySide6.QtWidgets import QWidget

from App.Widgets.Components.Paginator import Paginator
from App.Widgets.UIHelpers import UIHelpers


class PaginatorContainer(QWidget):
    def __init__(self, total_pages: int, page: int = 1, parent: QWidget = None):
        super(PaginatorContainer, self).__init__(parent)
        self.setFixedHeight(50)

        self.__paginator_layout = UIHelpers.h_layout(spacing=0)
        self.__paginator_layout.addStretch()

        self.__paginator = Paginator(total_pages, page, self)
        self.__paginator_layout.addWidget(self.__paginator)

        self.__paginator_layout.addStretch()

        self.setLayout(self.__paginator_layout)

    def paginator(self) -> Paginator:
        return self.__paginator
