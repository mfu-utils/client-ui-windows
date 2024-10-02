from typing import List

from App.Models.Client.Document import Type as DocumentType

from App.Models.Client.Scan import Scan
from App.Services.Client.DocConvertorService import DocConvertorService, ErrorCode, WarningCode
from App.Services.Client.DocConvertorService import CError as CError, CWarning as CWarning
from App.helpers import ini, events, notification, lc

CONVERT_ERRORS_TITLE = 'errors.convert_title'

LC_ERRORS = {
    ErrorCode.IMAGE_NOT_FOUND: (CONVERT_ERRORS_TITLE, 'errors.load_image_msg'),
    ErrorCode.LANGS_LIST_EMPTY: (CONVERT_ERRORS_TITLE, 'errors.langs_not_found'),
    ErrorCode.EXECUTED_NOT_FOUND: (CONVERT_ERRORS_TITLE, 'errors.executed_not_found'),
    ErrorCode.PARAMETERS_NOT_FOUND: (CONVERT_ERRORS_TITLE, 'errors.parameters_not_found'),
    ErrorCode.EXECUTE_ENGINE: (CONVERT_ERRORS_TITLE, 'errors.execute_engine'),
}

LC_WARNINGS = {
    WarningCode.CREATE_DIR: ('warning.create_dir_title', 'warning.create_dir_msg')
}


class UiDocConvertorService:
    @staticmethod
    def convertor() -> DocConvertorService:
        recognition_dir = ini('recognition.dir')
        execute = ini('ocr.path_to_executable')
        parameters = ini('ocr.parameters')
        sep = ini('ocr.langs_delimiter')

        return DocConvertorService(recognition_dir, execute, parameters, sep)

    @staticmethod
    def get_doc_dir() -> str:
        return UiDocConvertorService.convertor().get_doc_dir()

    @staticmethod
    def __err_convert(error: CError):
        parameters = ()

        if error.code() in [ErrorCode.IMAGE_NOT_FOUND, ErrorCode.EXECUTED_NOT_FOUND, ErrorCode.PARAMETERS_NOT_FOUND]:
            parameters = (error.parameters()['path'])

        if error.code() in [ErrorCode.EXECUTE_ENGINE]:
            parameters = (error.parameters()['code'])

        title, msg = LC_ERRORS[error.code()]

        notification().error(lc(title), lc(msg) % parameters)

    @staticmethod
    def __warning_convert(warning: CWarning):
        parameters = ()

        if warning.code() == WarningCode.CREATE_DIR:
            parameters = (warning.parameters()['path'])

        title, msg = LC_WARNINGS[warning.code()]

        notification().warning(lc(title), lc(msg) % parameters)

    @staticmethod
    def __convert_one(scan: Scan, _type: DocumentType, langs: [str]) -> bool:
        res = UiDocConvertorService.convertor().convert(scan, _type, langs)

        if isinstance(res, CError):
            if res.code() != ErrorCode.NO_ERROR:
                UiDocConvertorService.__err_convert(res)
                return False

        if isinstance(res, List):
            for item in res:
                item: CWarning

                UiDocConvertorService.__warning_convert(item)

        _type_name = DocConvertorService.TYPES[_type]['extension'].upper()

        notification().success(lc('success.convert_title'), lc('success.convert_msg') % (scan.title, _type_name))

        return True

    @staticmethod
    def convert_many(scan: Scan, _types: List[DocumentType], langs: [str]):
        for _type in _types:
            if not UiDocConvertorService.__convert_one(scan, _type, langs):
                return

        events().fire('update-history')

    @staticmethod
    def convert(scan: Scan, _type: DocumentType, langs: [str]):
        if not UiDocConvertorService.__convert_one(scan, _type, langs):
            return

        events().fire('update-history')
