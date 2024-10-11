from App.helpers import env, platform


__CONFIG__ = {
    # Enable all debug info
    "debug": env("PRINTING_LIST_MODAL_DEBUG", False),

    # Check document what has been convert previously
    "use_cached_docs": env("PRINTING_USE_CACHED_DOCUMENTS", False),

    # Save printer in cache for slow commands. Example: macOS local using.
    "use_cached_devices": env("PRINTING_USE_CACHED_DEVICES", False),

    "server_side_convert_tool": env(
        "PRINTING_SERVER_SIDE_CONVERT_TOOL",
        "msword" if platform().is_windows() else "libreoffice"
    ),
}

