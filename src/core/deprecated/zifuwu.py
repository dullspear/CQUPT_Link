"""自服务

使用 DrissionPage 进行网页自动化操作。
"""

# TODO: 需要爬虫+完善网页自动化服务功能，需要contributor参与
from DrissionPage import ChromiumOptions, ChromiumPage


def setup_browser():
    """配置浏览器选项

    Returns:
        ChromiumOptions: 配置好的浏览器选项
    """
    path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_browser_path(path).save()
    co.ignore_certificate_errors(True)
    return co


def auto_login(account, password):
    """自动登录校园网自助服务

    Args:
        account: 账号
        password: 密码

    Returns:
        response: 响应对象
    """
    cp = ChromiumPage()

    cp.get("https://202.202.32.120:8443/Self/login/")

    cp.ele("css:#account").input(account)
    cp.ele("css:#password").input(password)
    cp.ele("css:.btn.btn-primary.btn-block").click()

    response = cp.listen.wait().response

    return response


if __name__ == "__main__":
    # 测试代码
    setup_browser()
