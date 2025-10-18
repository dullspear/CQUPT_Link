from .platform_interface import IPlatform
from src.network_manager import NetworkMacOS
from src.network_manager import INetwork
from src.system_integration_manager import ISystemIntegration, SystemIntegrationMacOS


class PlatformMacOS(IPlatform):
    def name(self) -> str:
        return "macos"

    def get_network_manager(self) -> INetwork:
        return NetworkMacOS()

    def get_system_integration(self) -> ISystemIntegration:
        return SystemIntegrationMacOS()
