# 转载修改自 Csdn : https://blog.csdn.net/zhu6201976

import ctypes
import platform
import random
import re
import subprocess
import sys
import winreg

import chardet

from src.core.logger import log
from src.core.user_settings_manager import user_settings_manager


class SetMac:
    """
    修改 本地连接 mac地址
    """

    def __init__(self, kind="wireless"):
        # regex to MAC address like 00-00-00-00-00-00 or 00:00:00:00:00:00 or
        # 000000000000
        self.MAC_ADDRESS_RE = re.compile(
            r"""
            ([0-9A-F]{1,2})[:-]?
            ([0-9A-F]{1,2})[:-]?
            ([0-9A-F]{1,2})[:-]?
            ([0-9A-F]{1,2})[:-]?
            ([0-9A-F]{1,2})[:-]?
            ([0-9A-F]{1,2})
            """,
            re.I | re.VERBOSE,
        )  # re.I: case-insensitive matching. re.VERBOSE: just look nicer.

        self.WIN_REGISTRY_PATH = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"

        self.kind = kind

        # Set up the STARTUPINFO to hide the console window
        self.startupinfo = subprocess.STARTUPINFO()
        self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.startupinfo.wShowWindow = subprocess.SW_HIDE

    def is_admin(self):
        """
        is user an admin?
        :return:
        """
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            log.info(
                "Sorry! You should run this with administrative privileges if you want to change your MAC address."
            )
            sys.exit()
        else:
            log.info("admin")

    def get_macinfos(self):
        """
        查看所有mac信息
        :return:
        """
        log.info("=" * 50)
        try:
            mac_info = subprocess.check_output(
                "GETMAC /v /FO list",
                stderr=subprocess.STDOUT,
                startupinfo=self.startupinfo,
            )
            # 使用chardet检测编码
            result = chardet.detect(mac_info)
            encoding = result["encoding"]
            user_settings_manager.set_encoding(
                encoding
            )  # deprecated: 仅用于此deprecated模块
            mac_info = mac_info.decode(
                user_settings_manager.get_encoding()
            )  # deprecated: 仅用于此deprecated模块
            log.info("Your MAC address:\n " + "\n".join(mac_info.split("\n")[:11]))
        except subprocess.CalledProcessError as e:
            log.info(e.output)
            log.info(e.returncode)

    def get_target_device(self):
        """
        返回 本地连接 网络适配器
        :return:
        """
        mac_info = subprocess.check_output(
            "GETMAC /v /FO list", stderr=subprocess.STDOUT, startupinfo=self.startupinfo
        )
        # 使用chardet检测编码
        result = chardet.detect(mac_info)
        encoding = result["encoding"]
        user_settings_manager.set_encoding(
            encoding
        )  # deprecated: 仅用于此deprecated模块
        mac_info = mac_info.decode(
            user_settings_manager.get_encoding()
        )  # deprecated: 仅用于此deprecated模块

        if self.kind == "wireless":
            search = re.search(
                r"(WLAN)\s+(网络适配器:|Network Adapter:)(.+)\s+(物理地址:|Physical Address:)",
                mac_info,
            )
        else:
            search = re.search(
                r"(本地连接|以太网)\s+(网络适配器:|Network Adapter:)(.+)\s+(物理地址:|Physical Address:)",
                mac_info,
            )
        target_name, target_device = (
            (search.group(1), search.group(3).strip()) if search else ("", "")
        )
        if not all([target_name, target_device]):
            log.info("Cannot find the target device")
            sys.exit()

        log.info("target_name " + target_name)
        log.info("target_device " + target_device)
        return target_device

    import random

    def generate_random_mac(self):
        # 第一个字节必须是2、6、A或E
        first_byte = random.choice([0x02, 0x06, 0x0A, 0x0E])

        # 生成剩余的5个字节
        remaining_bytes = [random.randint(0x00, 0xFF) for _ in range(5)]

        # 组合成MAC地址
        mac_address = [first_byte] + remaining_bytes
        mac_address_str = "".join(["%02X" % byte for byte in mac_address])

        return mac_address_str

    def set_mac_address(self, target_device, new_mac):
        """
        设置新mac地址
        :param target_device: 本地连接 网络适配器
        :param new_mac: 新mac地址
        :return:
        """
        if not self.MAC_ADDRESS_RE.match(new_mac):
            log.info("Please input a correct MAC address")
            return
        log.info("当前setmac: " + new_mac)
        # Locate adapter's registry and update network address (mac)
        reg_hdl = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg_hdl, self.WIN_REGISTRY_PATH)
        info = winreg.QueryInfoKey(key)

        # Find adapter key based on sub keys
        adapter_key = None
        adapter_path = None
        target_index = -1

        for index in range(info[0]):
            subkey = winreg.EnumKey(key, index)
            path = self.WIN_REGISTRY_PATH + "\\" + subkey

            if subkey == "Properties":
                break

            # Check for adapter match for appropriate interface
            new_key = winreg.OpenKey(reg_hdl, path)
            try:
                adapterDesc = winreg.QueryValueEx(new_key, "DriverDesc")
                if adapterDesc[0] == target_device:
                    adapter_path = path
                    target_index = index
                    break
                else:
                    winreg.CloseKey(new_key)
            except OSError as err:
                if err.errno == 2:  # register value not found, ok to ignore
                    pass
                else:
                    raise err

        if adapter_path is None:
            log.info("Device not found.")
            winreg.CloseKey(key)
            winreg.CloseKey(reg_hdl)
            return
        print("device found")
        print(adapter_path)
        # Registry path found update mac addr
        adapter_key = winreg.OpenKey(reg_hdl, adapter_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(adapter_key, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
        winreg.CloseKey(adapter_key)
        winreg.CloseKey(key)
        winreg.CloseKey(reg_hdl)

        # Adapter must be restarted in order for change to take affect
        # log.info 'Now you should restart your netsh'
        self.restart_adapter(target_index, target_device)

    def restart_adapter(self, target_index, target_device):
        """
        Disables and then re-enables device interface
        """
        print(target_index)
        if platform.release() == "XP":
            # description, adapter_name, address, current_address = find_interface(device)
            cmd = "devcon hwids =net"
            try:
                result = subprocess.check_output(
                    cmd, stderr=subprocess.STDOUT, startupinfo=self.startupinfo
                )
            except FileNotFoundError:
                raise
            query = (
                "(" + target_device + "\r\n\\s*.*:\r\n\\s*)PCI\\\\(([A-Z]|[0-9]|_|&)*)"
            )
            query = query.encode("ascii")
            match = re.search(query, result)
            cmd = 'devcon restart "PCI\\' + str(match.group(2).decode("ascii")) + '"'
            subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, startupinfo=self.startupinfo
            )
        else:
            cmd = (
                "wmic path win32_networkadapter where index="
                + str(target_index)
                + " call disable"
            )
            subprocess.check_output(cmd, startupinfo=self.startupinfo)
            cmd = (
                "wmic path win32_networkadapter where index="
                + str(target_index)
                + " call enable"
            )
            subprocess.check_output(cmd, startupinfo=self.startupinfo)

    def run(self, new_mac=None):
        self.is_admin()
        self.get_macinfos()
        target_device = self.get_target_device()
        if new_mac is None:
            self.set_mac_address(target_device, self.generate_random_mac())
        else:
            self.set_mac_address(target_device, new_mac)
        self.get_macinfos()


if __name__ == "__main__":
    set_mac = SetMac("wireless")
    set_mac.run()
