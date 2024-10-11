from App.Core.Abstract.AbstractSeeder import AbstractSeeder
from db.seeders.Client.LanguagesSeeder import LanguagesSeeder
from db.seeders.Client.ScanTypeSeeder import ScanTypeSeeder


class Seeder(AbstractSeeder):
    def run(self):
        self._group([
            ScanTypeSeeder,
            LanguagesSeeder,
        ])
