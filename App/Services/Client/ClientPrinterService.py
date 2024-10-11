from typing import Optional, List

from App.Core import Filesystem
from App.Core.Network import NetworkManager
from App.Core.Network.Client import ClientConfig, ResponseDataPromise
from App.Core.Network.Protocol import CallRequest
from App.Core.Network.Protocol.Responses.AbstractResponse import AbstractResponse
from App.Core.Utils import MimeType, DocumentOrder, DocumentPagesUtil
from App.Core.Utils.Ui.PrintingPagePolicy import PrintingPagePolicy
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
            self
            .send_to_print_one(self._network_manager, printing_doc, count_pages, ClientConfig.client_ui())
            .then(success)
            .catch(error)
        )

        if sync:
            promise.wait_result()

        return promise

    def send_to_print_one(
        self, manager: NetworkManager, doc: PrintingDocumentDTO, max_page: int, client: ClientConfig
    ) -> ResponseDataPromise:
        if not doc.file:
            raise Exception("Cannot send document to printer without a file")

        if not doc.mime_type:
            raise Exception("Cannot send document to printer without a mime type")

        parameters = {
            "device": doc.device,
            "copies": doc.copies,
            "paper-size": doc.paper_size.name,
            "file": doc.file
        }

        if tray := doc.paper_tray:
            parameters.update({"paper-tray": tray.name})

        if pages_policy := doc.pages_policy:
            if ints := self.__resolve_pages_parameters(pages_policy, doc.pages, max_page):
                parameters.update({"pages": ints})

        if doc.order != DocumentOrder.Normal:
            parameters.update({"order": doc.order.name})

        if doc.mirror:
            parameters.update({"mirror": True})

        if doc.landscape:
            parameters.update({"landscape": True})

        if doc.transparency:
            parameters.update({"transparency": True})

        if mime_type := doc.mime_type:
            parameters.update({"mime-type": mime_type.name})

        return manager.request(CallRequest("print", parameters=parameters), client)

    @staticmethod
    def __resolve_pages_parameters(policy: PrintingPagePolicy, pages: str, max_page: int) -> List[int]:
        if policy == PrintingPagePolicy.Custom and len(ints := DocumentPagesUtil.cups_unpack(pages, max_page)) > 0:
            return ints

        elif policy == PrintingPagePolicy.Even and len(ints := [*range(2, max_page + 1)]) > 0:
            return ints

        elif policy == PrintingPagePolicy.NotEven and len(ints := [*range(1, max_page + 1)]) > 0:
            return ints

        return []

    @staticmethod
    def get_printers_promise(client: ClientConfig, manager: NetworkManager, update_cache: bool = False) -> ResponseDataPromise:
        parameters = {}

        if update_cache:
            parameters.update({"update-cache": update_cache})

        return manager.request(
            CallRequest(PrinterService.PRINTERS_COMMAND, [PrinterService.PRINTERS_SUBCOMMAND_LIST], parameters),
            client,
        )

    @staticmethod
    def get_printers_use_cache_promise(client: ClientConfig, manager: NetworkManager):
        return manager.request(
            CallRequest(PrinterService.PRINTERS_COMMAND, [PrinterService.PRINTERS_SUBCOMMAND_USE_CACHE]),
            client,
        )

    def get_printers_by_network(self, client: ClientConfig, manager: NetworkManager, update_cache: bool = False) -> List[dict]:
        ok, response = self.get_printers_promise(client, manager, update_cache).wait_result()

        if not ok:
            self._logger.error(f"Cannot get printers list. {response}", {"object": self})
            return []

        return response.data() or []

    def get_printers_use_cache_by_network(self, client: ClientConfig, manager: NetworkManager) -> bool:
        ok, response = self.get_printers_use_cache_promise(client, manager).wait_result()

        if not ok:
            self._logger.error(f"Cannot get printers use cache flag. {response}", {"object": self})
            return False

        return response.data() or False
