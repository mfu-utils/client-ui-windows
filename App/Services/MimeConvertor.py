import hashlib
import os
from enum import Enum
from typing import List, Optional, Union

import img2pdf
import docx2pdf

from App.Core import Filesystem, Config, MimeTypeConfig, Platform
from App.Core.Logger import Log
from App.Core.Utils import MimeType, OfficeSuite
from App.Subprocesses.LibreofficePdfConvert import LibreofficePdfConvert
from App.Subprocesses.AsposeConvert import AsposeConvert


class MimeConvertor:
    OFFICE_SUITE_NAMES = {
        OfficeSuite.MSWORD.value: "Microsoft Word",
        OfficeSuite.LIBREOFFICE.value: "Libreoffice",
        OfficeSuite.ASPOSE_LIBRAY.value: "Aspose (Restricted)"
    }

    def __init__(self, log: Log, _config: Config, mime: MimeTypeConfig, platform: Platform):
        self.__mime_type = mime

        self.__libreoffice_convert = LibreofficePdfConvert(log, _config, platform)
        self.__aspose_convertor = AsposeConvert(log, _config, platform)

        self.__debug = _config.get("printing.debug")
        self.__use_cached_docs = _config.get("printing.use_cached_docs")

        self.__log = log

    @staticmethod
    def suites(none: bool = True) -> List[Union[OfficeSuite, Enum]]:
        suites = [OfficeSuite.NONE] if none else []

        suites += [
            OfficeSuite.LIBREOFFICE,
            OfficeSuite.ASPOSE_LIBRAY,
        ]

        if not Platform.system_is(Platform.LINUX):
            suites.append(OfficeSuite.MSWORD)

        return suites

    @staticmethod
    def suites_values(none: bool = True) -> List[str]:
        return list(map(lambda x: x.value, MimeConvertor.suites(none)))

    @staticmethod
    def __get_unique_filename(path: str) -> str:
        _hash = str(hashlib.md5((f := open(path, 'rb')).read()).hexdigest())
        f.close()

        return _hash

    def __get_unique_filepath(self, path_from: str, extension: str) -> str:
        return Filesystem.create_tmp_path(self.__get_unique_filename(path_from) + f".{extension}")

    def __exists_path(self, path: str) -> bool:
        if not self.__use_cached_docs:
            return False

        return os.path.exists(path)

    def __get_converted_image_to_pdf(self, path_from: str) -> Optional[str]:
        path_to = self.__get_unique_filepath(path_from, MimeType.mime_extension(MimeType.PDF))

        if not self.__exists_path(path_to):
            if not Filesystem.write_file(path_to, img2pdf.convert(path_from)):
                return None

        return path_to

    def __get_converted_doc_by_aspose(self, path_from: str, extension: str) -> Optional[str]:
        path_to = self.__get_unique_filepath(path_from, extension)

        if not self.__exists_path(path_to):
            if not self.__aspose_convertor.convert(path_from, path_to):
                return None

        return path_to

    def __get_converted_doc_by_libreoffice(self, path_from: str, extension: str) -> Optional[str]:
        path_to = Filesystem.create_tmp_path(path_from.split('/')[-1].split('.')[0] + f".{extension}")

        if not self.__exists_path(path_to):
            return self.__libreoffice_convert.docx_convert(path_from, Filesystem.get_tmp_path(), extension)

        return path_to

    def __get_converted_doc_by_msword(self, path_from: str, extension: str) -> Optional[str]:
        path_to = self.__get_unique_filepath(path_from, extension)

        if not self.__exists_path(path_to):
            try:
                docx2pdf.convert(path_from, path_to)
            except BaseException as e:
                self.__log.error(f"Cannot convert file. {str(e)}")
                return None

            return None if not os.path.exists(path_to) else path_to

        return path_to

    def __get_converted_doc(self, path_from: str, extension: str, suite: OfficeSuite) -> Optional[str]:
        if suite == OfficeSuite.ASPOSE_LIBRAY:
            return self.__get_converted_doc_by_aspose(path_from, extension)

        if suite == OfficeSuite.MSWORD:
            return self.__get_converted_doc_by_msword(path_from, extension)

        if suite == OfficeSuite.LIBREOFFICE:
            return self.__get_converted_doc_by_libreoffice(path_from, extension)

        return None

    def convert_to_pdf(self, path: str, mime_type: MimeType, suite: OfficeSuite) -> Optional[str]:
        if mime_type in MimeType.doc_group():
            return self.__get_converted_doc(path, MimeType.mime_extension(MimeType.PDF), suite)

        if mime_type in MimeType.image_group():
            return self.__get_converted_image_to_pdf(path)

    def get_pdf(self, path: str, suite: OfficeSuite = OfficeSuite.NONE) -> Optional[str]:
        mime_type = self.__mime_type.get_mime_enum(path)

        if mime_type == MimeType.PDF:
            return path

        return self.convert_to_pdf(path, mime_type, suite)
