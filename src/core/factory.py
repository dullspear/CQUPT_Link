"""工厂类模块

提供平台相关对象的创建工厂。
"""

import platform

from src.core.network_manager import (
    INetwork,
    NetworkLinux,
    NetworkMacOS,
    NetworkWindows,
)
from src.core.platform import IPlatform, PlatformLinux, PlatformMacOS, PlatformWindows
from src.core.system_integration_manager import (
    ISystemIntegration,
    SystemIntegrationLinux,
    SystemIntegrationMacOS,
    SystemIntegrationWindows,
)


class Factory:
    """工厂类，根据当前平台创建相应的实现对象"""

    @staticmethod
    def create_platform() -> IPlatform:
        """创建平台相关对象

        Returns:
            IPlatform: 平台实现对象

        Raises:
            ValueError: 当平台不支持时
        """
        platform_name = platform.system()

        if platform_name == "Windows":
            return PlatformWindows()
        elif platform_name == "Linux":
            return PlatformLinux()
        elif platform_name == "Darwin":  # macOS
            return PlatformMacOS()
        else:
            raise ValueError(f"Unsupported platform: {platform_name}")

    @staticmethod
    def create_network() -> INetwork:
        """创建网络管理对象

        Returns:
            INetwork: 网络管理实现对象

        Raises:
            ValueError: 当平台不支持时
        """
        platform_name = platform.system()

        if platform_name == "Windows":
            return NetworkWindows()
        elif platform_name == "Linux":
            return NetworkLinux()
        elif platform_name == "Darwin":  # macOS
            return NetworkMacOS()
        else:
            raise ValueError(f"Unsupported platform: {platform_name}")

    @staticmethod
    def create_system_integration() -> ISystemIntegration:
        """创建系统集成对象

        Returns:
            ISystemIntegration: 系统集成实现对象

        Raises:
            ValueError: 当平台不支持时
        """
        platform_name = platform.system()

        if platform_name == "Windows":
            return SystemIntegrationWindows()
        elif platform_name == "Linux":
            return SystemIntegrationLinux()
        elif platform_name == "Darwin":  # macOS
            return SystemIntegrationMacOS()
        else:
            raise ValueError(f"Unsupported platform: {platform_name}")
