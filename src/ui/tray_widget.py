from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from src.user_settings_manager import UserSettingsManager, user_settings_manager


class TrayWidget(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_settings_manager: UserSettingsManager = user_settings_manager
        self.setIcon(QIcon(":/resource/images/logo.png"))
        self.setToolTip("重邮校园网登录")

        # 创建菜单
        self.menu = QMenu()

        # 自动登录复选框
        self.auto_login_action = QAction("自动登录", self, checkable=True)
        self.auto_login_action.setChecked(self.user_settings_manager.get_auto_login())
        self.auto_login_action.toggled.connect(self.toggle_auto_login)
        self.menu.addAction(self.auto_login_action)

        # 主动登录按钮
        self.login_action = QAction("主动登录", self)
        # self.login_action.triggered.connect(self.manual_login)
        self.menu.addAction(self.login_action)

        # 退出按钮
        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.force_quit_app)
        self.menu.addAction(self.exit_action)

        self.setContextMenu(self.menu)

        # 连接托盘激活信号（单击或双击时弹出 parent）
        self.activated.connect(self.on_activated)

    def toggle_auto_login(self, checked):
        self.user_settings_manager.set_auto_login(checked)

    def force_quit_app(self):
        """强制退出应用,不弹出托盘对话框"""
        parent = self.parent()
        if parent:
            # 直接调用主窗口的强制退出方法
            parent.force_quit_app()
        else:
            # 没有父窗口,直接退出
            QApplication.instance().quit()

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """
        当用户单击或双击系统托盘图标时，显示并激活 parent 窗口。
        支持单击(Trigger)和双击(DoubleClick)。
        """
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            parent = self.parent()
            if parent is None:
                return
            # 如果最小化则恢复
            if hasattr(parent, "isMinimized") and parent.isMinimized():
                parent.showNormal()
            parent.show()
            parent.raise_()
            parent.activateWindow()

    # def manual_login(self):
    #     self.main_window.login()


if __name__ == "__main__":
    import images  # noqa: F401
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)  # 创建 QApplication 实例
    main_window = QMainWindow()
    tray_widget = TrayWidget(main_window)
    tray_widget.show()
    sys.exit(app.exec())  # 启动事件循环
