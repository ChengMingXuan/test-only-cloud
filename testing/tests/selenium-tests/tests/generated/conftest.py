"""
generated/ 目录专用 conftest — 覆盖 driver fixture：
  - 按测试标记选择对应浏览器，避免跨浏览器用例被错误地全部跑成 Chrome
  - 默认 headless（无头）模式
  - 每条用例独立驱动，避免大批 generated 用例状态串扰
"""
import os
import pytest
from browser_utils import create_local_driver, get_base_url, seed_mock_auth


@pytest.fixture(scope="function")
def driver(request):
    """
  按测试标记动态创建 headless 浏览器驱动。
    """
  browser_marker = request.node.get_closest_marker("browser")
  if browser_marker and browser_marker.args:
    browser_name = browser_marker.args[0]
  else:
    marker_names = {marker.name for marker in request.node.iter_markers()}
    if "firefox" in marker_names:
      browser_name = "firefox"
    elif "edge" in marker_names:
      browser_name = "edge"
    else:
      browser_name = "chrome"

  _driver = create_local_driver(browser_name)

    _driver.implicitly_wait(3)
    _driver.set_page_load_timeout(20)
  seed_mock_auth(_driver, get_base_url())

    yield _driver

    _driver.quit()
