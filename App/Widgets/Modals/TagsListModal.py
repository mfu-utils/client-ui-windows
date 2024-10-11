from PySide6.QtWidgets import QWidget

from App.Services.Client.TagService import TagService
from App.Widgets.Modals.ListModal import ListModal
from App.helpers import lc


class TagsListModal(ListModal):
    def __init__(self, parent: QWidget = None):
        super(TagsListModal, self).__init__(lc('toolBar.tags'), TagService, parent)
