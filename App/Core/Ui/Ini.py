from typing import Any, Optional

from App.Core import Config

import configparser

from App.Core.Utils.Ui import Casts


class Ini:
    def __init__(self, config: Config):
        self.path = config.get('ui.ini_path')

        self.data = None

        self.load()

    def load(self):
        self.data = configparser.ConfigParser()
        self.data.read(self.path)

    def get(self, dot_path: str, _type: Optional[type] = None) -> Any:
        try:
            section, option = dot_path.split('.')

            data = self.data.get(section, option)

            if _type is not None:
                return Casts.str_to(data, _type)

            return data
        except ValueError:
            return None

    def set(self, dot_path: str, value):
        section, option = dot_path.split('.')

        self.data.set(section, option, str(value))

    def write(self):
        with open(self.path, 'w') as configfile:
            self.data.write(configfile)

        self.load()
