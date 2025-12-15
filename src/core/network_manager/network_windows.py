import locale
import socket
import subprocess
import time

import psutil

from src.core.logger import log
from src.core.network_manager.network_interface import INetwork


class NetworkWindows(INetwork):
    def __init__(self):
        # Set up the STARTUPINFO to hide the console window
        self.startupinfo = subprocess.STARTUPINFO()
        self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.startupinfo.wShowWindow = subprocess.SW_HIDE

    def connect_to_wifi(self) -> None:
        ssid_list = ["CQUPT-5G", "CQUPT", "CQUPT-2.4G"]
        for ssid in ssid_list:
            # 查看是否已连接
            time.sleep(2)
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding=locale.getpreferredencoding(),
            )
            if ssid in result.stdout:
                log.info("已经连接")
                return
            log.info("未连接")
            subprocess.run(
                [
                    "netsh",
                    "wlan",
                    "connect",
                    "name=" + ssid,
                    "ssid=" + ssid,
                    "interface=WLAN",
                ]
            )
        log.info("未能连接到任何可用的Wi-Fi")

    def _is_ethernet_connected(self):
        try:
            # 执行 ipconfig /all 命令
            result = subprocess.run(
                ["ipconfig", "/all"],
                stdout=subprocess.PIPE,
                text=True,
                encoding=locale.getpreferredencoding(),
                startupinfo=self.startupinfo,
            )
            output = result.stdout

            # 检查输出中是否包含以太网连接并具有以 10. 开头的 IP 地址
            lines = output.splitlines()
            log.info(lines[5])
            ethernet_found = False
            for line in lines:
                if "Ethernet adapter" in line or "以太网适配器" in line:
                    ethernet_found = True
                if ethernet_found and ("IPv4 Address" in line or "IPv4 地址" in line):
                    if "10." in line.split(":")[1].strip():
                        return True
                    ethernet_found = False
            return False
        except Exception as e:
            log.warning(f"检查网络连接时出错: {e}")
            return False

    def _is_wlan_connected(self):
        try:
            # 执行 ipconfig /all 命令
            result = subprocess.run(
                ["ipconfig", "/all"],
                stdout=subprocess.PIPE,
                text=True,
                encoding=locale.getpreferredencoding(),
                startupinfo=self.startupinfo,
            )
            output = result.stdout

            # 检查输出中是否包含以太网连接并具有以 10. 开头的 IP 地址
            lines = output.splitlines()
            ethernet_found = False
            for line in lines:
                if "Wireless LAN adapter" in line or "无线局域网适配器" in line:
                    ethernet_found = True
                if ethernet_found and ("IPv4 Address" in line or "IPv4 地址" in line):
                    if "10." in line.split(":")[1].strip():
                        return True
                    ethernet_found = False
            return False
        except Exception as e:
            log.info(f"检查网络连接时出错: {e}")
            return False

    def get_local_ip(self) -> str:
        try:
            # 检查有线连接并获取IP地址
            if self._is_ethernet_connected():
                interfaces = psutil.net_if_addrs().get("以太网")
                if interfaces:
                    for address in interfaces:
                        if (
                            address.family == socket.AF_INET
                            and address.address.startswith("10.")
                        ):
                            return "wired", address.address

            # 如果没有有线连接或者有线连接不是以 10. 开头，则返回无线IP地址
            if self._is_wlan_connected():
                interfaces = psutil.net_if_addrs().get("WLAN")
                if interfaces:
                    for address in interfaces:
                        if (
                            address.family == socket.AF_INET
                            and address.address.startswith("10.")
                        ):
                            return "wireless", address.address
            log.info("正在连接WiFi")
            self.connect_to_wifi()
            time.sleep(10)
            # 下面一段与上面几乎相同 但是先连wifi
            if self._is_wlan_connected():
                time.sleep(15)
                interfaces = psutil.net_if_addrs().get("WLAN")
                if interfaces:
                    for address in interfaces:
                        if (
                            address.family == socket.AF_INET
                            and address.address.startswith("10.")
                        ):
                            return "wireless", address.address

            # 如果没有无线连接或者无线连接不是以 10. 开头，则返回 None
            return None, None

        except Exception as e:
            log.warning(f"获取本地IP地址时出错: {e}")
            return None, None
