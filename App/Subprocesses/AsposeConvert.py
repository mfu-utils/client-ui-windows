import os
from typing import List

from App.Core import Config, Platform
from App.Core.Abstract import AbstractSubprocess
from App.Core.Logger import Log
from config import CWD, BUILD_TYPE, EXECUTABLE


class AsposeConvert(AbstractSubprocess):
    SCRIPT_NAME = 'aspose_convert'

    def __init__(self, log: Log, config: Config, platform: Platform):
        self.__platform = platform

        super(AsposeConvert, self).__init__(log, config, self.get_converter_exec(), False)

    def get_converter_exec(self) -> List[str]:
        if self.__platform == Platform.WINDOWS:
            if BUILD_TYPE:
                return [os.path.join(CWD, f"{self.SCRIPT_NAME}.exe")]
            else:
                return [EXECUTABLE, os.path.join(CWD, self.SCRIPT_NAME)]

        return [EXECUTABLE, os.path.join(CWD, self.SCRIPT_NAME)]

    def convert(self, path_from: str, path_to) -> bool:
        ok, out = self.run([path_from, path_to])

        if (not ok) or (not os.path.exists(path_to)):
            self._log.error(f"Aspose failed to convert. {out}", {"object": self})
            return False

        return True
