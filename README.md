<p align="center">
  <img width="18%" align="center" src="https://github.com/user-attachments/assets/f4baa5c8-60b2-4b29-82c3-df708035d970" alt="logo">
</p>
  <h1 align="center">
  重邮校园网客户端登录
</h1>
<p align="center">
  基于 PyQt6 - Fluent Design 设计
</p>
<p align="center">
  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Win%20%7C%20macOS%20%7C%20Linux-blue?color=#4ec820" alt="Platform Win|macOS|Linux"/>
  </a>
  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue?color=#4ec820" alt="GPLv3"/>
    </a>
    <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/version-2.0.2-blue?color=#4ec820" alt="v2.0.2"/>
  </a>
</p>

### 介绍

本程序基于pyqt6开发，使用pyqt6-fluent-widgets美化组件，提供重邮校园网伪装设备类型，gui登录等。

<img width="1745" height="808" alt="202406061402629" src="https://github.com/user-attachments/assets/18bb179b-1226-4e7b-a13c-a423513d890d" />

### 功能

- [X] 电脑端/移动端切换
- [X] 通过伪装，支持双电脑同时在线
- [X] 特殊登录（已失效）
- [ ] 突破坑位限制-不支持

### 项目结构

```
|----CQUPT_Link.py       	            主程序 ！！！！
|----account.db                         sqlite3数据库 如果没有自动生成
|----connect_db.py        	            连接数据库程序
|----images.py           	            Qt资源文件（图片资源）
|----LICENSE             	            GPL-3.0 license
|----logger.py           	            日志处理
|----login_window.py      	            登录界面
|----logout.py           	            校园网注销
|----README.md           	            README
|----requirements.txt    	            跨平台依赖配置
|----zifuwu.py           	            打开自服务
|----src\                	            多平台架构支持
|    |----factory.py     	            工厂方法
|    |----deprecated\    	            已弃用模块（弃用）
|    |    |----change_mac_csdn.py   	修改mac（弃用）
|    |    |----config.py            	配置文件处理（弃用）
|    |    |----is_admin.py          	跨平台管理员权限检查（弃用）
|    |    |----README.md            	弃用模块说明
|    |----network_manager\ 	            网络管理模块
|    |    |----network_interface.py 	网络接口
|    |    |----network_linux.py     	Linux网络实现
|    |    |----network_macos.py     	MacOS网络实现
|    |    |----network_windows.py   	Windows网络实现
|    |----platform\       	            平台相关模块
|    |    |----platform_interface.py	平台接口
|    |    |----platform_linux.py    	Linux平台实现
|    |    |----platform_macos.py    	MacOS平台实现
|    |    |----platform_windows.py  	Windows平台实现

```

### 自编译

如果您想自行编译源码，在导入requirements后

```
pyinstaller -w -i .\resource\images\favicon.ico CQUPT_Link.py
```

### 特殊登录(已失效)

> 注：特殊登录已于24年07月被学校修复。原功能为破解学校限速，现已失效。非常遗憾的是我们至今仍未知晓破解限速原理。

特殊登录仅供学习交流。

特殊登录在按下登录按钮后不会有任何显示，直到约1分钟后显示结果，期间请不要对本程序有任何操作，若强制关闭导致wifi驱动下线，请自行在设备管理器重新开启/重装wifi驱动。

再次强调，需要静等一分钟，直至出现弹窗。

我们目前需要更多朋友们帮我们完善该程序。

- 当前config.json的间隔时间不稳定，需要更多测试。
- 登录过程无法正常显示进度条。
- 没有网速测速模块。
- 无法python模拟dhcp请求。

如果您可以提供代码上的帮助，欢迎与我们联系，万分感谢。

### 参考

[校园网自动登录全平台解决方案 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/364016452?utm_medium=social&utm_oi=1112727310867927040&utm_id=0)

### 许可证

CQUPT_Link 使用 GPLv3 许可证.

Copyright © 2023 by dullspear
