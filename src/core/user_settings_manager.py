"""用户设置管理模块

提供用户设置的统一管理接口。
"""

import os

from src.core.config_manager import ConfigManager

# 配置文件路径
CONFIG_FILE_PATH = os.path.join(os.getcwd(), "config.json")

# 默认配置
DEFAULT_CONFIG = {
    "interval": 62,
    # feature flags
    "remember_credentials": True,
    "startup": False,
    "auto_login": False,
    "tray": False,
}


class UserSettingsManager:
    """用户设置管理器

    提供各种用户设置的获取和设置方法。
    """

    def __init__(self, config_file_path, default_config=None):
        """初始化用户设置管理器

        Args:
            config_file_path: 配置文件路径
            default_config: 默认配置字典
        """
        self.config_manager = ConfigManager(
            config_file_path=config_file_path, default_config=default_config
        )

    def set_startup(self, enable: bool, name: str = "CQUPT_Link") -> bool:
        """设置开机启动

        Args:
            enable: 是否启用
            name: 应用名称

        Returns:
            bool: 是否设置成功

        Note:
            TODO: 考虑删除此方法
        """
        try:
            from src.core.factory import Factory

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
        """获取是否自动登录"""
        return self.config_manager.get_config_value("auto_login", False)

    def set_auto_login(self, enable: bool) -> None:
        """设置是否自动登录"""
        self.config_manager.set_config_value("auto_login", bool(enable))

    def get_tray(self) -> bool:
        """获取是否启用托盘"""
        return self.config_manager.get_config_value("tray", False)

    def set_tray(self, enable: bool) -> None:
        """设置是否启用托盘"""
        self.config_manager.set_config_value("tray", bool(enable))

    def get_interval(self) -> int:
        """获取心跳间隔时间（秒）"""
        return self.config_manager.get_config_value("interval", 62)

    def set_interval(self, interval: int) -> None:
        """设置心跳间隔时间（秒）"""
        self.config_manager.set_config_value("interval", int(interval))

    def get_remember_credentials(self) -> bool:
        """获取是否记住密码"""
        return self.config_manager.get_config_value("remember_credentials", False)

    def set_remember_credentials(self, enable: bool) -> None:
        """设置是否记住密码"""
        self.config_manager.set_config_value("remember_credentials", bool(enable))

    def get_startup(self) -> bool:
        """获取是否开机启动"""
        return self.config_manager.get_config_value("startup", False)

    def get_show_close_to_tray_reminder(self) -> bool:
        """获取是否显示关闭到托盘提醒弹窗

        Returns:
            bool: True 表示显示提醒，False 表示不显示
        """
        return self.config_manager.get_config_value("show_close_to_tray_reminder", True)

    def set_show_close_to_tray_reminder(self, show: bool) -> None:
        """设置是否显示关闭到托盘提醒弹窗"""
        self.config_manager.set_config_value("show_close_to_tray_reminder", bool(show))

    def get_encoding(self) -> str:
        """获取编码格式（用于 deprecated 代码）

        Returns:
            str: 编码格式，默认为 'utf-8'
        """
        return self.config_manager.get_config_value("encoding", "utf-8")

    def set_encoding(self, encoding: str) -> None:
        """设置编码格式（用于 deprecated 代码）

        Args:
            encoding: 编码格式字符串
        """
        self.config_manager.set_config_value("encoding", encoding)

    # Deprecated methods - 不推荐使用的通用方法
    def get(self, key):
        """获取配置值（通用方法）

        .. deprecated::
            使用具体的 get_xxx 方法代替，例如 get_encoding()

        Note:
            TODO: 考虑删除此方法
        """
        return self.config_manager.get_config_value(key)

    def set(self, key, value):
        """设置配置值（通用方法）

        .. deprecated::
            使用具体的 set_xxx 方法代替，例如 set_encoding()

        Note:
            TODO: 考虑删除此方法
        """
        self.config_manager.set_config_value(key, value)

    def list(self):
        """列出所有配置

        .. deprecated::
            不推荐直接访问所有配置，使用具体的 get_xxx 方法

        Note:
            TODO: 考虑删除此方法
        """
        return self.config_manager.list_config()


# 模块级别单例
user_settings_manager: UserSettingsManager = UserSettingsManager(
    config_file_path=CONFIG_FILE_PATH, default_config=DEFAULT_CONFIG
)
