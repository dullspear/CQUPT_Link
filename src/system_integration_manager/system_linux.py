from typing import Optional
from logger import log
from src.system_integration_manager.system_interface import ISystemIntegration


class SystemIntegrationLinux(ISystemIntegration):
    def __init__(self):
        self.tray = None

    def setup_tray(self, app, main_window, enable: bool) -> Optional[object]:
        # Desktop environment specifics should be implemented later
        log.info("Linux setup_tray called (no-op)")
        return None

    def set_startup(self, enable: bool) -> bool:
        # Implement systemd/user or autostart .desktop writing later
        log.info("Linux set_startup called (no-op)")
        return False

    def set_auto_login(self, enable: bool) -> None:
        from src import config_manager as cfg

        cfg.set_config_value("auto_login", bool(enable))

    def cleanup(self) -> None:
        return None
