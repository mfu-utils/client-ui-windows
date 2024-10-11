from typing import Dict, Type

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from App.Models.Client.Tag import Tag
from App.Services.Client.AbstractListService import AbstractListService
from App.Widgets.Components.ListItem import ListItem
from App.Widgets.Modals.AbstractListModal import AbstractListModal
from App.helpers import events, lc


class ListModal(AbstractListModal):
    def __init__(self, title: str, service: Type[AbstractListService], parent: QWidget = None):
        self.__items: Dict[int, ListItem] = {}
        self.__service: Type[AbstractListService] = service

        super(ListModal, self).__init__(title, parent)

    def _on_delete(self, model: Tag, text: str):
        self.__items.pop(model.id)
        model.delete()

        events().fire("update-history")

    def _on_rename(self, model: Tag, text: str):
        item: ListItem = self.__items[model.id]

        if not self.__service.rename(model, text):
            item.set_error(lc("listModal.errors.update_exists") % (model.name, text, text))

            return

        item.rename(text)

        events().fire("update-history")

        return

    def _on_create(self, text: str):
        _type = self.__service.create(text)

        if not _type:
            self.set_error(lc("listModal.errors.create_exists") % text)

            return

        # noinspection PyUnresolvedReferences
        item = self._create_item(_type, _type.name)

        self._list_layout.insertWidget(0, item)

        # noinspection PyUnresolvedReferences
        self.__items.update({_type.id: item})

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self._save_new_item()
        else:
            super(ListModal, self).keyReleaseEvent(event)

    def _init_list(self):
        for scan_type in self.__service.reversed():
            # noinspection PyUnresolvedReferences
            item = self._create_item(scan_type, scan_type.name)

            self._list_layout.addWidget(item)

            # noinspection PyUnresolvedReferences
            self.__items.update({scan_type.id: item})
