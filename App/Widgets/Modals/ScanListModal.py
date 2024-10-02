from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QWidget, QPushButton

from App.Core.Utils.Ui import Casts
from App.Models.Client.Scan import Format as ScanFormat
from App.Models.Client.ScanType import ScanType
from App.Services.Client.DocConvertorService import DocConvertorService
from App.Services.Client.ScanService import ScanService
from App.Services.Client.ScanTypeService import ScanTypeService
from App.Services.Client.TagService import TagService
from App.Widgets.Components.PaginatorContainer import PaginatorContainer
from App.Widgets.Components.PreferencesControls import PreferencesControls
from App.Widgets.Components.ScanListWidget import ScanListWidget
from App.Widgets.Modals.AbstractModal import AbstractModal
from App.Widgets.UIHelpers import UIHelpers
from App.helpers import lc, styles, platform


class ScanListModal(AbstractModal):
    PER_PAGE = 20

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("ScanListContainer")
        self.setWindowTitle(lc("scanListWidget.title"))
        _styles = ["scanListContainer", "scrollBar", "scanItem", "qMenu", "scanListEmptyStub"]

        if platform().is_darwin():
            _styles.append("qMenuMacFix")

        self.setStyleSheet(styles(_styles))
        self.setMinimumSize(1000, 600)
        self.resize(1300, 800)

        self.__parameters = {}
        self.__current_page = 1
        self.__total_count = 0

        self.__central_layout = UIHelpers.h_layout((0, 0, 0, 0))

        self.__filters_layout = UIHelpers.v_layout((0, 0, 0, 0), 10)

        self.__filters_widget = PreferencesControls(lc("scanListWidget.filters.title"), self)
        self.__filters_widget.setFixedWidth(400)
        self.__filters_widget.add_set_value_callback(self.__set_value)
        self.__fill_filters()

        self.__filters_layout.addWidget(self.__filters_widget)

        self.__filters_buttons_widget = QWidget(self)
        self.__filters_buttons_widget.setFixedWidth(400)

        self.__filters_buttons_layout = UIHelpers.h_layout()
        self.__filters_buttons_layout.addStretch()

        self.__filter_button = QPushButton(lc('scanListWidget.filter_button'), self)
        self.__filter_button.setObjectName("ScanListFilterButton")
        self.__filter_button.clicked.connect(self.update_list)
        self.__filter_button.setFixedSize(70, 30)

        self.__filters_buttons_layout.addWidget(self.__filter_button)

        self.__filters_buttons_widget.setLayout(self.__filters_buttons_layout)

        self.__filters_layout.addWidget(self.__filters_buttons_widget)

        self.__central_layout.addLayout(self.__filters_layout)

        self.__content_widget = QWidget(self)
        self.__content_widget.setObjectName('ScanListContentContainer')

        self.__content_layout = UIHelpers.v_layout((0, 0, 0, 0), 10)

        self.__scroll_widget = UIHelpers.create_scroll(self, "ScanListScrollArea")

        self.__list_widget = ScanListWidget("ScanList", self.__filter, {"stub_title": lc("scanListWidget.empty")}, self)
        self.__scroll_widget.setWidget(self.__list_widget)
        self.__content_layout.addWidget(self.__scroll_widget)

        self.__paginator_container = PaginatorContainer(0, parent=self)
        self.__paginator = self.__paginator_container.paginator()
        self.__paginator.changed.connect(self.__update_page)

        self.__content_layout.addWidget(self.__paginator_container)

        self.__content_widget.setLayout(self.__content_layout)

        self.__central_layout.addWidget(self.__content_widget)

        self.centralWidget().setLayout(self.__central_layout)

        UIHelpers.to_center_screen(self)

        self.installEventFilter(self)

        self.__update_page(1)

        self.show()

        self._disable_all_parents()

    def __filter(self):
        params = {'title': self.__parameters.get('title')}

        if _format := self.__parameters.get('format'):
            params.update({'format': ScanFormat(int(_format))})

        if _type := self.__parameters.get('type'):
            scan_type = ScanType()

            scan_type.id = _type

            params.update({'type': scan_type})

        if _tags := self.__parameters.get('tags'):
            params.update({'tags': Casts.str2int_list(_tags)})

        if _doc_types := self.__parameters.get('doc_types'):
            params.update({'doc_types': Casts.str2int_list(_doc_types)})

        if _strong := self.__parameters.get('strong_tags'):
            params.update({'strict_tags': _strong})

        self.__total_count, items = ScanService.filter(self.__current_page, self.PER_PAGE, params)

        return items

    def __update_page(self, index: int):
        self.__current_page = index
        self.update_list()

    def update_list(self):
        self.__list_widget.update_items()

        cnt, mod = divmod(self.__total_count, self.PER_PAGE)

        if mod:
            cnt += 1

        self.__paginator.update_(cnt, self.__current_page)
        self.__paginator_container.setVisible(cnt > 1)

    def __set_value(self, key: str, value: str):
        self.__parameters.update({key: value})

    def __fill_filters(self):
        width = 70

        title_input = self.__filters_widget.create_line_edit('title', lc("scanListWidget.filters.name"))
        title_input.label().setFixedWidth(width)

        formats = dict(map(lambda x: (str(x.value), x.name), ScanFormat))
        formats = self.__filters_widget.create_combo_box('format', lc("scanListWidget.filters.format"), formats)
        formats.label().setFixedWidth(width)

        types = ScanTypeService.for_select("* " + lc("scanListWidget.all_types"))
        types_widget = self.__filters_widget.create_combo_box('type', lc("scanListWidget.filters.type"), types)
        types_widget.label().setFixedWidth(width)

        convertors = DocConvertorService.TYPES
        doc_types = dict(map(lambda x: (str(x[0].value), f"(.{x[1]['extension']}) {x[1]['name']}"), convertors.items()))
        self.__filters_widget.create_multiselect('doc_types', lc("scanListWidget.filters.doc_types"), doc_types)

        tags = TagService.for_select()
        self.__filters_widget.create_multiselect('tags', lc("scanListWidget.filters.tags"), tags)

        # TODO: Strong find by tags
        # self.__filters_widget.create_check_box('strict_tags', lc("scanListWidget.filters.strict_tags"))

        self.__filters_widget.generate()
        self.__filters_widget.set_checking_prev_value_enabled(False)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            event: QKeyEvent

            if event.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return]:
                self.update_list()
                return True

        return super(ScanListModal, self).eventFilter(watched, event)
