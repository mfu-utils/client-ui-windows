from typing import Optional, Union, Dict

from App.Models.Client.Scan import Format, Scan
from App.Services.Client.ScanService import ScanService, SCAN_TYPE, TAGS_TYPE, WarningCode, ScanWarning, ScanError, ErrorCode
from App.helpers import events, notification, lc


LC_WARNINGS = {
    WarningCode.CREATE_DIRECTORY: ('warning.create_dir_title', 'warning.create_dir_msg')
}

LC_ERRORS = {
    ErrorCode.CANNOT_CREATE_DIRECTORY: ('cannot_create_file.title', 'cannot_create_file.msg')
}


class UiScanService(ScanService):
    @staticmethod
    def __create_msg(msg: Union[ScanError, ScanWarning], _lc: Dict, params: tuple) -> tuple:
        title, msg = _lc[msg.code()]

        tm = (lc(title), lc(msg) % params)

        return tm

    @staticmethod
    def __create_warning(warning: ScanWarning, params: tuple) -> tuple:
        params = UiScanService.__create_msg(warning, LC_WARNINGS, params)

        notification().warning(params[0], params[1])

        return params

    @staticmethod
    def __create_error(error: ScanError, params: tuple) -> tuple:
        params = UiScanService.__create_msg(error, LC_ERRORS, params)

        notification().error(params[0], params[1])

        return params

    @staticmethod
    def store(title: str, scan_type: SCAN_TYPE, path: str, _format: Format, tags: TAGS_TYPE = None) -> Scan:
        res = ScanService.store(title, scan_type, path, _format, tags)

        notification().success(lc('success.save_scan_title'), lc('success.save_scan_msg') % path)

        events().fire("update-history")

        return res

    @staticmethod
    def save(_dir: Optional[str], content: bytes, name: str, _format: Format) -> Optional[tuple]:
        res = ScanService.save(_dir, content, name, _format)

        if isinstance(res, ScanError):
            params = res.parameters()
            return UiScanService.__create_error(res, (params['path'], params['msg']))

        for warning in res:
            warning: ScanWarning

            if warning.code() == WarningCode.CREATE_DIRECTORY:
                UiScanService.__create_warning(warning, (warning.parameters()['path']))
