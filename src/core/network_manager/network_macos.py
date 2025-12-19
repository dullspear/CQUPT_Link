import locale
import socket
import subprocess
import time

import psutil

from src.core.logger import log
from src.core.network_manager.network_interface import INetwork


class NetworkMacOS(INetwork):
    def __init__(self):
        # macOS不需要特殊的启动信息配置
        self.wifi_interface = self._get_wifi_interface()
        log.info(f"检测到WiFi接口: {self.wifi_interface}")

    def _get_wifi_interface(self) -> str:
        """动态获取WiFi接口名称"""
        try:
            # 使用networksetup获取所有硬件端口
            result = subprocess.run(
                ["networksetup", "-listallhardwareports"],
                capture_output=True,
                encoding=locale.getpreferredencoding(),
                text=True,
                timeout=10,
            )

            lines = result.stdout.split("\n")
            for i, line in enumerate(lines):
                if "Wi-Fi" in line:
                    # 下一行包含设备名称
                    if i + 1 < len(lines):
                        device_line = lines[i + 1]
                        if device_line.startswith("Device:"):
                            device = device_line.split(":")[1].strip()
                            log.info(f"找到WiFi接口: {device}")
                            return device

            # 如果没找到，尝试常见的接口名
            for interface in ["en1", "en0", "en2"]:
                if self._is_wifi_interface(interface):
                    log.info(f"使用备用WiFi接口: {interface}")
                    return interface

            log.warning("未找到WiFi接口，使用默认值 en1")
            return "en1"

        except Exception as e:
            log.warning(f"获取WiFi接口时出错: {e}，使用默认值 en1")
            return "en1"

    def _is_wifi_interface(self, interface: str) -> bool:
        """检查指定接口是否为WiFi接口"""
        try:
            result = subprocess.run(
                ["networksetup", "-getairportnetwork", interface],
                capture_output=True,
                text=True,
                encoding=locale.getpreferredencoding(),
                timeout=5,
            )
            # 如果命令成功执行且没有报错，说明是WiFi接口
            return (
                result.returncode == 0 and "not a Wi-Fi interface" not in result.stderr
            )
        except Exception:
            return False

    def _get_current_wifi_network(self) -> str:
        """获取当前连接的WiFi网络名称"""
        try:
            # 方法1: 使用networksetup
            result = subprocess.run(
                ["networksetup", "-getairportnetwork", self.wifi_interface],
                capture_output=True,
                text=True,
                encoding=locale.getpreferredencoding(),
                timeout=5,
            )

            if result.returncode == 0 and "Current Wi-Fi Network:" in result.stdout:
                network_name = result.stdout.split("Current Wi-Fi Network:")[1].strip()
                if (
                    network_name
                    and network_name
                    != "You are not associated with an AirPort network."
                ):
                    return network_name

            # 方法2: 使用system_profiler（更可靠但较慢）
            result = subprocess.run(
                ["system_profiler", "SPAirPortDataType"],
                capture_output=True,
                text=True,
                encoding=locale.getpreferredencoding(),
                timeout=10,
            )

            # 查找当前连接的网络
            lines = result.stdout.split("\n")
            for i, line in enumerate(lines):
                if "Current Network Information:" in line:
                    # 查找网络名称
                    for j in range(i, min(i + 10, len(lines))):
                        if lines[j].strip().endswith(":") and not lines[
                            j
                        ].strip().startswith("Current"):
                            network_name = lines[j].strip().rstrip(":")
                            if network_name:
                                return network_name

            return None

        except Exception as e:
            log.warning(f"获取当前WiFi网络时出错: {e}")
            return None

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

    def connect_to_wifi(self) -> None:
        """连接到CQUPT校园网WiFi"""
        ssid_list = ["CQUPT-5G", "CQUPT", "CQUPT-2.4G"]

        # 首先检查是否已经有校园网IP
        if self._has_campus_ip(self.wifi_interface):
            current_network = self._get_current_wifi_network()
            log.info(f"已连接到网络: {current_network}，且有校园网IP，无需重新连接")
            return

        for ssid in ssid_list:
            try:
                log.info(f"尝试连接到 {ssid}")

                # 使用networksetup连接WiFi
                result = subprocess.run(
                    ["networksetup", "-setairportnetwork", self.wifi_interface, ssid],
                    capture_output=True,
                    text=True,
                    encoding=locale.getpreferredencoding(),
                    timeout=15,
                )

                if result.returncode != 0:
                    log.warning(f"连接 {ssid} 失败: {result.stderr}")
                    continue

                # 等待连接建立和IP分配
                log.info(f"等待连接到 {ssid} 并获取IP地址...")
                for _ in range(10):  # 最多等待20秒
                    time.sleep(2)

                    # 检查是否获得校园网IP
                    if self._has_campus_ip(self.wifi_interface):
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

            # 检查所有以太网接口 (通常是en0, en2, en3等，但不是WiFi接口)
            for interface_name, addresses in interfaces.items():
                if (
                    interface_name.startswith("en")
                    and interface_name != self.wifi_interface
                    and interface_name != "en0"
                ):  # en0通常是主以太网，但在某些Mac上可能是WiFi
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
            # 检查WiFi接口是否活跃且有校园网IP
            stats = psutil.net_if_stats().get(self.wifi_interface)
            if stats and stats.isup:
                return self._has_campus_ip(self.wifi_interface)

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
                    if (
                        interface_name.startswith("en")
                        and interface_name != self.wifi_interface
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
                interfaces = psutil.net_if_addrs().get(self.wifi_interface)
                if interfaces:
                    for address in interfaces:
                        if (
                            address.family == socket.AF_INET
                            and address.address.startswith("10.")
                        ):
                            log.info(
                                f"使用WiFi连接: {self.wifi_interface}, IP: {address.address}"
                            )
                            return "wireless", address.address

            # 如果没有连接，尝试连接WiFi
            log.info("未检测到校园网连接，尝试连接WiFi")
            self.connect_to_wifi()

            # 再次检查WiFi连接
            time.sleep(5)  # 等待连接稳定
            if self._is_wifi_connected():
                interfaces = psutil.net_if_addrs().get(self.wifi_interface)
                if interfaces:
                    for address in interfaces:
                        if (
                            address.family == socket.AF_INET
                            and address.address.startswith("10.")
                        ):
                            log.info(
                                f"连接后使用WiFi: {self.wifi_interface}, IP: {address.address}"
                            )
                            return "wireless", address.address

            # 如果都没有连接成功
            log.warning("未能获取校园网IP地址")
            return None, None

        except Exception as e:
            log.error(f"获取本地IP地址时出错: {e}")
            return None, None
