from PyQt6.QtWidgets import QWidget
from src.user_settings_manager import UserSettingsManager, user_settings_manager
from src.ui.tray_dialog import TrayDialog
from src.ui.tray_widget import TrayWidget


class TrayUiLogic:
    def __init__(self, main_window: QWidget):
        self.main_window = main_window
        self.user_settings_manager: UserSettingsManager = user_settings_manager

    def _ensure_tray_visible(self):
        """无条件（重）创建托盘并附加到 main_window.tray_widget，然后 show()。"""
        try:
            # 始终创建并覆盖 main_window.tray_widget（已根据要求移除 if None 判断）
            tray = TrayWidget(self.main_window)
            setattr(self.main_window, "tray_widget", tray)
            tray.show()
        except Exception:
            # 忽略创建/显示时的异常，避免影响关闭流程
            pass

    def handle_tray_action(self, event):
        remind = self.user_settings_manager.get_close_to_tray_show_reminder()
        last_choice = self.user_settings_manager.get_close_to_tray_last_choice()
        if remind:
            dlg = TrayDialog(self.main_window)
            result = dlg.exec()
            dont_remind = dlg.isChecked()
            self.user_settings_manager.set_close_to_tray_show_reminder(not dont_remind)
            self.user_settings_manager.set_close_to_tray_last_choice(
                bool(result == TrayDialog.DialogCode.Accepted)
            )
            if result == TrayDialog.DialogCode.Accepted:
                self.user_settings_manager.set_tray(True)
                self.main_window.hide()
                self._ensure_tray_visible()
                event.ignore()
                return
            else:
                self.user_settings_manager.set_tray(False)
                event.accept()
                return
        else:
            if last_choice:
                self.user_settings_manager.set_tray(True)
                self.main_window.hide()
                self._ensure_tray_visible()
                event.ignore()
                return
            else:
                self.user_settings_manager.set_tray(False)
                event.accept()
                return
