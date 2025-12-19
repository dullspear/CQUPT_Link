from src.core.network_manager import INetwork, NetworkMacOS
from src.core.system_integration_manager import (
    ISystemIntegration,
    SystemIntegrationMacOS,
)

from .platform_interface import IPlatform


class PlatformMacOS(IPlatform):
    def name(self) -> str:
        return "macos"

    def get_network_manager(self) -> INetwork:
        return NetworkMacOS()

    def get_system_integration(self) -> ISystemIntegration:
        return SystemIntegrationMacOS()
