import argparse

from App.Core.Abstract import AbstractCommand
from App.Core.Console import Output
from App.Core.Network.Client import ClientConfig
from App.Services import PrinterService
from App.helpers import app


class PrintersCommand(AbstractCommand):
    signature = "printers"
    help = "Printers management"

    def __init__(self):
        super().__init__()

        self.__console: Output = app().get('console.output')
        self.__network_manager = app().get('network.manager')

        self.__services = PrinterService(app().get('cache'), app().get('log'), app().get('config'), self.__console)

    def _parameters(self):
        subparser = self._argument_parser.add_subparsers(title='subjects')

        list_parser = subparser.add_parser('list', help='Create list of printers')
        list_parser.add_argument('-l', '--local', help='Use command locale', action="store_true")
        list_parser.set_defaults(func=self._exec_get_list)

        update_cache_parser = subparser.add_parser('update', help='Update printers cache (Only local)')
        update_cache_parser.add_argument('-o', '--out', help='Show printers list', action="store_true")
        update_cache_parser.set_defaults(func=self._exec_update_cache)

    def _exec_update_cache(self, args: argparse.Namespace):
        out = args.out or False

        if not self.__services.update_printers_cache():
            self.__console.endl()
            self.__console.error_message('Printers cache update failed')
            return

        if out:
            self.__services.printers_console_out(self.__services.get_printers())
            return

        self.__console.endl()
        self.__console.success_message('Printers cache updated')

    def _exec_get_list(self, args: argparse.Namespace):
        local = args.local or False

        printers = (
            self.__services.get_printers()
            if local
            else self.__services.get_printers_by_network(ClientConfig.client(), self.__network_manager)
        )

        self.__services.printers_console_out(printers)

    def _execute(self, args: argparse.Namespace):
        pass
