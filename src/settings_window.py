from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox
from PyQt6.QtCore import Qt
from src.user_settings_manager import user_settings_manager


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(360, 180)

        self.layout = QVBoxLayout(self)
        self.user_settings_manager = user_settings_manager

        self.remember_cb = QCheckBox("记住账号密码")
        self.remember_cb.setChecked(
            self.user_settings_manager.get_remember_credentials()
        )
        self.layout.addWidget(self.remember_cb)

        self.startup_cb = QCheckBox("开机启动（未实现）")
        self.startup_cb.setChecked(self.user_settings_manager.get_startup())
        self.layout.addWidget(self.startup_cb)

        self.auto_login_cb = QCheckBox("自动登录（未实现）")
        self.auto_login_cb.setChecked(self.user_settings_manager.get_auto_login())
        self.layout.addWidget(self.auto_login_cb)

        self.tray_cb = QCheckBox("托盘后台保活")
        # TODO: get_remember_credentials 而非 get_tray?
        self.tray_cb.setChecked(self.user_settings_manager.get_tray())
        self.layout.addWidget(self.tray_cb)

        # 信号与槽
        self.remember_cb.stateChanged.connect(self.on_remember_changed)
        self.startup_cb.stateChanged.connect(self.on_startup_changed)
        self.auto_login_cb.stateChanged.connect(self.on_auto_login_changed)
        self.tray_cb.stateChanged.connect(self.on_tray_changed)

    def on_remember_changed(self, state):
        self.user_settings_manager.set_remember_credentials(
            self.remember_cb.isChecked()
        )

    def on_startup_changed(self, state):
        # TODO: 实现开机启动功能
        self.user_settings_manager.set_startup(self.startup_cb.isChecked())

    def on_auto_login_changed(self, state):
        self.user_settings_manager.set_auto_login(self.auto_login_cb.isChecked())

    def on_tray_changed(self, state):
        self.user_settings_manager.set_tray(self.tray_cb.isChecked())


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())
