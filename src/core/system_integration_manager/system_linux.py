from src.core.logger import log
from src.core.system_integration_manager.system_interface import ISystemIntegration


class SystemIntegrationLinux(ISystemIntegration):
    def __init__(self):
        self.tray = None

    def setup_tray(self, app, main_window, enable: bool) -> object | None:
        # Desktop environment specifics should be implemented later
        log.info("Linux setup_tray called (no-op)")
        return None

    def set_startup(self, enable: bool) -> bool:
        # Implement systemd/user or autostart .desktop writing later
        log.info("Linux set_startup called (no-op)")
        return False

    def set_auto_login(self, enable: bool) -> None:
        from src.core.user_settings_manager import user_settings_manager

        user_settings_manager.set_auto_login(enable)

    def cleanup(self) -> None:
        return None
