"""
generated/ 目录专用 conftest — 覆盖 driver fixture：
  - scope="module" 每个测试文件共享一个 Chrome 实例（大幅提速）
  - 默认 headless（无头）模式
  - 使用 data: URL 做 base URL 注入兼容性测试所需 DOM 结构
"""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

try:
    from webdriver_manager.chrome import ChromeDriverManager
    _USE_WDM = True
except ImportError:
    _USE_WDM = False


# 每次启动 Chrome 都使用同一可执行路径缓存（避免重复下载）
_DRIVER_EXEC = None


def _get_driver_path():
    global _DRIVER_EXEC
    if _DRIVER_EXEC is None and _USE_WDM:
        os.environ.setdefault("WDM_LOCAL", "1")
        _DRIVER_EXEC = ChromeDriverManager().install()
    return _DRIVER_EXEC


@pytest.fixture(scope="session")
def driver(request):
    """
    Session 级 headless Chrome 驱动。
    整个测试会话共用一个浏览器实例（最快）。
    """
    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--log-level=3")

    driver_path = _get_driver_path()
    if driver_path:
        svc = ChromeService(executable_path=driver_path)
        _driver = webdriver.Chrome(service=svc, options=opts)
    else:
        _driver = webdriver.Chrome(options=opts)

    _driver.implicitly_wait(3)
    _driver.set_page_load_timeout(20)

    yield _driver

    _driver.quit()
