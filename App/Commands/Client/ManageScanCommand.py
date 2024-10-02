import argparse
import os.path

from App.Core.Abstract import AbstractCommand
from App.Models.Client.Scan import Format
from App.Services.Client.ScanService import ScanService
from App.Services.Client.ScanTypeService import ScanTypeService
from config import CWD


class ManageScanCommand(AbstractCommand):
    signature = 'scan'
    help = 'Manage scan command'

    def __init__(self):
        super(ManageScanCommand, self).__init__()

        types = ScanTypeService.for_select()

        self._scan_types = list(types.values())
        self._scan_types_values = dict(map(lambda x: (x[1], x[0]), types.items()))

        self._formats = list(map(lambda x: x.name, list(Format)))

    def _parameters(self):
        subparser = self._argument_parser.add_subparsers(title='subjects')

        add_parser = subparser.add_parser('create', help='Create test scan')
        add_parser.add_argument('-n', '--name', help='Scan doc name', required=True)
        add_parser.add_argument('-t', '--type', help='Scan type', choices=self._scan_types)
        add_parser.add_argument('-g', '--tags', help='Scan tags list')
        add_parser.add_argument('-f', '--format', help='Scan format', choices=self._formats, default=Format.TIFF.name)
        add_parser.set_defaults(func=self.__execute_create)

        format_parser = subparser.add_parser('formats', help='Formats of scan')
        format_parser.set_defaults(func=self.__execute_formats)

    def _execute(self, _: argparse.Namespace):
        self._argument_parser.print_help()

    def __execute_formats(self, _: argparse.Namespace):
        self._output.header("Scan formats:")

        for _format in self._formats:
            self._output.line(f"- {_format}", indent=2)

    def __execute_create(self, args: argparse.Namespace):
        ScanService.store(
            args.name,
            self._scan_types_values[args.type] if args.type else None,
            os.path.join(CWD, "tests", "image.tiff"),
            Format[args.format],
            args.tags.split(',') if args.tags else []
        )

        self._output.success_message("Scan created successfully")
