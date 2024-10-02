import os

from App.Core import Config
from App.Core.DataFiles import JsonDataFile
from App.Core.Ui import Ini
from config import LANGS_DIR


class Lang:
    buffer = {}

    def __init__(self, config: Config, ini: Ini):
        self.langs = config.get('langs.all')
        self.current_lang = ini.get('app.lang')

    def load_lang_file(self, name: str):
        self.buffer[name] = JsonDataFile(str(os.path.join(LANGS_DIR, self.current_lang, f"{name}.json")))

    def has_lang_file(self, name: str):
        return bool(self.buffer.get(name))

    def get_langs(self) -> dict:
        return self.langs

    def get_locale(self, dot_path: str):
        segments = dot_path.split('.')

        if not self.has_lang_file(name := segments[0]):
            self.load_lang_file(name)

        lang_file = self.buffer[name]

        if dot_path == name:
            return lang_file.data()

        return lang_file.get(segments[1:])
