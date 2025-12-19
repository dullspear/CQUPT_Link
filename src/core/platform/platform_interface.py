from abc import ABC, abstractmethod

from src.core.network_manager import INetwork
from src.core.system_integration_manager import ISystemIntegration


class IPlatform(ABC):
    """
    平台命令接口，定义所有平台命令的共同接口。
    """

    @abstractmethod
    def get_network_manager(self) -> INetwork:
        raise NotImplementedError

    @abstractmethod
    def get_system_integration(self) -> ISystemIntegration:
        raise NotImplementedError
