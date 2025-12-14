from typing import Optional
from .system_interface import ISystemIntegration
from logger import log


class SystemIntegrationMacOS(ISystemIntegration):
    def __init__(self):
        self.tray = None

    def setup_tray(self, app, main_window, enable: bool) -> Optional[object]:
        log.info("macOS setup_tray called (no-op)")
        return None

    def set_startup(self, enable: bool) -> bool:
        log.info("macOS set_startup called (no-op)")
        return False

    def set_auto_login(self, enable: bool) -> None:
        from src import config_manager as cfg

        cfg.set_config_value("auto_login", bool(enable))

    def cleanup(self) -> None:
        return None
