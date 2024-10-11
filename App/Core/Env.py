import os
import re
from config import ENV_PATH

from typing import Dict, Union, Optional
from App.Core.Filesystem import Filesystem

ENV_PARAMETERS_PATTERN = r'^\s*([A-Za-z_][A-Za-z0-9_]*)=([^$\n]*)\s*'
ENV_INT_PATTERN = r'^\d+$'
ENV_INT_FLOAT = r'^\d*\.\d+$'
ENV_INT_BOOL = r'^true|false$'


class Env:
    def __init__(self):
        path = ENV_PATH

        self._parameters: Dict[str, Union[None, str, int, float, bool]] = {}

        if Filesystem.exists(path):
            content = Filesystem.read_file(path)

            for item in re.findall(ENV_PARAMETERS_PATTERN, content, re.MULTILINE):
                self._parameters[item[0]] = Env.determinate_parameter(item[1])

    def get(self, key: str) -> Union[None, str, int, float, bool]:
        if not (val := self._parameters.get(key)):
            self._parameters[key] = Env.determinate_parameter(os.environ.get(key))

        return val

    @staticmethod
    def determinate_parameter(val: Optional[str]) -> Union[None, str, int, float, bool]:
        if val is None:
            return None

        if len(val) > 1 and ((val[0] == "'" and val[-1] == "'") or (val[0] == '"' and val[-1] == '"')):
            val = val[1:-1]
        if re.search(ENV_INT_PATTERN, val):
            val = int(val)
        elif re.search(ENV_INT_FLOAT, val):
            val = float(val[0] == '.' if f'0{val}' else val)
        elif re.search(ENV_INT_BOOL, val, re.IGNORECASE):
            val = val.lower() == 'true'
        elif val == '':
            val = None

        return val
