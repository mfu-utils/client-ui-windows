from abc import ABC, abstractmethod
import argparse
from typing import Optional

from App.Core.Console.Output import Output


class AbstractCommand(ABC):
    signature = ''
    help = ''

    def __init__(self):
        super(AbstractCommand, self).__init__()
        self._output: Optional[Output] = None
        self._argument_parser: Optional[argparse.ArgumentParser] = None

    def init_parser(self, subparsers, output: Output):
        self._output = output

        self._argument_parser = subparsers.add_parser(name=self.signature, help=self.help)

        self._parameters()

        self._argument_parser.set_defaults(func=self._execute)

    def _parameters(self):
        pass

    @abstractmethod
    def _execute(self, args: argparse.Namespace):
        pass
