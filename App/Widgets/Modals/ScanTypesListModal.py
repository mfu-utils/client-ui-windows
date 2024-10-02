from PySide6.QtWidgets import QWidget

from App.Services.Client.ScanTypeService import ScanTypeService
from App.Widgets.Modals.ListModal import ListModal
from App.helpers import lc


class ScanTypesListModal(ListModal):
    def __init__(self, parent: QWidget = None):
        super(ScanTypesListModal, self).__init__(lc('toolBar.scan_types'), ScanTypeService, parent)
