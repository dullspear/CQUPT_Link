from __future__ import annotations

from src.core.network_manager import INetwork, NetworkLinux
from src.core.system_integration_manager import (
    ISystemIntegration,
    SystemIntegrationLinux,
)

from .platform_interface import IPlatform


class PlatformLinux(IPlatform):
    def name(self) -> str:
        return "linux"

    def get_network_manager(self) -> INetwork:
        return NetworkLinux()

    def get_system_integration(self) -> ISystemIntegration:
        return SystemIntegrationLinux()
