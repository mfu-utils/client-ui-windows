from App.helpers import env
from config import STATIC_APP_NAME

debug = bool(env("DEBUG", False))

__CONFIG__ = {
    # App name
    "name": "MfuUtils (Develop)" if debug else STATIC_APP_NAME,

    # Enable debug mode
    "debug": debug,
}
