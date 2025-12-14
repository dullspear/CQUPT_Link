from __future__ import annotations


from .platform_interface import IPlatform
from src.network_manager import NetworkLinux
from src.network_manager import INetwork
from src.system_integration_manager import ISystemIntegration, SystemIntegrationLinux


class PlatformLinux(IPlatform):
    def name(self) -> str:
        return "linux"

    def get_network_manager(self) -> INetwork:
        return NetworkLinux()

    def get_system_integration(self) -> ISystemIntegration:
        return SystemIntegrationLinux()
