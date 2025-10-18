import sys
import time
import webbrowser
from PyQt6.QtCore import Qt, QLocale, QObject, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication
from qframelesswindow import AcrylicWindow
from qfluentwidgets import (
    setThemeColor,
    FluentTranslator,
    SplitTitleBar,
    MessageBox,
)
from src.ui.login_window import Ui_Form
from connect_db import ConnectDb
import images  # 不要删，导入qrc文件 # noqa
from logger import log
from src.deprecated.is_admin import is_admin  # deprecated # noqa
import requests
from logout import query_user_info, fuck_user
from src.factory import Factory
from PyQt6.QtGui import QAction
from src.settings_window import SettingsWindow
from urllib3.exceptions import InsecureRequestWarning
from src.user_settings_manager import user_settings_manager, UserSettingsManager
from PyQt6.QtCore import QTimer
from src.ui.tray_ui_logic import TrayUiLogic

# TODO: 下面这一块预备工作要封装出去，解耦。
## Disable SSL verification warnings.

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# 强制取消代理带来的干扰
proxies = {
    "http": None,
    "https": None,
}
session = requests.Session()
session.proxies.update(proxies)


class Mysignals(QObject):
    text_print = pyqtSignal(str)


# 特殊登录传的新线程类
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run_special_login(self):
        # Call the special_login method of the parent (LoginWindow)
        self.parent().special_login()
        self.finished.emit()  # Emit finished signal when done


class StateToolTipWorker(QObject):
    def __init__(self, state_tooltip, parent=None):
        super().__init__(parent)
        self.state_tooltip = state_tooltip

    def run(self):
        self.state_tooltip.show()


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

        self.page_0.pushButton_2.clicked.connect(
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

            self.page_0.lineEdit_3.setText(self.user_account)
            self.page_0.lineEdit_4.setText(self.user_password)

            if self.isp == "cmcc":
                self.page_0.RadioButton_1.setChecked(True)
            elif self.isp == "unicom":
                self.page_0.RadioButton_2.setChecked(True)
            elif self.isp == "telecom":
                self.page_0.RadioButton_3.setChecked(True)

            if self.ip_master == "0":
                self.page_1.local_ip_rbtn.setChecked(True)
            else:
                self.page_1.others_ip_rbtn.setChecked(True)
                self.page_1.others_ip_edit.setText(self.ip_master)
                self.page_1.others_ip_edit.show()

            if self.method == "0":
                self.page_3.PC_rbtn.setChecked(True)
            elif self.method == "1":
                self.page_3.PE_rbtn.setChecked(True)

            if self.login_method == "0":
                self.page_4.normal_login_rbtn.setChecked(True)
            elif self.login_method == "1":
                self.page_4.special_login_rbtn.setChecked(True)

    def login(self):
        # TODO: 需要解耦出去，到src.core.cqupt_link_logic.py
        log.info("正在登录")
        if self.page_4.normal_login_rbtn.isChecked():
            self.normal_login()
        else:
            print("wtf")
            self.nextButton.setText("登录中")

            self.nextButton.setEnabled(False)
            self.previousButton.setEnabled(False)
            # TODO：增加登录状态等待提示
            # self.page_4.stateTooltip = StateToolTip('正在登录', '客官请耐心等待哦~~', self)
            # self.page_4.stateTooltip.move(1000, 50)
            # # 启动一个线程来处理 StateToolTip 的显示和隐藏
            # self.tooltip_thread = QThread()
            # self.tooltip_worker = StateToolTipWorker(self.page_4.stateTooltip)
            # self.tooltip_worker.moveToThread(self.tooltip_thread)
            # self.tooltip_thread.started.connect(self.tooltip_worker.run)
            # self.tooltip_thread.start()

            # Create a QThread object
            self.thread = QThread()
            # Create a Worker object
            self.worker = Worker(self)
            # Move the Worker object to the Thread object
            self.worker.moveToThread(self.thread)
            # Connect signals and slots
            self.thread.started.connect(self.worker.run_special_login)
            self.worker.finished.connect(self.on_special_login_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            # Start the thread
            self.thread.start()
            # self.page_4.stateTooltip = StateToolTip('正在登录', '客官请耐心等待哦~~', self)
            # self.page_4.stateTooltip.move(1000, 50)
            # self.page_4.stateTooltip.show()

    # 特殊登录流程：注销 -> 一次普通登录 -> change_mac -> 一次普通登录
    def special_login(self):
        # 一次登录
        log.info("特殊登录开始，首次登录中")
        wired_kind, ip = self.platform.get_network_manager().get_local_ip()
        print(ip, wired_kind)
        if wired_kind is None or (not ip.startswith("10")):
            MessageBox(
                "错误",
                "ip地址非法，可能是内部错误,请检查是否使用无线登录，是否开启wifi",
                self,
            ).exec()
            return
        # 注销
        log.info("开始注销")

        username = self.page_0.lineEdit_3.text()
        user_info = query_user_info(username)
        fuck_user(username, user_info)
        log.info("注销完成")

        # # 判断设备型号
        # log.info("第一次修改mac开始")
        from src.deprecated.change_mac_csdn import SetMac

        change_mac = SetMac(wired_kind)
        # change_mac.run()
        # log.info("第一次修改mac完成")

        # 不sleep有概率 UmFkOjEwOTAyNjAwNHwxMDkwMjAwMTN8UmVqZWN0IGJ5IGNvbmN1cnJlbmN5IGNvbnRyb2wu报错
        time.sleep(1)

        res = self.normal_login(show=False)
        if not res:
            log.debug("第一次登录失败")
            return
        start_time = time.time()
        log.info("login完成 以下为login后的mac:")
        change_mac.get_macinfos()  # 部署要删

        # 二次登录
        log.info("正在二次登录")
        log.info("第二次修改mac开始")
        change_mac.run()
        log.info("第二次修改mac结束")

        interval = self.user_settings_manager.get_interval()
        # log.info(time.time() + " " + start_time)
        # 等待指定时间间隔
        while time.time() - start_time < interval:
            time.sleep(0.1)  # 可以适当减小 sleep 的时间间隔以减少 CPU 占用

        self.normal_login()

        log.info("login完成 以下为login后的mac:")

    def normal_login(self, show=True):
        log.info("普通login")
        self.BASE_URL = "http://192.168.200.2:801/eportal"

        username = self.page_0.lineEdit_3.text()
        password = self.page_0.lineEdit_4.text()

        if self.page_0.RadioButton_1.isChecked():
            isp = "cmcc"
        elif self.page_0.RadioButton_2.isChecked():
            isp = "unicom"
        elif self.page_0.RadioButton_3.isChecked():
            isp = "telecom"
        else:
            MessageBox("信息缺少", "未选择运营商", self).exec()
            return
        if not username or not password:
            MessageBox("信息缺少", "请填写用户名和密码", self).exec()
            return
        wired_kind = None
        if self.page_1.others_ip_rbtn.isChecked():
            if (
                self.page_1.others_ip_edit.text() is None
                or self.page_1.others_ip_edit.text() == ""
            ):
                MessageBox("信息缺少", "若指定ip 请填写具体ip地址", self).exec()
                return
            else:
                ip_master = self.page_1.others_ip_edit.text()
                ip = ip_master
                wired_kind = "-1"
        else:
            ip_master = "0"
            wired_kind, ip = self.platform.get_network_manager().get_local_ip()

        if wired_kind is None or (not ip.startswith("10")):
            MessageBox(
                "错误",
                "ip地址非法，可能是内部错误,请检查是否使用无线登录，是否开启wifi",
                self,
            ).exec()
            return

        if self.page_3.PC_rbtn.isChecked():
            method = "0"
        else:
            method = "1"

        if self.page_4.normal_login_rbtn.isChecked():
            login_method = "0"
        else:
            login_method = "1"

        params = {
            "c": "Portal",
            "a": "login",
            "callback": "",
            "login_method": "1",
            "user_account": "," + method + "," + username + "@" + isp,
            "user_password": password,
            "wlan_user_ip": ip,
            "wlan_user_ipv6": "",
            "wlan_user_mac": "000000000000",
            "wlan_ac_ip": "",
            "wlan_ac_name": "",
            "jsVersion": "3.3.3",
            "v": "6305",
        }
        try:
            r = requests.get(
                url=self.BASE_URL,
                params=params,
                proxies=proxies,
                verify=False,
                timeout=15,
            )
        except requests.exceptions.RequestException as e:
            MessageBox(
                "网络异常", f"网络异常，无法连接到服务器，请检查网络\n{e}", self
            ).exec()
            return
        response_text = r.text.encode("utf-8").decode("unicode_escape")
        print("responst_text" + response_text)
        print("cao")
        content = ""
        if (
            '({"result":"0","msg":"","ret_code":2})' in response_text
            or "认证成功" in response_text
        ):
            # 保存到数据库（仅当用户选择记住账号密码）
            if self.user_settings_manager.get_remember_credentials():
                self.db.insert_user(
                    username, password, isp, ip_master, method, login_method
                )
            print(response_text)
            print("shit")
            title = "登录成功"
            if '({"result":"0","msg":"","ret_code":2})' in response_text:
                content = "重复登录，如果您想更改/伪装新的登录端，请先注销"
                # 也可能已达到 + method_mapping[self.method]  + 数量限制
        else:
            log.info("登录失败")
            title = "登录失败"
            log.info(response_text)
            # log.info('({"result":"0","msg":"dXNlcmlkIGVycm9yMQ==","ret_code":1})' == r.text)
            log.info("cao")
            if "bGRhcCBhdXRoIGVycm9y" in response_text:
                content = "密码错误或运营商错误，请仔细检查后重试"
            elif "aW51c2UsIGxvZ2luI" in response_text:
                content = "请再试一次"
            elif '({"result":"0","msg":"","ret_code":1})' in response_text:
                content = "请仔细检查ip地址等后重试！"
            elif (
                '({"result":"0","msg":"dXNlcmlkIGVycm9yMQ==","ret_code":1})'
                in response_text
            ):
                content = "请仔细检查运营商/用户名等后重试"
            elif "密码不能为空" in response_text:
                # 即({"result":"0","msg":"\u5bc6\u7801\\u4e0d\u80fd\u4e3a\u7a7a"})
                content = "密码不能为空，请重新填写密码"
            elif "获取用户ip失败，请重试" in response_text:
                # 即 '({"result":"0","msg":"\u83b7\u53d6\u7528\u6237IP\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5\uff01"})'
                content = "请填写本机ip，Tips:可以按下”获取本机ip“按钮，一键填写"
            content += f"\n \n {response_text}\n"
            log.info(content)
            # content += f"{url}"
            log.info(params)
        if show or title != "登录成功":
            dlg = MessageBox(title, content, self)
            # w.setWindowModality(Qt.WindowModality)  # 阻塞主窗口

            if dlg.exec():
                log.info("Yes button is pressed")
            else:
                log.info("Cancel button is pressed")
            return False
        return True

    def on_special_login_finished(self):
        if self.page_4.stateTooltip:
            self.page_4.stateTooltip.setContent("登录完成啦 😆")
            self.page_4.stateTooltip.setState(True)
            self.page_4.stateTooltip = None
        self.nextButton.setEnabled(True)
        self.previousButton.setEnabled(True)
        self.nextButton.setText("登陆")

    def _open_settings(self):
        try:
            dlg = SettingsWindow(self)
            dlg.exec()
        except Exception:
            log.exception("open settings failed")

    def closeEvent(self, event):
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
