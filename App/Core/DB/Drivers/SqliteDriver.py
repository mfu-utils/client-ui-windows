from App.Core import Config
from App.Core.Abstract import AbstractDbDriver
from App.Core.Logger import Log


class SqliteDriver(AbstractDbDriver):
    def __init__(self, log: Log, config: Config):
        self.__params: dict = config.get('db.drivers.sqlite')
        super(SqliteDriver, self).__init__(log)

    def creds(self) -> str:
        return 'sqlite:///' + (':memory:' if self.__params['memory'] else self.__params['path'])
