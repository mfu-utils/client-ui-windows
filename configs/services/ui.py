from App.helpers import env
from config import INI_PATH

__CONFIG__ = {
    "ini_path": env("APP_INI_PATH", INI_PATH),

    # Parameters for 'Main window'
    'rect': {'min-width': 600, 'min-height': 500},

    # Cache built styles into cache
    'non-cache-styles-for-debug': env('NON_CACHE_STYLES_FOR_DEBUG', True),

    # Create shadow for frameless window (For Windows os)
    'shadow-offset': 100,

    # Offset for create moving area for frameless windows (For Windows os)
    'frameless-drawable-top-offset': 40,

    # Enable shadows
    'shadow-enabled': True
}
