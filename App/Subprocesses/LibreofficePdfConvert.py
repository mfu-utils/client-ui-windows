import os
from typing import Optional

from App.Core import Config, Platform
from App.Core.Abstract import AbstractSubprocess
from App.Core.Logger import Log


class LibreofficePdfConvert(AbstractSubprocess):
    MACOS_LIBREOFFICE_BIN_PATH = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    LINUX_LIBREOFFICE_COMMAND = "soffice"
    WINDOWS_LIBREOFFICE_BIN_PATH = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"

    def __init__(self, log: Log, config: Config, platform: Platform):
        self.__platform = platform

        super(LibreofficePdfConvert, self).__init__(log, config, self.__determinate_bin_path(), False)

    def __determinate_bin_path(self) -> Optional[str]:
        if self.__platform.is_darwin():
            return self.__determinate_macos_bin_path()

        if self.__platform.is_windows():
            return self.__determinate_windows_bin_path()

        if self.__platform.is_linux():
            return self.__determinate_linux_bin_path()

    def __determinate_linux_bin_path(self) -> Optional[str]:
        ok, out = self.run(["command", "v", self.LINUX_LIBREOFFICE_COMMAND])

        if not ok:
            return out

        return None

    def __determinate_windows_bin_path(self) -> Optional[str]:
        if not os.path.exists(self.WINDOWS_LIBREOFFICE_BIN_PATH):
            return None

        if os.path.isdir(self.WINDOWS_LIBREOFFICE_BIN_PATH):
            return None

        return self.WINDOWS_LIBREOFFICE_BIN_PATH

    def __determinate_macos_bin_path(self) -> Optional[str]:
        if not os.path.exists(self.MACOS_LIBREOFFICE_BIN_PATH):
            return None

        if os.path.isdir(self.MACOS_LIBREOFFICE_BIN_PATH):
            return None

        return self.MACOS_LIBREOFFICE_BIN_PATH

    def docx_convert(self, path: str, tmp_dir: str, extension: str) -> Optional[str]:
        if not (_bin := self.__determinate_bin_path()):
            self._log.error("No binaries found for Libreoffice. Please install Libreoffice.", {"object": self})
            return None

        ok, out = self.run(
            parameters={"headless": True, "convert-to": extension, "outdir": tmp_dir},
            options={"additional": [path], "output": "join"}
        )

        path = os.path.join(tmp_dir, '.'.join(path.split(os.path.sep)[-1].split('.')[:-1]) + f".{extension}")

        if self._config['debug']:
            return path

        if (not ok) or (not os.path.exists(path)):
            self._log.error(f"Libreoffice failed to convert. {out}", {"object": self})
            return None

        return path
