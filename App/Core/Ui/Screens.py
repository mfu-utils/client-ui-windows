from typing import Tuple, Dict, Optional

from App.Core.Cache import CacheManager

import json


class Screens:
    SECTION = "screens"

    def __init__(self, cache: CacheManager):
        self.__cache = cache

    @staticmethod
    def __prepare_screen_name(screen_name: str) -> str:
        return screen_name.replace('\\', '%5C').replace('.', '%43')

    def set_screen_parameters(self, screen_name: str, pos: Tuple[int, int], size: Tuple[int, int]):
        screen_name = self.__prepare_screen_name(screen_name)

        self.__cache.set(f"{Screens.SECTION}.{screen_name}", json.dumps({'name': screen_name, 'pos': [pos[0], pos[1]], 'size': [size[0], size[1]]}))
        self.__cache.set(f"{Screens.SECTION}.current_screen_name", screen_name)

    def get_current_screen_name(self) -> Optional[str]:
        if name := self.__cache.get(f"{Screens.SECTION}.current_screen_name"):
            return name.replace('%5C', '\\').replace('%43', '.')

        return name

    def get_screen_parameters(self, screen_name: str) -> Optional[Dict[str, Tuple[int, int]]]:
        screen_name = self.__prepare_screen_name(screen_name)

        screen_name = f"{Screens.SECTION}.{screen_name}"

        if not self.__cache.has(screen_name):
            return None

        obj = json.loads(self.__cache.get(screen_name))

        return {
            'pos': (obj['pos'][0], obj['pos'][1]),
            'size': (obj['size'][0], obj['size'][1]),
        }
