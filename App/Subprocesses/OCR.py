import subprocess
from typing import List

from App.helpers import config, logger


class OCR:
    IMAGE_PATH_REPLACE = "$p"
    OUT_FILE_PATH_REPLACE = "$o"
    LANGUAGES_REPLACE = "$l"

    @staticmethod
    def convert(executed: str, template: str, path: str, out: str, langs_sep: str, langs: List[str]) -> int:
        langs = langs_sep.join(langs)

        cmd = " ".join([
            f'"{executed}"',
            template
            .replace(OCR.IMAGE_PATH_REPLACE, path)
            .replace(OCR.OUT_FILE_PATH_REPLACE, out)
            .replace(OCR.LANGUAGES_REPLACE, langs),
        ]).replace('\\', '\\\\')

        if config('convertor.debug_command'):
            logger().debug(f"Execute ocr convertor: `{cmd}`", {'object': OCR})
            return 0

        return subprocess.call(cmd)
