from App.Models.Client.ScanType import ScanType
from App.Services.Client.AbstractListService import AbstractListService


class ScanTypeService(AbstractListService):
    __type__ = ScanType
