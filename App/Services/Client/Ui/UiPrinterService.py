from typing import Optional

from App.Core.Network.Protocol.Responses.AbstractResponse import AbstractResponse
from App.Services.Client.ClientPrinterService import ClientPrinterService
from App.helpers import notification, lc


class UiPrinterService(ClientPrinterService):
    def on_success_print(self, device: str, path: str, response: AbstractResponse):
        super(UiPrinterService, self).on_success_print(device, path, response)

        notification().success(lc('success.printing_title'), lc('success.printing_msg') % path)

    def on_error_print(self, device: str, path: str, message: Optional[str]):
        super(UiPrinterService, self).on_error_print(device, path, message)

        notification().error(lc('errors.printing_title'), lc('errors.printing_msg') % path)

