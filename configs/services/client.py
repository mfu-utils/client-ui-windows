from App.helpers import env

__CONFIG__ = {
    # Socket hostname
    'address': env('CLIENT_ADDRESS', '0.0.0.0'),

    # Socket port
    'port': env('CLIENT_PORT', 9587),

    # Max len of socket packet (32 Kb)
    'max_bytes_receive': env("CLIENT_MAX_BYTES_RECEIVE", 1024 * 32),

    # Show debug messages from client connection
    'debug': env("CLIENT_CONNECTION_DEBUG", False),

    'timeout': env("CLIENT_CONNECTION_TIMEOUT", 60),
}
