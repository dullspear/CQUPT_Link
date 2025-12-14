from src.config_manager import ConfigManager
import os

# file_path = "config.json"
CONFIG_FILE_PATH = os.path.join(os.getcwd(), "config.json")
DEFAULT_CONFIG = {
    "interval": 62,
    # feature flags
    "remember_credentials": True,
    "startup": False,
    "auto_login": False,
    "tray": False,
}


class UserSettingsManager:
    def __init__(self, config_file_path, default_config=None):
        self.config_manager = ConfigManager(
            config_file_path=config_file_path, default_config=default_config
        )

    def set_startup(self, enable: bool, name: str = "CQUPT_Link") -> bool:
        # TODO: 删除此方法
        """Enable or disable startup on the host platform."""
        try:
            from src.factory import Factory

            integration = Factory.create_system_integration()
            if hasattr(integration, "set_startup"):
                ok = integration.set_startup(enable)
                self.config_manager.set_config_value("startup", bool(enable))
                return bool(ok)
        except Exception:
            pass
        self.config_manager.set_config_value("startup", bool(enable))
        return False

    def get_auto_login(self) -> bool:
        return self.config_manager.get_config_value("auto_login", False)

    def set_auto_login(self, enable: bool) -> None:
        self.config_manager.set_config_value("auto_login", bool(enable))

    def get_tray(self) -> bool:
        return self.config_manager.get_config_value("tray", False)

    def set_tray(self, enable: bool) -> None:
        self.config_manager.set_config_value("tray", bool(enable))

    def get_interval(self) -> int:
        return self.config_manager.get_config_value("interval", 62)

    def get_remember_credentials(self) -> bool:
        return self.config_manager.get_config_value("remember_credentials", False)

    def set_remember_credentials(self, enable: bool) -> None:
        self.config_manager.set_config_value("remember_credentials", bool(enable))

    def get_startup(self) -> bool:
        return self.config_manager.get_config_value("startup", False)

    def set_interval(self, interval: int) -> None:
        self.config_manager.set_config_value("interval", int(interval))

    # 托盘关闭提醒相关
    def get_show_close_to_tray_reminder(self) -> bool:
        """是否显示关闭到托盘提醒弹窗,默认 True,即显示提醒弹窗"""
        return self.config_manager.get_config_value("show_close_to_tray_reminder", True)

    def set_show_close_to_tray_reminder(self, show: bool) -> None:
        self.config_manager.set_config_value("show_close_to_tray_reminder", bool(show))

    # TODO: 该方法是否理应删除？
    def get(self, key):
        return self.config_manager.get_config_value(key)

    # TODO: 该方法是否理应删除？
    def set(self, key, value):
        self.config_manager.set_config_value(key, value)

    # TODO: 该方法是否理应删除？
    def list(self):
        return self.config_manager.list_config()


# 模块级别单例
user_settings_manager: UserSettingsManager = UserSettingsManager(
    config_file_path=CONFIG_FILE_PATH, default_config=DEFAULT_CONFIG
)
