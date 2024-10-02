import enum
import os
from typing import Optional, Union, List

from sqlalchemy import null
from sqlalchemy.orm import joinedload

from App.Core import Filesystem
from App.Models.Client.Scan import Scan, Format
from App.Models.Client.ScanTag import ScanTag
from App.Models.Client.ScanType import ScanType
from App.Services.Client.AbstractServiceWarning import AbstractServiceWarning
from App.Services.Client.DocumentService import DocumentService
from App.Services.Client.TagService import TagService
from App.helpers import now, platform
from App.Models.Client.Document import Type as DocumentType, Document
from App.helpers import logger

from config import HOME


SCAN_PATHS = {
    platform().WINDOWS: HOME / 'Documents',
    platform().LINUX: HOME,
    platform().DARWIN: HOME / 'Documents',
}

DEFAULT_SCAN_DIR = "Scans"

SCAN_TYPE = Union[ScanType, int, None]
TAGS_TYPE = Optional[List[str]]


class WarningCode(enum.Enum):
    CREATE_DIRECTORY = 1


class ErrorCode(enum.Enum):
    CANNOT_CREATE_DIRECTORY = 1


class ScanWarning(AbstractServiceWarning):
    __type__ = WarningCode


class ScanError(AbstractServiceWarning):
    __type__ = ErrorCode


class ScanService:
    def __init__(self, scan_directory: str):
        self.__scan_directory = scan_directory

    @staticmethod
    def last(limit: int = 10) -> list[Scan]:
        return (
            Scan
            .query()
            .order_by(Scan.id.desc())
            .options(joinedload(Scan.type), joinedload(Scan.tags), joinedload(Scan.documents))
            .limit(limit)
            .all()
        )

    @staticmethod
    def filter(page: int, per_items: int, parameters: dict) -> (int, list[Scan]):
        q = (
            Scan
            .query()
            .order_by(Scan.created_at.desc())
        )

        if _title := parameters.get('title'):
            q = q.filter(Scan.title.like(f"%{_title}%"))

        if _format := parameters.get('format'):
            if isinstance(_format, int):
                _format = Format(_format)

            # noinspection PyTypeChecker
            q = q.filter(Scan.format == _format)

        if _type := parameters.get('type'):
            q = q.filter(Scan.type == _type)

        if _tags := parameters.get('tags'):
            # TODO: Strong find by tags
            # if _strong_tags := parameters.get('strong_tags'):
            #     # noinspection PyTypeChecker
            #     q = q.filter(ScanTag.scan_id == Scan.id, ScanTag.tag_id.contains(_tags))
            # else:
            # noinspection PyTypeChecker
            q = q.filter(ScanTag.scan_id == Scan.id, ScanTag.tag_id.in_(_tags))

        if _doc_types := parameters.get('doc_types'):
            _doc_types = list(map(lambda x: DocumentType(x), _doc_types))

            # noinspection PyTypeChecker
            q = q.filter(Document.scan_id == Scan.id, Document.type.in_(_doc_types))

        return q.count(), q.offset((page - 1) * per_items).limit(per_items).all()

    @staticmethod
    def find(_id: int) -> Scan:
        return Scan().select().where(Scan.id == _id).one()

    @staticmethod
    def delete(scan: Scan):
        for tag in scan.tags:
            # noinspection PyTypeChecker
            ScanTag.query().filter(ScanTag.tag_id == tag.id, ScanTag.scan_id == scan.id).delete()

        scan.delete()

    @staticmethod
    def store(title: str, scan_type: SCAN_TYPE, path: str, _format: Format, tags: TAGS_TYPE = None) -> Scan:
        if isinstance(scan_type, ScanType):
            scan_type = scan_type.id

        _now = now()
        _type_id = null() if scan_type is None else scan_type

        scan = Scan.create(title=title, type_id=_type_id, path=path, format=_format, created_at=_now, updated_at=_now)

        for tag_model in TagService.save_list(tags):
            ScanTag.create(scan_id=scan.id, tag_id=tag_model.id)

        logger().success(f"Scan stored successfully '%s'" % scan.path, {'object': ScanService})

        return scan

    @staticmethod
    def get_scan_dir(_dir: Optional[str]) -> str:
        if not _dir:
            _dir = str(SCAN_PATHS[platform().name] / DEFAULT_SCAN_DIR)

        return _dir

    @staticmethod
    def get_scan_path(_dir: Optional[str], name: str, _format: Format) -> str:
        return os.path.join(ScanService.get_scan_dir(_dir), f"{name}.{_format.name.lower()}")

    @staticmethod
    def save(_dir: Optional[str], content: bytes, name: str, _format: Format) -> Union[ScanError, List[ScanWarning]]:
        path = ScanService.get_scan_path(_dir, name, _format)
        _dir = ScanService.get_scan_dir(_dir)

        warnings: List[ScanWarning] = []

        if not Filesystem.exists(_dir):
            os.makedirs(_dir, exist_ok=True)
            logger().warning("Save scan dir '%s' created" % path, {'object': ScanService})

            warnings.append(ScanWarning(WarningCode.CREATE_DIRECTORY, {'path': _dir}))

        try:
            res = Filesystem.write_file(path, content)
            err = ''
        except Exception as err:
            res = False
            err = str(err)

        if not res:
            return ScanError(ErrorCode.CANNOT_CREATE_DIRECTORY, {'path': path, 'msg': err})

        return warnings

    @staticmethod
    def store_converted(scan: Union[ScanType, int], _type: DocumentType, path: str):
        if isinstance(scan, Scan):
            scan = scan.id

        if _type in DocumentService.has_doc_types(scan):
            return

        scan = ScanService.find(scan)

        DocumentService.store(scan.id, _type, path)
