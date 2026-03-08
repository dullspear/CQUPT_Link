import os
import time

from PyQt6.QtCore import QEvent, QObject, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from qfluentwidgets import RoundMenu

from src.core.logger import log
from src.core.user_settings_manager import UserSettingsManager, user_settings_manager


def _is_windows() -> bool:
    return os.name == "nt"


class _MenuAutoHideFilter(QObject):
    """在菜单事件上自动管理：Show/Hide 时安装/卸载全局钩子，失焦时隐藏菜单。

    由于 RoundMenu 的行为有时不一致，我们在 Show 时确保安装钩子，Hide 时卸载钩子。
    """

    def __init__(self, owner, menu):
        # owner: TrayWidget
        super().__init__(menu)
        self.owner = owner
        self._menu = menu

    def eventFilter(self, obj, event):
        try:
            t = event.type()
            # 菜单显示时：确保钩子安装（兜底桌面点击）
            if obj is self._menu and t == QEvent.Type.Show:
                try:
                    log.info("Tray menu shown - ensuring mouse hook")
                except Exception:
                    pass
                try:
                    self.owner._start_mouse_hook()
                except Exception:
                    pass

            # 菜单隐藏时：卸载钩子
            if obj is self._menu and t == QEvent.Type.Hide:
                try:
                    log.info("Tray menu hidden - stopping mouse hook")
                except Exception:
                    pass
                try:
                    self.owner._stop_mouse_hook()
                except Exception:
                    pass

            # 失焦/窗口切换时收起菜单
            if obj is self._menu and t in (
                QEvent.Type.WindowDeactivate,
                QEvent.Type.FocusOut,
            ):
                QTimer.singleShot(0, self._menu.hide)
        except Exception:
            pass
        return False


class TrayWidget(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_settings_manager: UserSettingsManager = user_settings_manager
        self.setIcon(QIcon(":/resource/images/logo.png"))
        self.setToolTip("重邮校园网登录")

        # 菜单使用 qfluentwidgets 风格；自动隐藏由 Windows 全局鼠标钩子兜底
        # RoundMenu 的第一个位置参数是 title（str/None），parent 必须用关键字传入
        self.menu = RoundMenu(parent=parent)
        # 可选：给菜单一个标题（qfluentwidgets 内部会调用 setTitle）
        self.menu.setTitle("CQUPT Link")

        # Qt 侧的“失焦/窗口切换”自动隐藏：Alt+Tab、点其他应用等一般都能触发。
        # 注意：点桌面在 Windows 上经常不会触发 Qt 的 deactivate，所以仍需要下面的全局鼠标钩子兜底。
        self._menu_event_filter = _MenuAutoHideFilter(self, self.menu)
        self.menu.installEventFilter(self._menu_event_filter)

        # Windows 下：桌面点击属于“应用外点击”，Qt 收不到事件。
        # 用全局低级鼠标钩子兜底，只在菜单可见时启用。
        self._mouse_hook = None
        self._mouse_hook_proc = None
        self._hook_started_at = 0.0

        # 菜单隐藏时停掉全局钩子
        self.menu.aboutToHide.connect(self._stop_mouse_hook)

        # 注意：上面的过滤器/定时器应先于 addAction，避免显示瞬间漏掉事件

        # 自动登录复选框
        self.auto_login_action = QAction("自动登录", self, checkable=True)
        self.auto_login_action.setChecked(self.user_settings_manager.get_auto_login())
        self.auto_login_action.toggled.connect(self.toggle_auto_login)
        self.menu.addAction(self.auto_login_action)

        self.menu.addSeparator()

        # 主动登录按钮
        self.login_action = QAction("主动登录", self)
        self.login_action.triggered.connect(self.manual_login)
        self.menu.addAction(self.login_action)

        # 显示主界面按钮
        self.show_action = QAction("显示主界面", self)
        self.show_action.triggered.connect(self.show_main_window)
        self.menu.addAction(self.show_action)

        # 设置按钮
        self.settings_action = QAction("设置", self)
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.settings_action)

        self.menu.addSeparator()

        # 退出按钮
        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.force_quit_app)
        self.menu.addAction(self.exit_action)

        # 不使用 setContextMenu，而是手动处理右键点击
        # self.setContextMenu(self.menu)

        # 连接托盘激活信号（右键、单击或双击）
        self.activated.connect(self.on_activated)

        # 有些系统/环境下，托盘未就绪时 show() 可能被忽略；这里确保可见状态。
        self.setVisible(True)

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

    def on_activated(self, reason):
        """
        处理托盘图标的各种点击事件。
        - 右键：显示菜单
        - 单击/双击：显示主窗口
        """
        if reason == QSystemTrayIcon.ActivationReason.Context:
            # 右键点击 - 显示菜单
            from PyQt6.QtGui import QCursor

            self.menu.popup(QCursor.pos())
            # 仅作为“点桌面”兜底：Qt 往往收不到桌面点击的失焦事件
            self._start_mouse_hook()
            return

        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            # 左键单击或双击 - 显示主窗口
            parent = self.parent()
            if parent is None:
                return
            # 如果最小化则恢复
            if hasattr(parent, "isMinimized") and parent.isMinimized():
                parent.showNormal()
            parent.show()
            parent.raise_()
            parent.activateWindow()

    def _start_mouse_hook(self):
        if not _is_windows():
            return
        if self._mouse_hook is not None:
            return
        if not self.menu or not self.menu.isVisible():
            return

        # 记录 hook 启动时间，用于忽略“弹出菜单的那一下”后紧跟着的误触
        self._hook_started_at = time.monotonic()

        try:
            import ctypes
            from ctypes import wintypes

            WH_MOUSE_LL = 14
            WM_LBUTTONDOWN = 0x0201
            WM_RBUTTONDOWN = 0x0204
            WM_MBUTTONDOWN = 0x0207
            WM_XBUTTONDOWN = 0x020B
            WM_MOUSEWHEEL = 0x020A
            WM_MOUSEHWHEEL = 0x020E

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

            class MSLLHOOKSTRUCT(ctypes.Structure):
                _fields_ = [
                    ("pt", wintypes.POINT),
                    ("mouseData", wintypes.DWORD),
                    ("flags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", wintypes.ULONG_PTR),
                ]

            LowLevelMouseProc = ctypes.WINFUNCTYPE(
                wintypes.LRESULT, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM
            )

            def _proc(nCode, wParam, lParam):
                try:
                    if nCode == 0 and self.menu and self.menu.isVisible():
                        # hook 刚启用的一小段时间内，不做收起，避免“时好时坏”的竞态
                        if (time.monotonic() - self._hook_started_at) < 0.12:
                            return user32.CallNextHookEx(
                                self._mouse_hook, nCode, wParam, lParam
                            )

                        # 只在“按下/滚轮”事件上处理
                        if wParam in (
                            WM_LBUTTONDOWN,
                            WM_RBUTTONDOWN,
                            WM_MBUTTONDOWN,
                            WM_XBUTTONDOWN,
                            WM_MOUSEWHEEL,
                            WM_MOUSEHWHEEL,
                        ):
                            # 如果点击发生在菜单外，则收起菜单
                            try:
                                ms = ctypes.cast(
                                    lParam, ctypes.POINTER(MSLLHOOKSTRUCT)
                                ).contents
                                x, y = int(ms.pt.x), int(ms.pt.y)
                                # 使用 frameGeometry 获取全局坐标系中的边界，更可靠（多显示器/缩放）
                                g = self.menu.frameGeometry()
                                inside = g.contains(x, y)
                            except Exception:
                                inside = False

                            if not inside:
                                try:
                                    log.info(
                                        "Global click outside menu at %s,%s -> hiding menu",
                                        x,
                                        y,
                                    )
                                except Exception:
                                    pass
                                QTimer.singleShot(0, self.menu.hide)
                except Exception:
                    pass

                return user32.CallNextHookEx(self._mouse_hook, nCode, wParam, lParam)

            self._mouse_hook_proc = LowLevelMouseProc(_proc)
            h_instance = kernel32.GetModuleHandleW(None)
            self._mouse_hook = user32.SetWindowsHookExW(
                WH_MOUSE_LL, self._mouse_hook_proc, h_instance, 0
            )
            if not self._mouse_hook:
                # 安装失败，清理
                self._mouse_hook = None
                self._mouse_hook_proc = None
                return
            else:
                try:
                    log.info("Installed global mouse hook: %s", self._mouse_hook)
                except Exception:
                    pass
        except Exception:
            self._mouse_hook = None
            self._mouse_hook_proc = None

    def _stop_mouse_hook(self):
        if not _is_windows():
            return
        if self._mouse_hook is None:
            return
        try:
            import ctypes

            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.UnhookWindowsHookEx(self._mouse_hook)
        except Exception:
            pass
        finally:
            self._mouse_hook = None
            self._mouse_hook_proc = None
            try:
                log.info("Uninstalled global mouse hook")
            except Exception:
                pass

    def manual_login(self):
        if self.menu and self.menu.isVisible():
            self.menu.hide()
        parent = self.parent()
        if parent and hasattr(parent, "login"):
            parent.login()

    def show_main_window(self):
        if self.menu and self.menu.isVisible():
            self.menu.hide()
        parent = self.parent()
        if parent:
            if hasattr(parent, "isMinimized") and parent.isMinimized():
                parent.showNormal()
            parent.show()
            parent.raise_()
            parent.activateWindow()

    def open_settings(self):
        if self.menu and self.menu.isVisible():
            self.menu.hide()
        parent = self.parent()
        if parent and hasattr(parent, "_open_settings"):
            parent._open_settings()


if __name__ == "__main__":
    from resource import resources  # noqa: F401
    import sys

    from PyQt6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)  # 创建 QApplication 实例
    main_window = QMainWindow()
    tray_widget = TrayWidget(main_window)
    tray_widget.show()
    sys.exit(app.exec())  # 启动事件循环
