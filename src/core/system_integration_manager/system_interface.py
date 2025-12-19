from abc import ABC, abstractmethod


class ISystemIntegration(ABC):
    """系统集成接口：托盘、开机启动、自动登录等与操作系统强耦合的功能。"""

    @abstractmethod
    def setup_tray(self, app, main_window, enable: bool) -> object | None:
        """Create or remove a system tray integration.

        Return an opaque tray object or None.
        """
        raise NotImplementedError

    @abstractmethod
    def set_startup(self, enable: bool) -> bool:
        """Enable or disable application startup on login."""
        raise NotImplementedError

    @abstractmethod
    def set_auto_login(self, enable: bool) -> None:
        """Enable or disable the auto-login behavior (store config)."""
        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup any created resources (tray icons etc)."""
        raise NotImplementedError
