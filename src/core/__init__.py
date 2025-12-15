"""核心业务逻辑模块

提供应用的核心功能，包括：
- 日志管理 (logger)
- 数据库操作 (database)
- 配置管理 (config_manager)
- 用户设置管理 (user_settings_manager)
- 工厂类 (factory)
- 登出服务 (logout_service)
- Web 自动化服务 (web_service)
"""

from .config_manager import ConfigManager
from .database import ConnectDb
from .factory import Factory
from .logout_service import (
    fuck_user,
    fuck_user1,
    fuck_user2,
    print_user_info,
    query_user_info,
)
from .user_settings_manager import UserSettingsManager, user_settings_manager

__all__ = [
    # Database
    "ConnectDb",
    # Config
    "ConfigManager",
    "UserSettingsManager",
    "user_settings_manager",
    # Factory
    "Factory",
    # Logout Service
    "query_user_info",
    "print_user_info",
    "fuck_user",
    "fuck_user1",
    "fuck_user2",
]
