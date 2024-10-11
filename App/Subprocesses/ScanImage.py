import os
from typing import Tuple, Union

from App.Core import Config, Filesystem
from App.Core.Abstract import AbstractSubprocess
from App.Core.Logger import Log
from App.Core.Utils import DocumentsRealSizes, DocumentMediaType
from config import CWD


class ScanImage(AbstractSubprocess):
    SCANIMAGE_PARAMETER_OUTPUT = 'output'
    SCANIMAGE_PARAMETER_FORMAT_DEVICE_LIST = 'formatted-device-list'
    SCANIMAGE_PARAMETER_DONT_SCAN = 'dont-scan'
    SCANIMAGE_PARAMETER_X = 'x'
    SCANIMAGE_PARAMETER_Y = 'y'
    SCANIMAGE_PARAMETER_MEDIA = 'media'

    FORMAT = ','.join(['%i', '%d', '%v', '%m', '%t%n'])

    def __init__(self, log: Log, config: Config):
        super().__init__(log, config, 'scanimage')

        self.__file_path = config.get('scan.tmp_file')
        self.__scan_debug = config.get('scan.debug')

        self.set_multi_character_parameters_delimiter('=')

    def __resolve_media_type(self, parameters: dict) -> dict:
        if not (media := parameters.get(ScanImage.SCANIMAGE_PARAMETER_MEDIA)):
            return parameters

        media = DocumentMediaType[media]

        x, y = DocumentsRealSizes.size(media)
        parameters.pop(ScanImage.SCANIMAGE_PARAMETER_MEDIA)

        parameters.update({self.SCANIMAGE_PARAMETER_X: x, self.SCANIMAGE_PARAMETER_Y: y})

        return parameters

    def __create_scan_tmp_dir(self):
        if not Filesystem.exists(_dir := os.path.dirname(self.__file_path)):
            self._log.warning(f"Create scan tmp directory '{_dir}'")
            os.makedirs(os.path.dirname(self.__file_path), exist_ok=True)

    def scan(self, parameters: dict) -> Tuple[bool, Union[str, bytes]]:
        parameters.update({ScanImage.SCANIMAGE_PARAMETER_OUTPUT: self.create_windows_path_for_linux(self.__file_path)})

        try:
            ok, message = self.run(parameters=self.__resolve_media_type(parameters))
        except Exception as e:
            self._log.error(message := f"Cannot run scanimage. {e}")
            return False, message

        if self.__scan_debug:
            self._log.warning(f'Scan debug mode enabled. Return test data. Scanning parameters: {parameters}')

            return True, Filesystem.read_file(str(os.path.join(CWD, "tests", "images", f"demo.{parameters['format']}")), True)

        self.__create_scan_tmp_dir()

        if ok:
            return True, Filesystem.read_file(self.__file_path, True)

        self._log.error(message := f'Failed to scan: {message}')

        return False, message

    def device_list(self) -> list:
        ok, content = self.run(parameters={
            self.SCANIMAGE_PARAMETER_DONT_SCAN: True,
            self.SCANIMAGE_PARAMETER_FORMAT_DEVICE_LIST: self.FORMAT
        })

        devices = []

        if not ok:
            return devices

        for device_data in content.split('\n'):
            parameters = device_data.split(',')

            devices.append({
                'model': parameters[3],
                'vendor': parameters[2],
                'device': parameters[1],
                'index': parameters[0],
                'type': parameters[4].split(' '),
            })

        return devices
