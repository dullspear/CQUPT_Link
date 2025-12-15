"""配置管理模块

提供配置文件的加载、保存和访问功能。
"""

import json
import os

from src.core.logger import log


class ConfigManager:
    """配置管理器类，用于管理应用配置"""

    def __init__(self, config_file_path, default_config=None):
        """初始化配置管理器

        Args:
            config_file_path: 配置文件路径
            default_config: 默认配置字典
        """
        self.config_file_path = config_file_path
        self.default_config = default_config
        self.load_config()

    def load_config(self) -> dict:
        """加载配置文件

        Returns:
            dict: 配置字典
        """
        if not os.path.exists(self.config_file_path):
            if self.default_config is not None:
                with open(self.config_file_path, "w", encoding="utf-8") as f:
                    json.dump(self.default_config, f, indent=4)
                return self.default_config.copy()
            else:
                with open(self.config_file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4)
                return {}
        else:
            with open(self.config_file_path, encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    if self.default_config is not None:
                        data = self.default_config.copy()
                    else:
                        data = {}
                    self.save_config(data)
            if self.default_config is not None:
                for k, v in self.default_config.items():
                    if k not in data:
                        data[k] = v
            return data

    def save_config(self, config: dict) -> None:
        """保存配置到文件

        Args:
            config: 配置字典
        """
        with open(self.config_file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def get_config_value(self, key, default=None):
        """获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值

        Raises:
            KeyError: 当配置键不存在且未提供默认值时
        """
        config = self.load_config()
        if key in config:
            return config[key]
        if default is not None:
            return default
        log.error(f"Config key '{key}' not found and no default provided.")
        raise KeyError(f"Config key '{key}' not found")

    def set_config_value(self, key, value):
        """设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        config = self.load_config()
        config[key] = value
        self.save_config(config)

    def delete_config_key(self, key):
        """删除配置键

        Args:
            key: 配置键

        Returns:
            bool: 是否成功删除
        """
        config = self.load_config()
        if key in config:
            del config[key]
            self.save_config(config)
            return True
        return False

    def list_config(self):
        """列出所有配置

        Returns:
            dict: 配置字典
        """
        return self.load_config()
