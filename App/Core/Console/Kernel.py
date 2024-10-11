import argparse
import os
from importlib import import_module

from App.Core import Config
from App.Core.Console.Output import Output

from config import COMMANDS_NAMESPACES, ROOT


class Kernel:
    DISABLED_FILES = [
        '__init__.py',
        '__init__.pyc',
        '__init__.pyo',
        '__pycache__',
    ]

    def __init__(self, config: Config, output: Output):
        self.__parser = argparse.ArgumentParser(description=config.get('app.name'))
        self.__subparsers = self.__parser.add_subparsers(title='commands')
        self.__output = output

    def init(self):
        for namespace in COMMANDS_NAMESPACES:
            self.scan_dir(namespace, f'{ROOT}/{namespace.replace(".", "/")}')

        args = self.__parser.parse_args()

        if not vars(args):
            self.__parser.print_usage()
        else:
            args.func(args)

        print()

    def scan_dir(self, namespace: str, path: str):
        files = os.listdir(path)

        for file_path in files:
            file_name = file_path.split('/')[-1]

            if file_name in self.DISABLED_FILES:
                continue

            if os.path.isdir(file_path):
                self.scan_dir(f"{namespace}.{file_name}", file_path)
                continue

            if not file_name.endswith('Command.py'):
                continue  # Skip

            name = file_name[:-3]

            command = import_module(f"{namespace}.{name}").__getattribute__(name)

            command().init_parser(self.__subparsers, self.__output)
