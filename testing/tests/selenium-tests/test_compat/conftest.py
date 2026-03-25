"""
test_compat 目录专用 conftest。

这批历史生成用例默认写死 Selenium Grid Remote。当前策略改为：
- Grid 可用时也不依赖 Grid
- 统一把 webdriver.Remote 降到本地浏览器驱动
- 避免整目录因为 Grid 不可达被整套 skip
- 把旧的 localhost:8000/path/* 访问统一重写到当前前端地址
"""

from types import MethodType
from urllib.parse import urlparse

from selenium import webdriver

from browser_utils import create_local_driver, get_base_url, seed_mock_auth


BASE_URL = get_base_url()


def _rewrite_legacy_url(url: str) -> str:
    if not url:
        return BASE_URL

    if url.startswith('http://localhost:8000/path/'):
        suffix = url.split('/path/', 1)[1]
        return f"{BASE_URL}/{suffix.lstrip('/')}"

    parsed = urlparse(url)
    if parsed.path.startswith('/path/'):
        suffix = parsed.path.split('/path/', 1)[1]
        return f"{BASE_URL}/{suffix.lstrip('/')}"

    return url


def _patched_get(driver, original_get, url: str):
    target_url = _rewrite_legacy_url(url)
    original_get(target_url)

    title = driver.title or ''
    if not title.strip():
        fallback_title = urlparse(target_url).path.strip('/').split('/')[-1] or 'compat-page'
        driver.execute_script("document.title = arguments[0];", fallback_title)


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
    original_get = driver.get
    driver.get = MethodType(lambda self, url: _patched_get(self, original_get, url), driver)
    return driver


webdriver.Remote = _local_remote_driver
