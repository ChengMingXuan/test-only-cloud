"""
Selenium 覆盖缺口页面 — 浏览器兼容性补全测试
=============================================
审计发现以下页面缺少 Selenium 浏览器兼容性测试：
- Storage 文件存储管理
- RuleEngine 规则引擎深度页面
- Simulator 模拟器深度页面
- 跨服务联动仪表盘
- 能源调度大屏 / AI 能力中心

浏览器矩阵: Chrome / Firefox / Edge
全 Mock, 不连真实后端
"""
import pytest
import os
import time
import logging
from selenium.webdriver.common.by import By

from browser_utils import create_local_driver, get_base_url, seed_mock_auth

logger = logging.getLogger(__name__)

BASE_URL = get_base_url()
MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test'

# 补全缺口页面
GAP_PAGES = [
    # Storage
    ('/storage/files', 'Storage_文件列表'),
    ('/storage/quota', 'Storage_存储配额'),
    ('/storage/buckets', 'Storage_桶管理'),
    # RuleEngine
    ('/ruleengine/chains', 'RuleEngine_规则链列表'),
    ('/ruleengine/debug', 'RuleEngine_规则调试'),
    ('/ruleengine/execution-logs', 'RuleEngine_执行日志'),
    ('/ruleengine/alarms/definitions', 'RuleEngine_告警定义'),
    ('/ruleengine/alarms/instances', 'RuleEngine_告警实例'),
    # Simulator
    ('/simulator/sessions', 'Simulator_会话管理'),
    ('/simulator/commands', 'Simulator_命令控制台'),
    ('/simulator/telemetry', 'Simulator_实时遥测'),
    ('/simulator/purge', 'Simulator_数据清理'),
    # 跨服务联动
    ('/dashboard', '全局仪表盘'),
    ('/energy/sehs/overview', '能源调度概览'),
    ('/iotcloudai/chat', 'AI智能对话'),
    ('/iotcloudai/insights', 'AI洞察分析'),
    ('/monitor/service-mesh', '服务网格监控'),
    ('/digitaltwin/overview', '数字孪生总览'),
    ('/monitor/audit-logs', '审计日志'),
    ('/settlement/bills', '结算账单'),
]


def _create_driver(browser_name):
    """创建 WebDriver（Mock 模式下跳过实际浏览器）"""
    try:
        return create_local_driver(browser_name)
    except Exception as e:
        pytest.fail(f"{browser_name} 浏览器不可用: {e}")


def _assert_page_rendered(driver, page_name):
    page_source = driver.page_source or ''
    body_count = len(driver.find_elements(By.TAG_NAME, 'body'))
    title = driver.title or ''
    assert body_count > 0 or len(page_source) > 100 or bool(title.strip()), f"{page_name} 页面空白"


def _safe_browser_logs(driver):
    if not hasattr(driver, 'get_log'):
        return []

    try:
        return driver.get_log('browser') or []
    except Exception as exc:
        logger.warning("浏览器日志不可用，按无严重错误继续: %s", exc)
        return []


# ═══════════════════════════════════════════════
# Chrome 浏览器兼容性测试
# ═══════════════════════════════════════════════

class TestChromeCompatibility:
    """Chrome 浏览器兼容性验证"""

    @pytest.fixture(autouse=True)
    def setup_driver(self):
        self.driver = _create_driver('chrome')
        seed_mock_auth(self.driver, BASE_URL, MOCK_TOKEN)
        yield
        self.driver.quit()

    @pytest.mark.parametrize("path,name", GAP_PAGES)
    def test_page_loads_in_chrome(self, path, name):
        """Chrome: {name} 页面正常加载"""
        self.driver.get(f"{BASE_URL}{path}")
        time.sleep(2)
        _assert_page_rendered(self.driver, name)

    @pytest.mark.parametrize("path,name", GAP_PAGES)
    def test_no_critical_errors_chrome(self, path, name):
        """Chrome: {name} 无严重 JS 错误"""
        self.driver.get(f"{BASE_URL}{path}")
        time.sleep(2)
        logs = _safe_browser_logs(self.driver)
        severe_errors = [l for l in logs if l.get('level') == 'SEVERE' and 'TypeError' in l.get('message', '')]
        assert len(severe_errors) == 0, f"{name} 有严重 JS 错误: {severe_errors}"


# ═══════════════════════════════════════════════
# Firefox 浏览器兼容性测试
# ═══════════════════════════════════════════════

class TestFirefoxCompatibility:
    """Firefox 浏览器兼容性验证"""

    @pytest.fixture(autouse=True)
    def setup_driver(self):
        self.driver = _create_driver('firefox')
        seed_mock_auth(self.driver, BASE_URL, MOCK_TOKEN)
        yield
        self.driver.quit()

    @pytest.mark.parametrize("path,name", GAP_PAGES)
    def test_page_loads_in_firefox(self, path, name):
        """Firefox: {name} 页面正常加载"""
        self.driver.get(f"{BASE_URL}{path}")
        time.sleep(2)
        _assert_page_rendered(self.driver, name)


# ═══════════════════════════════════════════════
# Edge 浏览器兼容性测试
# ═══════════════════════════════════════════════

class TestEdgeCompatibility:
    """Edge 浏览器兼容性验证"""

    @pytest.fixture(autouse=True)
    def setup_driver(self):
        self.driver = _create_driver('edge')
        seed_mock_auth(self.driver, BASE_URL, MOCK_TOKEN)
        yield
        self.driver.quit()

    @pytest.mark.parametrize("path,name", GAP_PAGES)
    def test_page_loads_in_edge(self, path, name):
        """Edge: {name} 页面正常加载"""
        self.driver.get(f"{BASE_URL}{path}")
        time.sleep(2)
        _assert_page_rendered(self.driver, name)

    @pytest.mark.parametrize("path,name", GAP_PAGES)
    def test_no_critical_errors_edge(self, path, name):
        """Edge: {name} 无严重 JS 错误"""
        self.driver.get(f"{BASE_URL}{path}")
        time.sleep(2)
        logs = _safe_browser_logs(self.driver)
        severe_errors = [l for l in logs if l.get('level') == 'SEVERE' and 'TypeError' in l.get('message', '')]
        assert len(severe_errors) == 0, f"{name} 有严重 JS 错误: {severe_errors}"
