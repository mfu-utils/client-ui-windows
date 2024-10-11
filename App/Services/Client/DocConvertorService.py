import enum
from typing import Dict, List, Union
import os

from App.Core import Filesystem
from App.Models.Client.Document import Type as DocumentType
from App.Models.Client.Language import Language
from App.Models.Client.Scan import Scan
from App.Services.Client.AbstractServiceError import AbstractServiceError
from App.Services.Client.AbstractServiceWarning import AbstractServiceWarning
from App.Subprocesses.OCR import OCR
from App.helpers import platform, config, logger
from App.Services.Client.DocumentService import DocumentService
from config import HOME

DOC_PATHS = {
    platform().WINDOWS: HOME / 'Documents',
    platform().DARWIN: HOME / 'Documents',
    platform().LINUX: HOME,
}


class ErrorCode(enum.Enum):
    NO_ERROR = 1
    IMAGE_NOT_FOUND = 2
    LANGS_LIST_EMPTY = 3
    EXECUTED_NOT_FOUND = 4
    PARAMETERS_NOT_FOUND = 5
    EXECUTE_ENGINE = 6


class WarningCode(enum.Enum):
    NO_WARNING = 1
    CREATE_DIR = 2


class CError(AbstractServiceError):
    __type__ = ErrorCode


class CWarning(AbstractServiceWarning):
    __type__ = WarningCode


class DocConvertorService:
    TYPES = {
        DocumentType.PDF: {
            'name': 'PDF Document',
            'extension': 'pdf',
        },
        DocumentType.MS_WORD: {
            'name': 'Microsoft Word',
            'extension': 'docx',
        },
        DocumentType.TXT: {
            'name': 'Text document',
            'extension': 'txt',
        },
        DocumentType.HTML: {
            'name': 'HTML Document',
            'extension': 'html',
        },
        DocumentType.RTF: {
            'name': 'Rich Text Format',
            'extension': 'rtf',
        },
        DocumentType.CSV: {
            'name': 'CSV Document',
            'extension': 'csv',
        },
        DocumentType.ODT: {
            'name': 'OpenDocument Text',
            'extension': 'odt',
        },
        DocumentType.FB2: {
            'name': 'FB2 Document',
            'extension': 'fb2',
        },
        DocumentType.EPUB: {
            'name': 'EPUB Document',
            'extension': 'epub',
        }
    }

    # TODO: Temporary version
    CONVERTOR_LANGS = {
        'english': 'English',
        'russian': 'Russian',
        'azeri_latin': 'AzeriLatin',
        'bashkir': 'Bashkir',
        'bulgarian': 'Bulgarian',
        'catalan': 'Catalan',
        'croatian': 'Croatian',
        'czech': 'Czech',
        'danish': 'Danish',
        'dutch': 'Dutch',
        'dutch_belgian': 'DutchBelgian',
        'estonian': 'Estonian',
        'finnish': 'Finnish',
        'french': 'French',
        'german': 'German',
        'german_new_spelling': 'GermanNewSpelling',
        'hebrew': 'Hebrew',
        'hungarian': 'Hungarian',
        'indonesian': 'Indonesian',
        'italian': 'Italian',
        'korean': 'Korean',
        'korean_hangul': 'KoreanHangul',
        'latvian': 'Latvian',
        'lithuanian': 'Lithuanian',
        'norwegian_bokmal': 'NorwegianBokmal',
        'norwegian_nynorsk': 'NorwegianNynorsk',
        'polish': 'Polish',
        'portuguese_brazilian': 'PortugueseBrazilian',
        'portuguese_standard': 'PortugueseStandard',
        'romanian': 'Romanian',
        'slovak': 'Slovak',
        'slovenian': 'Slovenian',
        'spanish': 'Spanish',
        'swedish': 'Swedish',
        'tatar': 'Tatar',
        'turkish': 'Turkish',
        'ukrainian': 'Ukrainian',
        'vietnamese': 'Vietnamese',
    }

    SPACE_DELIMITER = ":SPACE:"

    def __init__(self, recognition_dir: str, path_to_executable: str, execute_parameters: str, langs_delimiter: str):
        self.__recognition_dir = recognition_dir
        self.__path_to_executable = path_to_executable
        self.__langs_delimiter = langs_delimiter
        self.__execute_parameters = execute_parameters

        self.__debug_mode = config('ocr_convertor.debug')

    def get_doc_dir(self) -> str:
        _dir = self.__recognition_dir

        if not self.__recognition_dir:
            _dir = str(DOC_PATHS[platform().name])

        return _dir

    def get_doc_type_dir(self, _type: DocumentType) -> str:
        return os.path.join(self.get_doc_dir(), DocConvertorService.TYPES[_type]['name'])

    def get_document_path(self, name: str, _type: DocumentType) -> str:
        return os.path.join(
            self.get_doc_type_dir(_type),
            f"{name}.{DocConvertorService.TYPES[_type]['extension']}",
        )

    @staticmethod
    def langs() -> Dict[str, str]:
        return dict(map(lambda x: (x.name, x.title), Language.query().all()))

    @staticmethod
    def get_convertors() -> dict:
        return dict(map(
            lambda x: (str(x[0].value), f"(.{x[1]['extension']}) {x[1]['name']}"),
            DocConvertorService.TYPES.items()
        ))

    def __convert_err(self, title: str, error: ErrorCode, params: dict = None) -> CError:
        for key, param in params.items():
            title = title.replace(f"%{param}", params[param])

        logger().error(title, {'object': self})

        return CError(error, params)

    def convert(self, scan: Scan, _type: DocumentType, langs: List[str]) -> Union[CError, List[CWarning]]:
        if not self.__debug_mode:
            if not Filesystem.exists(self.__path_to_executable):
                return self.__convert_err(f"Cannot find executable '%path'.", ErrorCode.EXECUTED_NOT_FOUND, {
                    'path': self.__path_to_executable,
                })

        if not (parameters := self.__execute_parameters):
            return self.__convert_err(f"Parameters for executable '%path' not found.", ErrorCode.PARAMETERS_NOT_FOUND, {
                'path': self.__path_to_executable,
            })

        if not len(langs):
            return self.__convert_err(f"Langs list empty.", ErrorCode.LANGS_LIST_EMPTY)

        if not Filesystem.exists(scan.path):
            return self.__convert_err(f"Cannot find image '%path'.", ErrorCode.IMAGE_NOT_FOUND, {
                'path': scan.path,
            })

        warnings: List[CWarning] = []

        out_path = self.get_doc_type_dir(_type)
        if not Filesystem.exists(out_path):
            os.makedirs(out_path, exist_ok=True)
            logger().warning(f"Create directory '{out_path}' due to dir not found.", {'object': self})

            warnings.append(CWarning(WarningCode.CREATE_DIR, {'path': out_path}))

        if (sep := self.__langs_delimiter) == DocConvertorService.SPACE_DELIMITER:
            sep = ' '

        out = self.get_document_path(scan.title, _type)
        langs = list(map(lambda x: DocConvertorService.CONVERTOR_LANGS[x], langs))

        if code := OCR.convert(self.__path_to_executable, parameters, scan.path, out, sep, langs):
            return self.__convert_err(f"OCR engine executed with error code (%code).", ErrorCode.EXECUTE_ENGINE, {
                'code': str(code),
            })

        DocumentService.store(scan.id, _type, out)

        return warnings
