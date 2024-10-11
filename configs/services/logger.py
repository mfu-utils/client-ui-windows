from App.helpers import env
from config import LOGS_PATH

__CONFIG__ = {

    # Channel for logger output stream
    # Channels: stdout, single, daily, stack
    "default": env("LOG_CHANNEL", "stack"),

    "channels": {
        "stdout": {
            # Log levels ascii colors
            "colors": {
                "info": "#3F74BA",
                "error": "#D64D5B",
                "warning": "#E4B40F",
                "success": "#5B9561",
                "debug": "#415294",
            },

            # Wrap by ascii colors
            "colorize": True,

            "level": "debug"
        },
        "single": {
            "path": f"{LOGS_PATH}/sane-util.log",
            "level": "error",
        },
        "daily": {
            "days": 14,
            "path": f"{LOGS_PATH}/sane-util.log",
            "level": "error",
        },
        "stack": {
            "channels": ["single", "stdout"],
        }
    },
}
