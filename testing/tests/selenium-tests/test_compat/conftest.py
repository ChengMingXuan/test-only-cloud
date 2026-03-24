"""
test_compat 目录专用 conftest。

这批历史生成用例默认写死 Selenium Grid Remote。当前策略改为：
- Grid 可用时也不依赖 Grid
- 统一把 webdriver.Remote 降到本地浏览器驱动
- 避免整目录因为 Grid 不可达被整套 skip
"""

from selenium import webdriver

from browser_utils import create_local_driver, get_base_url, seed_mock_auth


BASE_URL = get_base_url()


def _browser_name_from_options(options) -> str:
    option_type = type(options).__name__.lower() if options is not None else ""
    if "firefox" in option_type:
        return "firefox"
    if "edge" in option_type:
        return "edge"
    return "chrome"


def _local_remote_driver(command_executor=None, options=None, *args, **kwargs):
    browser_name = _browser_name_from_options(options)
    driver = create_local_driver(browser_name)
    seed_mock_auth(driver, BASE_URL)
    return driver


webdriver.Remote = _local_remote_driver
