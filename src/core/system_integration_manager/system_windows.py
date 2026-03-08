import os
import sys
import winreg

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from src.core.logger import log
from src.core.system_integration_manager.system_interface import ISystemIntegration
from src.core.user_settings_manager import user_settings_manager


class SystemIntegrationWindows(ISystemIntegration):
    def __init__(self):
        self.tray = None
        self.user_settings_manager = user_settings_manager

    def setup_tray(self, app, main_window, enable: bool) -> object | None:
        try:
            if not enable:
                if self.tray:
                    self.tray.hide()
                    self.tray = None
                return None
            self.tray = QSystemTrayIcon(main_window)
            self.tray.setIcon(QIcon(":/resource/images/favicon.ico"))
            menu = QMenu()
            show_action = QAction("显示", main_window)
            settings_action = QAction("设置", main_window)
            quit_action = QAction("退出", main_window)
            menu.addAction(show_action)
            menu.addAction(settings_action)
            menu.addSeparator()
            menu.addAction(quit_action)
            show_action.triggered.connect(lambda: main_window.showNormal())
            settings_action.triggered.connect(lambda: main_window.open_settings())
            quit_action.triggered.connect(lambda: QApplication.quit())
            self.tray.setContextMenu(menu)
            self.tray.show()
            self.tray.activated.connect(
                lambda reason: main_window.showNormal()
                if reason == QSystemTrayIcon.ActivationReason.Trigger
                else None
            )
            return self.tray
        except Exception:
            log.exception("system tray setup failed")
            return None

    def set_startup(self, enable: bool) -> bool:
        try:
            run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            exe_path = sys.executable
            script = os.path.abspath(sys.argv[0])
            if getattr(sys, "frozen", False):
                # Add a flag to indicate startup launch for frozen app
                value = f'"{exe_path}" --startup'
            else:
                # For development/script mode, we need to run python with the script
                # Use pythonw.exe to avoid console window if possible, or just python.exe
                # pythonw.exe is usually in the same directory as python.exe
                python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(python_exe):
                    python_exe = sys.executable
                # Add a flag to indicate startup launch
                value = f'"{python_exe}" "{script}" --startup'

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                if enable:
                    winreg.SetValueEx(key, "CQUPT_Link", 0, winreg.REG_SZ, value)
                else:
                    try:
                        winreg.DeleteValue(key, "CQUPT_Link")
                    except FileNotFoundError:
                        pass
            return True
        except Exception:
            log.exception("set_startup failed")
            return False

    def cleanup(self) -> None:
        try:
            if self.tray:
                self.tray.hide()
                self.tray = None
        except Exception:
            pass
