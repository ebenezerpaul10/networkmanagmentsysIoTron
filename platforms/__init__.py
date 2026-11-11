"""
NetShield-IoT: Platforms Package
Factory and unified entry point for platform adapters.
"""

import platform
from platforms.base import AbstractPlatformAdapter
from platforms.linux import LinuxPlatformAdapter
from platforms.windows import WindowsPlatformAdapter
from platforms.macos import MacOSPlatformAdapter

_CURRENT_ADAPTER: AbstractPlatformAdapter = None

def get_platform_adapter() -> AbstractPlatformAdapter:
    """Returns the singleton platform adapter for the current operating system."""
    global _CURRENT_ADAPTER
    if _CURRENT_ADAPTER is None:
        sys_name = platform.system()
        if sys_name == "Windows":
            _CURRENT_ADAPTER = WindowsPlatformAdapter()
        elif sys_name == "Darwin":
            _CURRENT_ADAPTER = MacOSPlatformAdapter()
        else:
            _CURRENT_ADAPTER = LinuxPlatformAdapter()
    return _CURRENT_ADAPTER
