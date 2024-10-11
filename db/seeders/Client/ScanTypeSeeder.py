from App.Core.Abstract.AbstractSeeder import AbstractSeeder
from App.Models.Client.ScanType import ScanType

types = [
    # Default Types
]


class ScanTypeSeeder(AbstractSeeder):
    def run(self):
        for name in types:
            ScanType.create(name=name)
