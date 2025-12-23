"""学校网络登录/注销相关逻辑，GUI 与 CLI 可复用。"""

from __future__ import annotations

from dataclasses import dataclass
import time

import requests
from urllib3.exceptions import InsecureRequestWarning

from src.core.factory import Factory
from src.core.logger import log
from src.core.logout_service import fuck_user, query_user_info
from src.core.user_settings_manager import user_settings_manager

# 全局禁用 SSL 校验告警（与 GUI 旧逻辑保持一致）
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# 取消代理干扰
DEFAULT_PROXIES = {"http": None, "https": None}


@dataclass
class LoginParams:
    username: str
    password: str
    isp: str  # cmcc / unicom / telecom
    device_method: str  # "0"=PC  "1"=移动端
    login_method: str = "0"  # "0"=普通  "1"=特殊
    ip: str | None = None  # 指定 IP；None 时自动获取
    remember: bool = False  # 是否保存到数据库（若提供 db）


@dataclass
class LoginResult:
    success: bool
    title: str
    message: str = ""
    response_text: str | None = None


class SchoolnetManager:
    BASE_URL = "http://192.168.200.2:801/eportal"

    def __init__(
        self,
        platform=None,
        db=None,
        settings_manager=None,
        session: requests.Session | None = None,
    ) -> None:
        self.platform = platform or Factory.create_platform()
        self.db = db
        self.settings_manager = settings_manager or user_settings_manager
        self.session = session or requests.Session()
        self.session.proxies.update(DEFAULT_PROXIES)

    def normal_login(self, params: LoginParams) -> LoginResult:
        if not params.username or not params.password:
            return LoginResult(False, "信息缺少", "请填写用户名和密码")

        wired_kind, ip, ip_master = self._resolve_ip(params.ip)
        if ip is None or not ip.startswith("10"):
            return LoginResult(
                False, "错误", "IP 地址非法，请检查是否使用无线登录并已开启 Wi-Fi"
            )

        login_params = {
            "c": "Portal",
            "a": "login",
            "callback": "",
            "login_method": "1",
            "user_account": ","
            + params.device_method
            + ","
            + params.username
            + "@"
            + params.isp,
            "user_password": params.password,
            "wlan_user_ip": ip,
            "wlan_user_ipv6": "",
            "wlan_user_mac": "000000000000",
            "wlan_ac_ip": "",
            "wlan_ac_name": "",
            "jsVersion": "3.3.3",
            "v": "6305",
        }

        try:
            resp = self.session.get(
                url=self.BASE_URL,
                params=login_params,
                proxies=DEFAULT_PROXIES,
                verify=False,
                timeout=15,
            )
        except requests.exceptions.RequestException as exc:
            return LoginResult(
                False, "网络异常", f"无法连接到服务器，请检查网络\n{exc}"
            )

        response_text = resp.text.encode("utf-8").decode("unicode_escape")
        log.debug("login response: %s", response_text)

        # 判定成功
        if (
            '({"result":"0","msg":"","ret_code":2})' in response_text
            or "认证成功" in response_text
        ):
            title = "登录成功"
            message = ""
            if '({"result":"0","msg":"","ret_code":2})' in response_text:
                message = "重复登录，如果您想更改/伪装新的登录端，请先注销"

            if params.remember and self.db is not None:
                self.db.insert_user(
                    params.username,
                    params.password,
                    params.isp,
                    ip_master,
                    params.device_method,
                    params.login_method,
                )

            return LoginResult(True, title, message, response_text)

        # 失败分支
        msg = self._map_error(response_text)
        return LoginResult(False, "登录失败", msg + f"\n\n{response_text}\n")

    def special_login(self, params: LoginParams) -> LoginResult:
        # 获取本机/指定 IP
        wired_kind, ip, ip_master = self._resolve_ip(params.ip)
        if ip is None or not ip.startswith("10"):
            return LoginResult(
                False, "错误", "IP 地址非法，请检查是否使用无线登录并已开启 Wi-Fi"
            )

        # 注销
        username = params.username
        user_info = query_user_info(username)
        fuck_user(username, user_info)

        from src.core.deprecated.change_mac_csdn import SetMac

        change_mac = SetMac(wired_kind)

        time.sleep(1)

        first_login_result = self.normal_login(
            LoginParams(
                username=params.username,
                password=params.password,
                isp=params.isp,
                device_method=params.device_method,
                login_method="0",
                ip=ip,
                remember=False,
            )
        )
        if not first_login_result.success:
            return first_login_result

        start_time = time.time()
        change_mac.get_macinfos()

        # 第二次登录
        change_mac.run()

        interval = 62
        if self.settings_manager is not None:
            interval = self.settings_manager.get_interval()

        while time.time() - start_time < interval:
            time.sleep(0.1)

        second_login_result = self.normal_login(
            LoginParams(
                username=params.username,
                password=params.password,
                isp=params.isp,
                device_method=params.device_method,
                login_method="1",
                ip=ip_master if ip_master != "0" else None,
                remember=params.remember,
            )
        )
        return second_login_result

    def _resolve_ip(self, override_ip: str | None):
        if override_ip:
            return "-1", override_ip, override_ip
        wired_kind, ip = self.platform.get_network_manager().get_local_ip()
        return wired_kind, ip, "0"

    @staticmethod
    def _map_error(response_text: str) -> str:
        if "bGRhcCBhdXRoIGVycm9y" in response_text:
            return "密码错误或运营商错误，请仔细检查后重试"
        if "aW51c2UsIGxvZ2luI" in response_text:
            return "请再试一次"
        if '({"result":"0","msg":"","ret_code":1})' in response_text:
            return "请仔细检查 IP 地址等后重试！"
        if (
            '({"result":"0","msg":"dXNlcmlkIGVycm9yMQ==","ret_code":1})'
            in response_text
        ):
            return "请仔细检查运营商/用户名等后重试"
        if "密码不能为空" in response_text:
            return "密码不能为空，请重新填写密码"
        if "获取用户ip失败，请重试" in response_text:
            return "请填写本机 IP，或点击“获取本机 IP”按钮"
        return "登录失败，请稍后再试"
