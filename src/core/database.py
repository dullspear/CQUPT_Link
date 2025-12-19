"""数据库操作模块

提供用户账户信息的数据库存储和查询功能。
"""

import sqlite3

from src.core.logger import log


class ConnectDb:
    """数据库连接类，用于管理用户账户信息"""

    def __init__(self, db_file="account.db"):
        """初始化数据库连接

        Args:
            db_file: 数据库文件路径，默认为 'account.db'
        """
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        """创建用户表（如果不存在）"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id VARCHAR(20) PRIMARY KEY,
                user_account VARCHAR(20),
                user_password VARCHAR(20),
                isp VARCHAR(20),
                ip_master VARCHAR(20),
                method VARCHAR(20),
                login_method VARCHAR(20)
            )
        """)
        self.connection.commit()

    def insert_user(
        self, user_account, user_password, isp, ip_master, method, login_method
    ):
        """插入或替换用户信息

        Args:
            user_account: 用户账号
            user_password: 用户密码
            isp: 运营商类型
            ip_master: IP 地址
            method: 登录方法
            login_method: 登录方式
        """
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO user (id, user_account, user_password, isp, ip_master, method, login_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (1, user_account, user_password, isp, ip_master, method, login_method),
        )
        self.connection.commit()

    def close_connection(self):
        """关闭数据库连接"""
        self.connection.close()

    def get_first_user(self):
        """获取第一个用户的信息

        Returns:
            tuple: (是否存在, 用户信息)
        """
        self.cursor.execute("SELECT * FROM user WHERE id = 1")
        result = self.cursor.fetchone()
        return result is not None, result

    def __del__(self):
        """析构函数,关闭数据库连接"""
        log.debug("Database object is being destroyed")
        self.close_connection()
