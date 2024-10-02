from App.helpers import env

__CONFIG__ = {
    'debug': env('SUBPROCESSES_DEBUG', False),

    # host, wsl
    'target_platform_cmd': env('TARGET_PLATFORM_CMD', 'host'),
}
