from .network_interface import INetwork
from .network_linux import NetworkLinux
from .network_macos import NetworkMacOS
from .network_windows import NetworkWindows

__all__ = [
    "INetwork",
    "NetworkWindows",
    "NetworkLinux",
    "NetworkMacOS",
]
