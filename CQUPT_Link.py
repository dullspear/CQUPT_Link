"""主 GUI 入口。"""

# 不要删，导入qrc文件
from resource import resources  # noqa
import sys
import webbrowser

from PyQt6.QtCore import QLocale, QObject, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import (
    FluentIcon,
    FluentTranslator,
    MessageBox,
    SplitTitleBar,
    TransparentToolButton,
    setThemeColor,
)
from qframelesswindow import AcrylicWindow

from src.core.database import ConnectDb
from src.core.deprecated.is_admin import is_admin  # deprecated # noqa
from src.core.factory import Factory
from src.core.logger import log
from src.core.schoolnet_manager import LoginParams, SchoolnetManager
from src.core.user_settings_manager import UserSettingsManager, user_settings_manager
from src.ui.login_window import Ui_Form
from src.ui.settings_window import SettingsWindow
from src.ui.tray_ui_logic import TrayUiLogic


class Mysignals(QObject):
    text_print = pyqtSignal(str)


# 特殊登录传的新线程类
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, params: LoginParams, parent=None):
        super().__init__(parent)
        self.params = params

    def run_special_login(self):
        self.parent().special_login(self.params)
        self.finished.emit()


class LoginWindow(AcrylicWindow, Ui_Form):
    # my_signals = Mysignals()
    # ms = my_signals.text_print
    db = ConnectDb()

    def __init__(self):
        self.platform = Factory.create_platform()
        super().__init__()
        # TODO: delete it, since special login was deprecated.
        # is_admin()  # 以管理员身份运行 以运行之后的 change_mac

        self.setupUi(self)
        # setTheme(Theme.DARK)
        setThemeColor("#28afe9")

        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        # 添加设置按钮到标题栏
        self._add_settings_button_to_titlebar()

        self.label.setScaledContents(False)
        self.setWindowTitle("重邮校园网登录")
        self.setWindowIcon(QIcon(":/resource/images/logo.png"))
        self.resize(1000, 650)

        self.windowEffect.setMicaEffect(self.winId(), isDarkMode=False)
        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: white
            }
        """)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # 以下是核心代码

        # load settings
        self.user_settings_manager: UserSettingsManager = user_settings_manager
        # 如果用户选择了记住密码，则加载数据库中的用户设置
        if self.user_settings_manager.get_remember_credentials():
            self._apply_db_settings()

        self.schoolnet_manager = SchoolnetManager(
            platform=self.platform,
            db=self.db,
            settings_manager=self.user_settings_manager,
        )

        self.self_service_btn.clicked.connect(
            lambda: webbrowser.open("https://202.202.32.120:8443/Self/login/")
        )

        self.login_button_clicked.connect(self.login)

        # shortcut to open settings: Ctrl+,
        try:
            settings_action = QAction(self)
            settings_action.setShortcut("Ctrl+,")
            settings_action.triggered.connect(self._open_settings)
            self.addAction(settings_action)
        except Exception:
            pass

        if self.user_settings_manager.get_auto_login():
            QTimer.singleShot(300, lambda: self.login())

    def _apply_db_settings(self):
        """
        当用户选择“记住密码”时，程序启动时自动加载数据库中的用户设置。
        """
        exists, account = self.db.get_first_user()

        if exists:
            # self.id = account[0]
            self.user_account = account[1]
            self.user_password = account[2]
            self.isp = account[3]
            self.ip_master = account[4]
            self.method = account[5]
            self.login_method = account[6]

            self.username_edit.setText(self.user_account)
            self.password_edit.setText(self.user_password)

            if self.isp == "cmcc":
                self.isp_cmcc_rbtn.setChecked(True)
            elif self.isp == "unicom":
                self.isp_unicom_rbtn.setChecked(True)
            elif self.isp == "telecom":
                self.isp_telecom_rbtn.setChecked(True)

            # 展开高级设置以展示加载的配置
            self.advanced_toggle_btn.setChecked(True)
            self.advanced_widget.setVisible(True)

            if self.ip_master != "0":
                self.use_other_ip_rbtn.setChecked(True)
                self.other_ip_edit.setText(self.ip_master)
                self.other_ip_edit.show()
            else:
                self.use_local_ip_rbtn.setChecked(True)

            if self.method == "0":
                self.device_pc_rbtn.setChecked(True)
            elif self.method == "1":
                self.device_pe_rbtn.setChecked(True)

            if self.login_method == "0":
                self.login_type_normal_rbtn.setChecked(True)
            elif self.login_method == "1":
                self.login_type_special_rbtn.setChecked(True)

    def login(self):
        log.info("正在登录")
        params = self._build_login_params()
        if not params:
            return

        if params.login_method == "0":
            result = self.schoolnet_manager.normal_login(params)
            self._show_result(result)
        else:
            self._start_special_login(params)

    def _start_special_login(self, params: LoginParams):
        self.loginButton.setText("登录中")
        self.loginButton.setEnabled(False)
        self._special_login_result = None

        self.thread = QThread()
        self.worker = Worker(params, self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_special_login)
        self.worker.finished.connect(self.on_special_login_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def special_login(self, params: LoginParams):
        self._special_login_result = self.schoolnet_manager.special_login(params)

    def _show_result(self, result):
        if not result:
            return
        # 成功但有提示（例如重复登录）或失败时弹窗
        if (result.title != "登录成功") or result.message:
            dlg = MessageBox(result.title, result.message or "", self)
            dlg.exec()

    def _build_login_params(self) -> LoginParams | None:
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if self.isp_cmcc_rbtn.isChecked():
            isp = "cmcc"
        elif self.isp_unicom_rbtn.isChecked():
            isp = "unicom"
        elif self.isp_telecom_rbtn.isChecked():
            isp = "telecom"
        else:
            MessageBox("信息缺少", "未选择运营商", self).exec()
            return None

        if not username or not password:
            MessageBox("信息缺少", "请填写用户名和密码", self).exec()
            return None

        ip_override = None
        if self.use_other_ip_rbtn.isChecked():
            ip_override = self.other_ip_edit.text().strip()
            if not ip_override:
                MessageBox("信息缺少", "若指定 IP，请填写具体 IP 地址", self).exec()
                return None

        device_method = "0" if self.device_pc_rbtn.isChecked() else "1"
        login_method = "0" if self.login_type_normal_rbtn.isChecked() else "1"

        remember = self.user_settings_manager.get_remember_credentials()

        return LoginParams(
            username=username,
            password=password,
            isp=isp,
            device_method=device_method,
            login_method=login_method,
            ip=ip_override,
            remember=remember,
        )

    def on_special_login_finished(self):
        self.loginButton.setEnabled(True)
        self.loginButton.setText("登录")
        if hasattr(self, "_special_login_result"):
            self._show_result(self._special_login_result)

    def _add_settings_button_to_titlebar(self):
        """在标题栏添加设置按钮"""
        try:
            # 创建设置按钮
            self.settings_btn = TransparentToolButton(FluentIcon.SETTING, self)
            self.settings_btn.setFixedSize(46, 32)
            self.settings_btn.clicked.connect(self._open_settings)

            # 添加到标题栏 (在最小化/最大化/关闭按钮的左边)
            self.titleBar.hBoxLayout.insertWidget(
                self.titleBar.hBoxLayout.count()
                - 3,  # 在最后3个按钮(最小化/最大化/关闭)之前插入
                self.settings_btn,
                0,
                Qt.AlignmentFlag.AlignRight,
            )
        except Exception:
            log.exception("Failed to add settings button to titlebar")

    def _open_settings(self):
        try:
            dlg = SettingsWindow(self)
            dlg.exec()
        except Exception:
            log.exception("open settings failed")

    def force_quit_app(self):
        """强制退出应用,不弹出托盘对话框"""
        QApplication.instance().quit()

    def closeEvent(self, event):
        """窗口关闭事件,可能弹出托盘对话框"""
        tray_logic = TrayUiLogic(self)
        tray_logic.handle_tray_action(event)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        pixmap = QPixmap(":/resource/images/gd3u3ibyyp.jpg").scaled(
            # pixmap = QPixmap("./resource/images/middle.jpg").scaled(
            self.label.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Internationalization
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)

    w = LoginWindow()
    w.show()
    app.exec()
