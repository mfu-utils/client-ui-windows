import os
import re
from enum import Enum
from typing import List

from App.Core import Config, Filesystem
from App.Core.Cache import CacheManager
from App.Core.Console import Output
from App.Core.Logger import Log
from App.Core.Network import NetworkManager
from App.Core.Network.Client import ClientConfig, ResponseDataPromise
from App.Core.Network.Protocol import CallRequest
from App.Core.Utils import DocumentPagesUtil, DocumentOrder
from App.Core.Utils.Ui import Patterns
from App.Core.Utils.Ui.PrintingPagePolicy import PrintingPagePolicy
from App.DTO.Client import PrintingDocumentDTO
from App.Subprocesses import LpstatSubprocess
from App.Subprocesses.LpinfoSubprocess import LpinfoSubprocess
from config import CWD


class PrinterService:
    REGEX_IP = re.compile(Patterns.IP)
    REGEX_SPACES = re.compile("\\s+")

    PRINTER_PARAMETER_DISPLAY_NAME = "display_name"
    PRINTER_PARAMETER_AVAILABLE = "available"
    PRINTER_PARAMETER_HIDDEN = "hidden"
    PRINTER_PARAMETER_DEVICE = "device"
    PRINTER_PARAMETER_INDEX = "index"
    PRINTER_PARAMETER_SCOPE = "scope"
    PRINTER_PARAMETER_NAME = "name"

    NETWORK_PROTOCOLS = ["lpd", "ipp", "ipps", "dnssd", "http", "https", "smb", "socket"]
    FILTER_PROTOCOLS = ["lpd"]

    CACHE_PRINTER_DATA = "printers_devices"

    PRINTERS_COMMAND = "printers"

    PRINTERS_SUBCOMMAND_USE_CACHE = "use_cache"
    PRINTERS_SUBCOMMAND_LIST = "list"

    INDENT = 2

    def __init__(self, cache: CacheManager, logger: Log, config: Config, console: Output):
        self._cache = cache
        self._logger = logger
        self._config = config
        self._console = console

        self.__use_cache_devices = config.get("printing.use_cached_devices")
        self.__debug = config.get("printing.debug")

    class Scope(Enum):
        Network = 1
        Local = 2

    @staticmethod
    def __determinate_scope(proto: str) -> Scope:
        return (
            PrinterService.Scope.Network
            if proto in PrinterService.NETWORK_PROTOCOLS
            else PrinterService.Scope.Local
        )

    @staticmethod
    def __create_device_object(parameters: tuple, direct_devices: list) -> dict:
        proto = parameters[1].split(":")[0]

        scope = PrinterService.__determinate_scope(proto)
        display_name = PrinterService.__create_display_name(parameters[0])

        return {
            PrinterService.PRINTER_PARAMETER_AVAILABLE: parameters[1] in direct_devices,
            PrinterService.PRINTER_PARAMETER_DISPLAY_NAME: display_name,
            PrinterService.PRINTER_PARAMETER_DEVICE: parameters[1],
            PrinterService.PRINTER_PARAMETER_NAME: parameters[0],
            PrinterService.PRINTER_PARAMETER_SCOPE: scope.value,
            PrinterService.PRINTER_PARAMETER_HIDDEN: proto in PrinterService.FILTER_PROTOCOLS,
        }

    @staticmethod
    def filter_hidden_devices(devices: List[dict]) -> List[dict]:
        return list(filter(lambda x: not x[PrinterService.PRINTER_PARAMETER_HIDDEN], devices))

    def printers_console_out(self, printers: List[dict]):
        self._console.endl()
        self._console.header("Printers:")

        if not printers:
            self._console.line("Empty printers list", indent=self.INDENT)

        for printer in printers:
            scope = PrinterService.Scope(printer[PrinterService.PRINTER_PARAMETER_SCOPE])

            self._console.header(f"- {printer[self.PRINTER_PARAMETER_DISPLAY_NAME]}:")
            self._console.line(indent=self.INDENT, message=f"Name:      {printer[self.PRINTER_PARAMETER_NAME]}")
            self._console.line(indent=self.INDENT, message=f"Scope:     {scope.name}")
            self._console.line(indent=self.INDENT, message=f"Device:    {printer[self.PRINTER_PARAMETER_DEVICE]}")
            self._console.line(indent=self.INDENT, message=f"Hidden:    {printer[self.PRINTER_PARAMETER_HIDDEN]}")
            self._console.line(indent=self.INDENT, message=f"Available: {printer[self.PRINTER_PARAMETER_AVAILABLE]}")
            self._console.endl()

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

    @staticmethod
    def __create_display_name(name: str) -> str:
        name = name.replace("_", " ").strip()

        if PrinterService.REGEX_IP.match(ip_name := name.replace(" ", ".")):
            return ip_name

        return PrinterService.REGEX_SPACES.sub(" ", name)

    def update_printers_cache(self) -> bool:
        ok, devices = LpstatSubprocess(self._logger, self._config).get_printers_list()

        if not ok:
            return False

        ok, dev = LpinfoSubprocess(self._logger, self._config).get_direct_devices()

        if not ok:
            return False

        self._cache.set(self.CACHE_PRINTER_DATA, list(map(lambda x: self.__create_device_object(x, dev), devices)))

        return True

    def get_printers(self, force_cache_update: bool = False) -> List[dict]:
        if self.__debug:
            return Filesystem.read_json(os.path.join(CWD, "tests", "dictionaries", "devices.json"))

        has_devices = self._cache.has(self.CACHE_PRINTER_DATA)

        if (not has_devices) or (not self.__use_cache_devices) or force_cache_update:
            if not self.update_printers_cache():
                return []

        return self._cache.get(self.CACHE_PRINTER_DATA)

    @staticmethod
    def __resolve_pages_parameters(policy: PrintingPagePolicy, pages: str, max_page: int) -> List[int]:
        if policy == PrintingPagePolicy.Custom and len(ints := DocumentPagesUtil.cups_unpack(pages, max_page)) > 0:
            return ints

        elif policy == PrintingPagePolicy.Even and len(ints := [*range(2, max_page + 1)]) > 0:
            return ints

        elif policy == PrintingPagePolicy.NotEven and len(ints := [*range(1, max_page + 1)]) > 0:
            return ints

        return []

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
