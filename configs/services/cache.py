import os

from App.helpers import env
from config import CACHE_PATH, STATIC_APP_NAME

__CONFIG__ = {
    # Driver for cache accessible
    # Drivers: file, memory
    "default": env("CACHE_DRIVER", "file"),

    "drivers": {
        "file": {
            # Path of cache storage
            "path": os.path.join(CACHE_PATH, "storage.cache"),
        },
    },

    # Prefix for database based cache services
    "prefix": env("CACHE_PREFIX", STATIC_APP_NAME).replace("-", "_") + "_cache_",
}
