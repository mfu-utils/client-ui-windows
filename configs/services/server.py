from App.helpers import env

__CONFIG__ = {
    # Socket listen
    "max_incoming_connections": env("SERVER_MAX_INCOMING_CONNECTION", 10),

    # Socket hostname
    "address": env("SERVER_ADDRESS", "0.0.0.0"),

    # Socket port
    "port": env("SERVER_PORT", 9587),

    # Max len of socket packet (64 Kb)
    "max_bytes_receive": env("SERVER_MAX_BYTES_RECEIVE", 1024 * 64),

    # Reuse socket if down
    "reuse_socket": env("SERVER_PORT_CAN_REUSE", True),

    # Die when the main thread dies
    "daemon": env("SERVER_DAEMON", False),

    # Show debug messages for server connection
    "debug": env("SERVER_DEBUG_CONNECTIONS", False),
}
