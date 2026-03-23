"""
Selenium 测试配置文件
AIOPS 平台跨浏览器兼容性测试

核心特性:
- Selenium Grid 分布式执行
- 多浏览器×多版本矩阵
- 老旧浏览器支持
- 移动浏览器模拟
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os
import json
from datetime import datetime
from pathlib import Path

# ========== 测试配置 ==========

# WebDriver Manager 缓存目录 — 指向 D 盘项目内，避免写入 C 盘 %USERPROFILE%\.wdm
_wdm_cache = str(Path(__file__).parent.parent.parent / ".test-cache" / "webdriver")
os.environ.setdefault("WDM_LOCAL", "1")

TEST_CONFIG = {
    "base_url": os.getenv("TEST_BASE_URL", "http://localhost:8000"),
    "implicit_wait": 10,  # 隐式等待秒数
    "page_load_timeout": 30,  # 页面加载超时
    "screenshot_dir": "../test-reports/selenium-report/screenshots",
    "log_dir": "../test-reports/selenium-report/logs",
    "grid_url": os.getenv("SELENIUM_GRID_URL", "http://localhost:4444"),  # Selenium Grid地址
}

# ========== pytest Fixtures ==========

@pytest.fixture(scope="session")
def test_config():
    """测试配置"""
    return TEST_CONFIG


@pytest.fixture(scope="function")
def driver(request):
    """
    根据pytest标记动态创建WebDriver
    
    使用方式:
    @pytest.mark.browser("chrome")
    def test_something(driver):
        driver.get("https://example.com")
    """
    browser_marker = request.node.get_closest_marker("browser")
    if browser_marker and browser_marker.args:
        browser = browser_marker.args[0]
    else:
        # 从 parametrize 的 "browser" 参数中获取，或默认 chrome
        browser = request.node.callspec.params.get("browser", "chrome") if hasattr(request.node, "callspec") else "chrome"
    
    use_grid = request.config.getoption("--use-grid", default=False)
    headless = request.config.getoption("--headless", default=False)
    
    if use_grid:
        _driver = _create_remote_driver(browser, headless)
    else:
        _driver = _create_local_driver(browser, headless)
    
    # 设置超时
    _driver.implicitly_wait(TEST_CONFIG["implicit_wait"])
    _driver.set_page_load_timeout(TEST_CONFIG["page_load_timeout"])
    
    # 最大化窗口
    _driver.maximize_window()
    
    yield _driver
    
    # 失败时截图
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        _take_screenshot(_driver, request.node.name)
    
    # 清理
    _driver.quit()


@pytest.fixture(scope="function")
def chrome_driver(request):
    """Chrome浏览器专用fixture"""
    options = ChromeOptions()
    if request.config.getoption("--headless"):
        options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = ChromeService(ChromeDriverManager().install())
    _driver = webdriver.Chrome(service=service, options=options)
    
    _driver.implicitly_wait(TEST_CONFIG["implicit_wait"])
    _driver.maximize_window()
    
    yield _driver
    
    if request.node.rep_call.failed:
        _take_screenshot(_driver, request.node.name)
    
    _driver.quit()


@pytest.fixture(scope="function")
def firefox_driver(request):
    """Firefox浏览器专用fixture"""
    options = FirefoxOptions()
    if request.config.getoption("--headless"):
        options.add_argument("--headless")
    
    service = FirefoxService(GeckoDriverManager().install())
    _driver = webdriver.Firefox(service=service, options=options)
    
    _driver.implicitly_wait(TEST_CONFIG["implicit_wait"])
    _driver.maximize_window()
    
    yield _driver
    
    if request.node.rep_call.failed:
        _take_screenshot(_driver, request.node.name)
    
    _driver.quit()


@pytest.fixture(scope="function")
def edge_driver(request):
    """Edge浏览器专用fixture"""
    options = EdgeOptions()
    if request.config.getoption("--headless"):
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    
    service = EdgeService(EdgeChromiumDriverManager().install())
    _driver = webdriver.Edge(service=service, options=options)
    
    _driver.implicitly_wait(TEST_CONFIG["implicit_wait"])
    _driver.maximize_window()
    
    yield _driver
    
    if request.node.rep_call.failed:
        _take_screenshot(_driver, request.node.name)
    
    _driver.quit()


@pytest.fixture(scope="function")
def mobile_chrome_driver(request):
    """移动Chrome浏览器（模拟）"""
    mobile_emulation = {
        "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36"
    }
    
    options = ChromeOptions()
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    service = ChromeService(ChromeDriverManager().install())
    _driver = webdriver.Chrome(service=service, options=options)
    
    _driver.implicitly_wait(TEST_CONFIG["implicit_wait"])
    
    yield _driver
    
    if request.node.rep_call.failed:
        _take_screenshot(_driver, request.node.name)
    
    _driver.quit()


# ========== Helper Functions ==========

def _create_local_driver(browser: str, headless: bool = False):
    """创建本地WebDriver"""
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    
    elif browser == "safari":
        # Safari不需要service（仅macOS）
        return webdriver.Safari()
    
    else:
        raise ValueError(f"不支持的浏览器: {browser}")


def _create_remote_driver(browser: str, headless: bool = False):
    """创建Selenium Grid远程WebDriver"""
    capabilities = {
        "browserName": browser,
        "platformName": "Linux",  # 或 "Windows", "macOS"
    }
    
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        return webdriver.Remote(
            command_executor=TEST_CONFIG["grid_url"],
            options=options
        )
    
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Remote(
            command_executor=TEST_CONFIG["grid_url"],
            options=options
        )
    
    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Remote(
            command_executor=TEST_CONFIG["grid_url"],
            options=options
        )
    
    else:
        raise ValueError(f"Grid不支持的浏览器: {browser}")


def _take_screenshot(driver, test_name: str):
    """测试失败时截图"""
    screenshot_dir = Path(TEST_CONFIG["screenshot_dir"])
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.png"
    filepath = screenshot_dir / filename
    
    driver.save_screenshot(str(filepath))
    print(f"截图已保存: {filepath}")


# ========== pytest Hooks ==========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """获取测试结果，用于失败时截图"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_addoption(parser):
    """添加命令行选项"""
    try:
        parser.addoption(
            "--use-grid",
            action="store_true",
            default=False,
            help="使用Selenium Grid执行测试"
        )
    except Exception:
        pass
    try:
        parser.addoption(
            "--headless",
            action="store_true",
            default=False,
            help="无头浏览器模式"
        )
    except Exception:
        pass
    try:
        parser.addoption(
            "--browser",
            action="store",
            default="chrome",
            help="指定浏览器: chrome, firefox, edge, safari"
        )
    except Exception:
        pass


def pytest_configure(config):
    """pytest配置钩子"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "browser(name): 指定浏览器运行测试"
    )
    config.addinivalue_line(
        "markers", "compatibility: 兼容性测试"
    )
    config.addinivalue_line(
        "markers", "cross_browser: 跨浏览器测试"
    )
    config.addinivalue_line(
        "markers", "mobile: 移动浏览器测试"
    )
    
    # 创建报告目录
    Path(TEST_CONFIG["screenshot_dir"]).mkdir(parents=True, exist_ok=True)
    Path(TEST_CONFIG["log_dir"]).mkdir(parents=True, exist_ok=True)
    
    # 记录测试开始时间
    config.start_time = datetime.now()


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束"""
    end_time = datetime.now()
    duration = (end_time - session.config.start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print(f"Selenium 测试执行完成")
    print(f"总耗时: {duration:.2f}秒")
    print(f"退出状态: {exitstatus}")
    print(f"{'='*60}\n")
    
    # 生成简洁摘要
    summary = {
        "tool": "selenium",
        "timestamp": end_time.isoformat(),
        "duration_seconds": duration,
        "exit_status": exitstatus,
    }
    
    summary_path = Path("../test-reports/selenium-report/summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
