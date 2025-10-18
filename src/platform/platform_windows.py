from src.platform.platform_interface import IPlatform
from src.network_manager import NetworkWindows
from src.system_integration_manager import ISystemIntegration, SystemIntegrationWindows


class PlatformWindows(IPlatform):
    def name(self) -> str:
        return "windows"

    def get_network_manager(self) -> NetworkWindows:
        return NetworkWindows()

    def get_system_integration(self) -> ISystemIntegration:
        return SystemIntegrationWindows()
