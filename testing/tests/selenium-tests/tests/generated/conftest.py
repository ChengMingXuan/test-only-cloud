"""
generated/ 目录专用 conftest — 覆盖 driver fixture：
  - scope="module" 每个测试文件共享一个 Chrome 实例（大幅提速）
  - 默认 headless（无头）模式
  - 使用 data: URL 做 base URL 注入兼容性测试所需 DOM 结构
"""
import os
import pytest
from browser_utils import create_local_driver


@pytest.fixture(scope="session")
def driver(request):
    """
    Session 级 headless Chrome 驱动。
    整个测试会话共用一个浏览器实例（最快）。
    """
    _driver = create_local_driver("chrome")

    _driver.implicitly_wait(3)
    _driver.set_page_load_timeout(20)

    yield _driver

    _driver.quit()
