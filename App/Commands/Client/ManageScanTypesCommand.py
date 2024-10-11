import argparse

from App.Core.Abstract import AbstractCommand
from App.Services.Client.ScanTypeService import ScanTypeService


class ManageScanTypesCommand(AbstractCommand):
    signature = 'scan-types'
    help = 'Manage scan types'

    def __init__(self):
        super(ManageScanTypesCommand, self).__init__()
        self._types = ScanTypeService.all()

    def _parameters(self):
        subparser = self._argument_parser.add_subparsers(title='subjects')

        add_parser = subparser.add_parser('create', help='Create scan type')
        add_parser.add_argument('-n', '--name', help='Type name', required=True)
        add_parser.set_defaults(func=self._execute_add)

    def _execute_add(self, args: argparse.Namespace):
        name = args.name

        _type = ScanTypeService.create(name)

        # noinspection PyUnresolvedReferences
        self._output.success_message(f'Successfully created scan type (id: {_type.id})')

    def _execute(self, args: argparse.Namespace):
        self._output.header("Scan types:" if self._types else 'Scan types list EMPTY.')

        for scan_type in self._types:
            # noinspection PyUnresolvedReferences
            self._output.line(f"- {scan_type.name}", indent=2)
