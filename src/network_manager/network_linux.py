import locale
from src.network_manager.network_interface import INetwork
import subprocess
import socket
import time
import psutil
import shutil
import os
from logger import log


class NetworkLinux(INetwork):
    def __init__(self):
        # Linux 使用 NetworkManager，通常不需要特殊配置
        pass

    def _has_campus_ip(self, interface: str) -> bool:
        """检查指定接口是否有校园网IP地址（10.x.x.x）"""
        try:
            interfaces = psutil.net_if_addrs().get(interface)
            if interfaces:
                for address in interfaces:
                    if address.family == socket.AF_INET and address.address.startswith(
                        "10."
                    ):
                        log.info(f"接口 {interface} 有校园网IP: {address.address}")
                        return True
            return False
        except Exception as e:
            log.warning(f"检查IP地址时出错: {e}")
            return False

    def _get_wireless_interfaces(self) -> list:
        """返回系统中可能的无线接口列表，优先检测 /sys/class/net/<iface>/wireless"""
        interfaces = []
        try:
            for iface in psutil.net_if_addrs().keys():
                # 检查 sysfs 无线目录
                wireless_path = f"/sys/class/net/{iface}/wireless"
                if os.path.isdir(wireless_path):
                    interfaces.append(iface)
                    continue

                # 常见无线接口名前缀
                if (
                    iface.startswith("wlan")
                    or iface.startswith("wl")
                    or iface.startswith("wifi")
                ):
                    interfaces.append(iface)

            # 去重并返回
            return list(dict.fromkeys(interfaces))
        except Exception as e:
            log.warning(f"获取无线接口时出错: {e}")
            # 退回到简单的前缀匹配
            try:
                return [
                    iface
                    for iface in psutil.net_if_addrs().keys()
                    if iface.startswith("wlan")
                    or iface.startswith("wl")
                    or iface.startswith("wifi")
                ]
            except Exception:
                return []

    def _get_current_wifi_network(self) -> str:
        """获取当前连接的WiFi网络名称"""
        try:
            # 优先使用 nmcli（如果存在）
            if shutil.which("nmcli"):
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "active,ssid", "device", "wifi", "list"],
                    capture_output=True,
                    text=True,
                    encoding=locale.getpreferredencoding(),
                    timeout=10,
                )
                lines = result.stdout.split("\n")
                for line in lines:
                    if line.startswith("yes:"):
                        ssid = line.split(":")[1]
                        return ssid

            # 回退：使用 iwconfig 检查各无线接口的 ESSID
            wifi_ifaces = self._get_wireless_interfaces()
            for iface in wifi_ifaces:
                try:
                    result = subprocess.run(
                        ["iwconfig", iface],
                        capture_output=True,
                        text=True,
                        encoding=locale.getpreferredencoding(),
                        timeout=5,
                    )
                    out = result.stdout
                    # 查找 ESSID:"..."
                    for part in out.splitlines():
                        if "ESSID:" in part:
                            # 例如: ESSID:"CQUPT"
                            start = part.find("ESSID:")
                            essid_part = part[start:]
                            if '"' in essid_part:
                                try:
                                    ssid = essid_part.split("ESSID:")[1].strip()
                                    ssid = ssid.strip().strip('"')
                                    if ssid and ssid != "off/any":
                                        return ssid
                                except Exception:
                                    continue
                except Exception:
                    continue
            return None
        except Exception as e:
            log.warning(f"获取当前WiFi网络时出错: {e}")
            return None

    def connect_to_wifi(self) -> None:
        """连接到CQUPT校园网WiFi"""
        ssid_list = ["CQUPT-5G", "CQUPT", "CQUPT-2.4G"]

        # 首先检查是否已经有校园网IP（结合macOS优点）
        wifi_interfaces = self._get_wireless_interfaces()
        for iface in wifi_interfaces:
            if self._has_campus_ip(iface):
                current_network = self._get_current_wifi_network()
                log.info(f"已连接到网络: {current_network}，且有校园网IP，无需重新连接")
                return

        for ssid in ssid_list:
            try:
                log.info(f"尝试连接到 {ssid}")

                # 优先使用 nmcli（如果存在），否则回退到 iwconfig
                if shutil.which("nmcli"):
                    result = subprocess.run(
                        ["nmcli", "device", "wifi", "connect", ssid],
                        capture_output=True,
                        text=True,
                        encoding=locale.getpreferredencoding(),
                        timeout=15,
                    )

                    if result.returncode != 0:
                        log.warning(f"连接 {ssid} 失败: {result.stderr}")
                        continue
                else:
                    # 回退：尝试对每个无线接口设置 ESSID（注意：iwconfig 对 WPA/WPA2 支持有限）
                    wifi_ifaces = self._get_wireless_interfaces()
                    if not wifi_ifaces:
                        log.warning("未检测到无线接口，且 nmcli 不可用，无法连接")
                        continue
                    iw_success = False
                    for iface in wifi_ifaces:
                        try:
                            res = subprocess.run(
                                ["iwconfig", iface, "essid", ssid],
                                capture_output=True,
                                text=True,
                                encoding=locale.getpreferredencoding(),
                                timeout=10,
                            )
                            if res.returncode == 0:
                                iw_success = True
                                break
                            else:
                                log.warning(
                                    f"iwconfig 连接 {ssid} 在接口 {iface} 上失败: {res.stderr}"
                                )
                        except Exception as e:
                            log.warning(f"iwconfig 连接时出错: {e}")
                    if not iw_success:
                        continue

                # 等待连接建立和IP分配（使用轮询，连接后刷新接口列表）
                log.info(f"等待连接到 {ssid} 并获取IP地址...")
                for _ in range(10):
                    time.sleep(1)
                    wifi_interfaces = self._get_wireless_interfaces()
                    for iface in wifi_interfaces:
                        if self._has_campus_ip(iface):
                            current_network = self._get_current_wifi_network()
                            log.info(f"成功连接到 {ssid}，当前网络: {current_network}")
                            return

                log.warning(f"连接到 {ssid} 但未获得校园网IP")

            except Exception as e:
                log.warning(f"连接WiFi {ssid} 时出错: {e}")
                continue

        log.warning("未能连接到任何可用的CQUPT Wi-Fi网络")

    def _is_ethernet_connected(self) -> bool:
        """检查以太网是否连接并获得10.x.x.x的IP"""
        try:
            interfaces = psutil.net_if_addrs()

            # 检查以太网接口 (通常是eth0, enp0s3等)
            for interface_name, addresses in interfaces.items():
                if interface_name.startswith("eth") or interface_name.startswith("enp"):
                    # 检查接口是否活跃
                    stats = psutil.net_if_stats().get(interface_name)
                    if stats and stats.isup:
                        for address in addresses:
                            if (
                                address.family == socket.AF_INET
                                and address.address.startswith("10.")
                            ):
                                log.info(
                                    f"以太网接口 {interface_name} 已连接，IP: {address.address}"
                                )
                                return True
            return False
        except Exception as e:
            log.warning(f"检查以太网连接时出错: {e}")
            return False

    def _is_wifi_connected(self) -> bool:
        """检查WiFi是否连接并获得10.x.x.x的IP"""
        try:
            wifi_interfaces = self._get_wireless_interfaces()
            for interface_name in wifi_interfaces:
                # 检查接口是否活跃且有校园网IP
                stats = psutil.net_if_stats().get(interface_name)
                if stats and stats.isup:
                    if self._has_campus_ip(interface_name):
                        return True
            return False
        except Exception as e:
            log.warning(f"检查WiFi连接时出错: {e}")
            return False

    def get_local_ip(self) -> tuple:
        """获取本地IP地址，返回(连接类型, IP地址)"""
        try:
            # 检查有线连接
            if self._is_ethernet_connected():
                interfaces = psutil.net_if_addrs()
                for interface_name, addresses in interfaces.items():
                    if interface_name.startswith("eth") or interface_name.startswith(
                        "enp"
                    ):
                        stats = psutil.net_if_stats().get(interface_name)
                        if stats and stats.isup:
                            for address in addresses:
                                if (
                                    address.family == socket.AF_INET
                                    and address.address.startswith("10.")
                                ):
                                    log.info(
                                        f"使用有线连接: {interface_name}, IP: {address.address}"
                                    )
                                    return "wired", address.address

            # 检查WiFi连接
            if self._is_wifi_connected():
                wifi_interfaces = self._get_wireless_interfaces()
                for interface_name in wifi_interfaces:
                    stats = psutil.net_if_stats().get(interface_name)
                    if stats and stats.isup:
                        addresses = psutil.net_if_addrs().get(interface_name)
                        if addresses:
                            for address in addresses:
                                if (
                                    address.family == socket.AF_INET
                                    and address.address.startswith("10.")
                                ):
                                    log.info(
                                        f"使用WiFi连接: {interface_name}, IP: {address.address}"
                                    )
                                    return "wireless", address.address

            # 如果没有连接，尝试连接WiFi
            log.info("未检测到校园网连接，尝试连接WiFi")
            self.connect_to_wifi()

            # 再次检查WiFi连接
            time.sleep(5)  # 等待连接稳定
            if self._is_wifi_connected():
                wifi_interfaces = self._get_wireless_interfaces()
                for interface_name in wifi_interfaces:
                    stats = psutil.net_if_stats().get(interface_name)
                    if stats and stats.isup:
                        addresses = psutil.net_if_addrs().get(interface_name)
                        if addresses:
                            for address in addresses:
                                if (
                                    address.family == socket.AF_INET
                                    and address.address.startswith("10.")
                                ):
                                    log.info(
                                        f"连接后使用WiFi: {interface_name}, IP: {address.address}"
                                    )
                                    return "wireless", address.address

            # 如果都没有连接成功
            log.warning("未能获取校园网IP地址")
            return None, None

        except Exception as e:
            log.error(f"获取本地IP地址时出错: {e}")
            return None, None
