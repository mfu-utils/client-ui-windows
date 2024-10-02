from db.seeders.Seeder import Seeder
from App import Application


class SeederManager:
    @staticmethod
    def start():
        app = Application()

        app.register_type(Seeder, {'alias': 'seeder'})

        app.call(['seeder', 'run'])
