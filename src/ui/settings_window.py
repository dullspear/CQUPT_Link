"""设置窗口模块

提供用户设置界面。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QDialog, QVBoxLayout

from src.core.user_settings_manager import user_settings_manager


class SettingsWindow(QDialog):
    """设置窗口类"""

    def __init__(self, parent=None):
        """初始化设置窗口

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(360, 180)

        self.layout = QVBoxLayout(self)
        self.user_settings_manager = user_settings_manager

        # 记住账号密码选项
        self.remember_cb = QCheckBox("记住账号密码")
        self.remember_cb.setChecked(
            self.user_settings_manager.get_remember_credentials()
        )
        self.layout.addWidget(self.remember_cb)

        # 开机启动选项
        self.startup_cb = QCheckBox("开机启动")
        self.startup_cb.setChecked(self.user_settings_manager.get_startup())
        self.layout.addWidget(self.startup_cb)

        # 自动登录选项
        self.auto_login_cb = QCheckBox("自动登录")
        self.auto_login_cb.setChecked(self.user_settings_manager.get_auto_login())
        self.layout.addWidget(self.auto_login_cb)

        # 托盘后台保活选项
        self.tray_cb = QCheckBox("托盘")
        self.tray_cb.setChecked(self.user_settings_manager.get_tray())
        self.layout.addWidget(self.tray_cb)

        # 信号与槽连接
        self.remember_cb.stateChanged.connect(self.on_remember_changed)
        self.startup_cb.stateChanged.connect(self.on_startup_changed)
        self.auto_login_cb.stateChanged.connect(self.on_auto_login_changed)
        self.tray_cb.stateChanged.connect(self.on_tray_changed)

    def on_remember_changed(self, state):
        """记住密码选项改变"""
        self.user_settings_manager.set_remember_credentials(
            self.remember_cb.isChecked()
        )

    def on_startup_changed(self, state):
        """开机启动选项改变

        Note:
            TODO: 实现开机启动功能
        """
        self.user_settings_manager.set_startup(self.startup_cb.isChecked())

    def on_auto_login_changed(self, state):
        """自动登录选项改变"""
        self.user_settings_manager.set_auto_login(self.auto_login_cb.isChecked())

    def on_tray_changed(self, state):
        """托盘选项改变"""
        is_checked = self.tray_cb.isChecked()
        self.user_settings_manager.set_tray(is_checked)

        # 立即生效：通知主窗口更新托盘状态
        parent = self.parent()
        if parent and hasattr(parent, "update_tray_state"):
            parent.update_tray_state(is_checked)


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())
