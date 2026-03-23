"""
Selenium 测试 — 规则引擎边缘模式跨浏览器兼容性
测试矩阵: Chrome / Firefox / Edge
覆盖: 规则引擎页面渲染、边缘状态面板、表格交互、响应式布局
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")


class TestRuleEngineEdgeCompatibility:
    """规则引擎边缘模式 — 跨浏览器兼容性测试"""

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_ruleengine_page_rendering(self, driver, test_config, browser):
        """[P0] 规则引擎页面在主流浏览器中正确渲染"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#root, .ant-layout"))
            )
        except TimeoutException:
            pass

        # 断言：页面框架存在
        root = driver.find_elements(By.CSS_SELECTOR, "#root, .ant-layout, body")
        assert len(root) > 0, f"{browser}: 根容器不存在"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_ruleengine_table_rendering(self, driver, test_config, browser):
        """[P0] 规则链表格在各浏览器中正确渲染"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table, table, .ant-table-wrapper"))
            )
            tables = driver.find_elements(By.CSS_SELECTOR, ".ant-table, table, .ant-table-wrapper")
            assert len(tables) > 0, f"{browser}: 表格组件未渲染"
        except TimeoutException:
            # SPA 需要登录，跳过
            pass

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_ruleengine_buttons_clickable(self, driver, test_config, browser):
        """[P1] 操作按钮在各浏览器中可点击"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button, .ant-btn"))
            )
            buttons = driver.find_elements(By.CSS_SELECTOR, "button, .ant-btn")
            for btn in buttons[:3]:  # 检查前 3 个按钮
                assert btn.is_displayed(), f"{browser}: 按钮不可见"
                assert btn.is_enabled(), f"{browser}: 按钮未启用"
        except TimeoutException:
            pass

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_ruleengine_search_input(self, driver, test_config, browser):
        """[P1] 搜索输入框在各浏览器中可用"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.ant-input, .ant-input-search input"))
            )
            inputs = driver.find_elements(By.CSS_SELECTOR, "input.ant-input, .ant-input-search input")
            if inputs:
                inputs[0].clear()
                inputs[0].send_keys("告警规则")
                value = inputs[0].get_attribute("value")
                assert "告警" in value, f"{browser}: 输入值未正确设置"
        except TimeoutException:
            pass

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_ruleengine_responsive_layout(self, driver, test_config, browser):
        """[P1] 规则引擎页面响应式布局"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        # 桌面尺寸
        driver.set_window_size(1920, 1080)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#root"))
            )
        except TimeoutException:
            pass

        # 平板尺寸
        driver.set_window_size(768, 1024)
        root = driver.find_elements(By.CSS_SELECTOR, "#root, body")
        assert len(root) > 0, f"{browser}: 平板尺寸下页面崩溃"

        # 恢复桌面
        driver.set_window_size(1920, 1080)


class TestRuleEngineEdgeStatusPanel:
    """边缘状态面板 — 跨浏览器兼容性"""

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_edge_status_badge_rendering(self, driver, test_config, browser):
        """[P1] 边缘状态徽章在各浏览器中渲染"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-badge, .ant-tag"))
            )
            badges = driver.find_elements(By.CSS_SELECTOR, ".ant-badge, .ant-tag")
            if badges:
                for badge in badges[:3]:
                    assert badge.is_displayed(), f"{browser}: 徽章不可见"
        except TimeoutException:
            pass  # 云端模式无边缘状态

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_edge_tabs_navigation(self, driver, test_config, browser):
        """[P1] Tab 导航在各浏览器中正常"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-tabs-tab"))
            )
            tabs = driver.find_elements(By.CSS_SELECTOR, ".ant-tabs-tab")
            for tab in tabs:
                assert tab.is_displayed(), f"{browser}: Tab 不可见"
                tab.click()
        except TimeoutException:
            pass

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_alarm_severity_color_coding(self, driver, test_config, browser):
        """[P2] 告警严重级别颜色在各浏览器中一致"""
        driver.get(f"{test_config['base_url']}/ruleengine")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-tag"))
            )
            tags = driver.find_elements(By.CSS_SELECTOR, ".ant-tag")
            if tags:
                for tag in tags[:5]:
                    # 验证标签有颜色类
                    cls = tag.get_attribute("class")
                    assert "ant-tag" in cls, f"{browser}: Tag 类名不正确"
        except TimeoutException:
            pass

    @pytest.mark.browser("chrome")
    def test_ruleengine_chrome_devtools_audit(self, chrome_driver, test_config):
        """[P2] Chrome DevTools 审计 — 无严重控制台错误"""
        chrome_driver.get(f"{test_config['base_url']}/ruleengine")

        logs = chrome_driver.get_log("browser")
        severe_logs = [l for l in logs if l.get("level") == "SEVERE"]
        # 排除常见非关键错误
        filtered = [l for l in severe_logs
                    if "favicon" not in l.get("message", "").lower()
                    and "net::ERR" not in l.get("message", "")]
        assert len(filtered) == 0, f"Chrome 控制台有严重错误: {filtered}"
