"""登出服务模块

提供查询在线用户信息、强制下线等网络服务功能。
"""

import json

import requests


def query_user_info(username):
    """查询用户在线信息

    Args:
        username: 用户账号

    Returns:
        dict: 用户在线信息
    """
    params = {
        "c": "Portal",
        "a": "online_list",
        "user_account": username,
    }
    r = requests.get(
        url="http://192.168.200.2:801/eportal", params=params, verify=False, timeout=10
    )
    print(r)
    print(r.text)
    result = json.loads(r.text[1:-1])
    print(result)
    return result


def print_user_info(username, user_info):
    """打印用户在线信息

    Args:
        username: 用户账号
        user_info: 用户在线信息字典
    """
    if user_info["result"] == "0":
        print(f"  无法找到 {username} 的在线信息: {user_info['msg']}")
        print("")
        return

    print(f"用户 {username} 的在线信息:")
    print("")

    for i, session in enumerate(user_info["list"]):
        if i != 0:
            print("  -----------------------------")
        print(f"  Session: #{i}")
        print(f"  上线时间: {session['online_time']}")
        print(f"  在线 IP : {session['online_ip']}")
        print(f"  在线 MAC: {session['online_mac']}")
        print(f"  上行数据: {session['uplink_bytes']} bytes")
        print(f"  下载数据: {session['downlink_bytes']} bytes")
        print("")


def fuck_user1(username, ip, mac):
    """解绑用户 MAC 地址

    Args:
        username: 用户账号
        ip: IP 地址
        mac: MAC 地址

    Returns:
        dict: 操作结果
    """
    params = {
        "c": "Portal",
        "a": "unbind_mac",
        "user_account": username,
        "wlan_user_ip": ip,
        "wlan_user_mac": "",
        "jsVersion": "3.3.3",
        "v": "4026",
    }
    r = requests.get(
        url="http://192.168.200.2:801/eportal", params=params, verify=False, timeout=10
    )
    return json.loads(r.text[1:-1])


def fuck_user2(ip, mac):
    """强制用户下线

    Args:
        ip: IP 地址
        mac: MAC 地址

    Returns:
        dict: 操作结果
    """
    params = {
        "c": "Portal",
        "a": "logout",
        "login_method": "1",
        "user_account": "123",
        "user_password": "123",
        "wlan_user_ip": ip,
        "wlan_user_mac": mac,
        "ac_logout": "1",
        "register_mode": "1",
        "wlan_user_ipv6": "",
        "wlan_vlan_id": "1",
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "3.3.3",
        "v": "5225",
    }
    r = requests.get(
        url="http://192.168.200.2:801/eportal", params=params, verify=False, timeout=10
    )
    print(r.text)
    return json.loads(r.text[1:-1])


def fuck_user(username, user_info):
    """强制用户所有会话下线

    Args:
        username: 用户账号
        user_info: 用户在线信息字典
    """
    print("")
    if user_info["msg"] == "在线数据为空":
        return

    for i, session in enumerate(user_info["list"]):
        if i != 0:
            print("  -----------------------------")
        print(
            f"  F**king Session: #{i}\tIP: {session['online_ip']}\tMAC: {session['online_mac']}"
        )
        print("  强制下线 ...")
        status1 = fuck_user1(username, session["online_ip"], session["online_mac"])
        print(f"  {status1['msg']}")
        print("  解绑 MAC ...")
        status2 = fuck_user2(session["online_ip"], session["online_mac"])
        print(f"  {status2['msg']}")
        print("")


if __name__ == "__main__":
    username = ""
    print(f"Username : {username}")
    print("-------------------------------------------")

    user_info = query_user_info(username)
    print_user_info(username, user_info)

    fuck_user(username, user_info)
