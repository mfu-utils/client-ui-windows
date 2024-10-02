from abc import ABC
from typing import Optional, List, Tuple, Union
import platform

from App.Core import Config
from App.Core.Logger import Log
import subprocess


class AbstractSubprocess(ABC):
    TARGET_PLATFORM_CMD_HOST = 'host'
    TARGET_PLATFORM_CMD_WSL = 'wsl'

    WINDOWS_C_ROOT_DIR = '/mnt/c/'

    TARGETS_PLATFORMS_CMD = [
        TARGET_PLATFORM_CMD_HOST,
        TARGET_PLATFORM_CMD_WSL,
    ]

    def __init__(self, log: Log, config: Config, command: Union[List[str], str], remote_cmd: bool = True):
        self._command: Union[List[str], str] = command

        if isinstance(command, str):
            self._command = [command]

        self._log = log
        self._config = config.get('subprocesses')

        self._multi_character_parameters_delimiter = None
        self._multi_character_parameters_wrap = True
        self._multi_character_parameters_prefix = '--'
        
        self._once_character_parameters_delimiter = None
        self._once_character_parameters_prefix = '-'

        self._target_platform_cmd = self._config.get('target_platform_cmd')
        self._remote_cmd = remote_cmd

        if self._target_platform_cmd not in self.TARGETS_PLATFORMS_CMD:
            raise Exception(f'Remote targets not supported ({self._target_platform_cmd}).')

    def set_command_is_remote(self, enable: bool):
        self._remote_cmd = enable

    def set_multi_character_parameters_delimiter(self, delimiter: str):
        self._multi_character_parameters_delimiter = delimiter

        return self

    def set_multi_character_parameters_wrap(self, wrap: bool):
        self._multi_character_parameters_wrap = wrap

        return self

    def set_multi_character_parameters_prefix(self, prefix: str):
        self._multi_character_parameters_prefix = prefix

        return self

    def set_once_character_parameters_delimiter(self, delimiter: str):
        self._once_character_parameters_delimiter = delimiter

        return self

    def set_once_character_parameters_prefix(self, prefix: str):
        self._once_character_parameters_prefix = prefix

        return self

    def create_windows_path_for_linux(self, path: str):
        return path.replace('C:\\', self.WINDOWS_C_ROOT_DIR).replace('\\', '/')

    def __create_multi_character_parameter_name(self, parameter: str) -> str:
        return f"{self._multi_character_parameters_prefix}{parameter}"

    def __create_once_character_parameter_name(self, parameter: str) -> str:
        return f"{self._once_character_parameters_prefix}{parameter}"

    def __create_multi_character_parameter(self, parameter: str, value: str) -> List[str]:
        parameter = self.__create_multi_character_parameter_name(parameter)

        if value is None:
            return [parameter] if self._multi_character_parameters_wrap else parameter.split(' ')

        if type(value) is bool:
            return [parameter] if value else []

        value = str(value)

        if not self._multi_character_parameters_delimiter:
            return [parameter, value]

        res = f"{parameter}{self._multi_character_parameters_delimiter}{str(value)}"

        return [res] if self._multi_character_parameters_wrap else res.split(' ')

    def __create_once_character_parameter(self, parameter: str, value: str) -> List[str]:
        parameter = self.__create_once_character_parameter_name(parameter)

        if type(value) is bool:
            return [parameter] if value else []

        value = str(value)

        if not self._once_character_parameters_delimiter:
            return [parameter, value]

        return [f"{parameter}{self._once_character_parameters_delimiter}{str(value)}"]

    def _create_parameter(self, name: str, value: str) -> List[str]:
        if len(name) > 1:
            return self.__create_multi_character_parameter(name, value)

        return self.__create_once_character_parameter(name, value)

    def __create_parameters(self, parameters: dict) -> list:
        formated = []

        for key, value in parameters.items():
            list(map(lambda x: formated.append(x), self._create_parameter(key, value)))

        return formated

    def __get_command(self) -> List[str]:
        if self._remote_cmd and self._target_platform_cmd == self.TARGET_PLATFORM_CMD_WSL:
            return ['wsl', *self._command]

        return self._command

    @staticmethod
    def __to_str(parameters: List[str]) -> str:
        wrapped = []

        for parameter in parameters:
            wrapped.append(f'"{parameter}"' if ' ' in parameter else parameter)

        return " ".join(wrapped)

    def run(
        self,
        subcommands: Optional[list] = None,
        parameters: Optional[dict] = None,
        options: dict = None
    ) -> Tuple[bool, str]:
        options = options or {}

        if subcommands is None:
            subcommands = []

        if parameters is None:
            parameters = {}

        if isinstance(options.get('additional'), str):
            options['additional'] = [options.get('additional')]

        cmd = [
            *self.__get_command(),
            *subcommands,
            *self.__create_parameters(parameters),
            *(options.get('additional') or [])
        ]

        self._log.debug(f"Running subprocess: `{self.__to_str(cmd)}`", {'object': self})

        if self._config['debug']:
            self._log.warning(f'Subprocess debug mode enabled. Command NOT EXECUTED!!!.')

            return True, ""

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=options.get('input'))

        out_name = options.get("output")

        if out_name == "join":
            encoding = "cp1251" if platform.system() == 'Windows' else "utf-8"
            out = result.stdout.decode(encoding).strip()
            err = result.stderr.decode(encoding).strip()
            data = f"\n@Stdout:\n{out}\n\n@Stderr:\n{err}"
        else:
            data = (
                result.__getattribute__(out_name or 'stderr' if result.returncode > 0 else 'stdout')
                .decode("utf-8")
                .strip()
            )

        if result.returncode > 0:
            self._log.error(f'Error. {data}', {'object': self})
            return False, data

        self._log.success(f"Success process. `{self.__to_str(cmd)}`", {'object': self})
        return True, data
