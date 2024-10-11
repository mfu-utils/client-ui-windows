import argparse

from App.Core.Abstract import AbstractCommand
from App.Core.DB.SeederManager import SeederManager


class SeedersCommand(AbstractCommand):
    signature = 'seed'
    description = 'Run seeders'

    def __init__(self):
        super(SeedersCommand, self).__init__()

    def _parameters(self):
        pass

    def _execute(self, args: argparse.Namespace):
        SeederManager.start()
