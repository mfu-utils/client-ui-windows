import os.path

from config import SQLITE_PATH
from App.helpers import env


__CONFIG__ = {
    'driver': env('DB_DRIVER', 'sqlite'),

    'drivers': {
        'sqlite': {
            'path': os.path.join(SQLITE_PATH, "default.db"),

            # If this flag is 'True' path was ignored
            'memory': env('SQLITE_DB_IN_MEMORY', False)
        }
    },
}
