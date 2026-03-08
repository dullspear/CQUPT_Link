from PyQt6.QtWidgets import QWidget

from src.core.logger import log
from src.core.user_settings_manager import UserSettingsManager, user_settings_manager
from src.ui.tray_dialog import TrayDialog
from src.ui.tray_widget import TrayWidget


class TrayUiLogic:
    def __init__(self, main_window: QWidget):
        self.main_window = main_window
        self.user_settings_manager: UserSettingsManager = user_settings_manager

    def _ensure_tray_visible(self):
        """确保托盘图标可见，如果已存在则复用。"""
        try:
            # 检查是否已经存在托盘实例
            if (
                hasattr(self.main_window, "tray_widget")
                and self.main_window.tray_widget
            ):
                if not self.main_window.tray_widget.isVisible():
                    self.main_window.tray_widget.show()
                return

            # 创建新的托盘实例
            tray = TrayWidget(self.main_window)
            self.main_window.tray_widget = tray
            tray.show()
        except Exception:
            # 不要吞异常，否则托盘“消失”时完全不可见原因。
            log.exception("Failed to create/show tray widget")

    def handle_tray_action(self, event):
        show_reminder = self.user_settings_manager.get_show_close_to_tray_reminder()

        if show_reminder:
            # 显示提醒对话框
            dlg = TrayDialog(self.main_window)
            result = dlg.exec()
            dont_remind = dlg.isChecked()

            # 如果用户勾选了"下次不再提醒"
            if dont_remind:
                self.user_settings_manager.set_show_close_to_tray_reminder(False)

            if result == TrayDialog.DialogCode.Accepted:
                # 用户选择"是" - 最小化到托盘
                self.user_settings_manager.set_tray(True)
                self.main_window.hide()
                self._ensure_tray_visible()
                event.ignore()
                return
            else:
                # 用户选择"否" - 直接关闭
                self.user_settings_manager.set_tray(False)
                event.accept()
                return
        else:
            # 不显示提醒,根据 tray 配置决定行为
            if self.user_settings_manager.get_tray():
                # 最小化到托盘
                self.main_window.hide()
                self._ensure_tray_visible()
                event.ignore()
            else:
                # 直接关闭
                event.accept()
