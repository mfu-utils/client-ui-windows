from typing import Optional

from App.Core import Filesystem
from App.Core.Network.Client import ClientConfig, ResponseDataPromise
from App.Core.Network.Protocol.Responses.AbstractResponse import AbstractResponse
from App.Core.Utils import MimeType
from App.DTO.Client import PrintingDocumentDTO
from App.Services import PrinterService
from App.helpers import cache, logger, config, console, network_manager


class ClientPrinterService(PrinterService):
    def __init__(self):
        super(ClientPrinterService, self).__init__(cache(), logger(), config(), console())

        self._network_manager = network_manager()

    def on_success_print(self, device: str, path: str, response: AbstractResponse):
        self._logger.success(f"Success send to response ({device}). {response.data()}", {'object': self})

    def on_error_print(self, device: str, path: str, message: Optional[str]):
        self._logger.error(f"Cannot send to printing ({device}). {message or ''}", {'object': self})

    def send_to_print(
        self,
        printing_doc: PrintingDocumentDTO,
        count_pages: int,
        path: str,
        converted_path: Optional[str],
        on_success: callable,
        on_error: callable,
        sync: bool = False
    ) -> ResponseDataPromise:
        if printing_doc.send_converted and converted_path:
            printing_doc.mime_type = MimeType.PDF
            printing_doc.file = Filesystem.read_file(converted_path, True)
        else:
            printing_doc.file = Filesystem.read_file(path, True)

        def success(response: AbstractResponse):
            self.on_success_print(printing_doc.device, path, response)
            on_success()

        def error(msg: Optional[str]):
            self.on_error_print(printing_doc.device, path, msg)
            on_error()

        promise = (
            super(ClientPrinterService, self)
            .send_to_print_one(self._network_manager, printing_doc, count_pages, ClientConfig.client_ui())
            .then(success)
            .catch(error)
        )

        if sync:
            promise.wait_result()

        return promise
