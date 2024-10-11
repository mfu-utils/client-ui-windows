from dataclasses import dataclass

from App import Application
from App.Core import Config
from App.Core.Ui import Ini


@dataclass
class ClientConfig:
    address: str
    port: int
    max_bytes_receive: int
    debug: bool
    timeout: int

    def to_dict(self) -> dict:
        return {
            'address': self.address,
            'port': self.port,
            'max_bytes_receive': self.max_bytes_receive,
            'debug': self.debug,
            'timeout': self.timeout,
        }

    @staticmethod
    def ini() -> Ini:
        return Application().get('ui.ini')

    @staticmethod
    def config() -> Config:
        return Application().get('config')

    @staticmethod
    def client_ui():
        ini = ClientConfig.ini()
        config = ClientConfig.config().get('client')

        return ClientConfig(
            address=ini.get('network.address'),
            port=ini.get('network.port', int),
            max_bytes_receive=config['max_bytes_receive'],
            debug=config['debug'],
            timeout=ini.get('network.timeout', int)
        )

    @staticmethod
    def client():
        conf = ClientConfig.config().get('client')

        client_config = ClientConfig(
            address=conf['address'],
            port=conf['port'],
            max_bytes_receive=conf['max_bytes_receive'],
            debug=conf['debug'],
            timeout=conf['timeout'],
        )

        return client_config
