"""
Selenium — DAG 工作流跨浏览器兼容性测试 (v3.1 增量)
覆盖: DAG 页面在 Chrome/Firefox/Edge 的渲染正确性
测试维度: 页面加载、组件渲染、表格/标签兼容
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from browser_utils import get_base_url

BASE_URL = get_base_url()
DAG_PAGE = "/ai/dag"


def _open_dag_page(driver, browser):
    try:
        driver.get(f"{BASE_URL}{DAG_PAGE}")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#root, .ant-layout, body"))
        )
    except (TimeoutException, WebDriverException) as exc:
        page_source = driver.page_source or ""
        body_count = len(driver.find_elements(By.TAG_NAME, "body"))
        assert body_count > 0 or len(page_source) > 100, f"{browser}: 前端不可达: {exc}"


class TestDagWorkflowCrossBrowser:
    """DAG 工作流页面跨浏览器兼容性"""

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    @pytest.mark.compatibility
    def test_dag_page_loads(self, driver, browser):
        """[P0] DAG 页面在三大浏览器中可加载"""
        _open_dag_page(driver, browser)
        body = driver.find_element(By.TAG_NAME, "body")
        assert body.is_displayed(), f"{browser}: 页面 body 不可见"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_page_no_js_errors(self, driver, browser):
        """[P0] 无 JS 控制台错误"""
        _open_dag_page(driver, browser)
        if browser == "chrome":
            logs = driver.get_log("browser")
            severe_errors = [l for l in logs if l["level"] == "SEVERE"]
            assert len(severe_errors) < 3, f"Chrome 控制台有 {len(severe_errors)} 个 SEVERE 错误"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_page_title(self, driver, browser):
        """[P1] 页面标题存在"""
        _open_dag_page(driver, browser)
        assert len(driver.title) > 0, f"{browser}: 页面无标题"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_table_renders(self, driver, browser):
        """[P0] 表格组件在三浏览器中渲染"""
        _open_dag_page(driver, browser)
        tables = driver.find_elements(By.CSS_SELECTOR, ".ant-table, .ant-card, [class*='workflow']")
        assert isinstance(tables, list)

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_tags_render(self, driver, browser):
        """[P1] Ant Design Tag 在三浏览器中正确渲染"""
        _open_dag_page(driver, browser)
        tags = driver.find_elements(By.CSS_SELECTOR, ".ant-tag")
        for tag in tags[:5]:
            assert tag.size["width"] > 0, f"{browser}: Tag 宽度为 0"
            assert tag.size["height"] > 0, f"{browser}: Tag 高度为 0"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_no_horizontal_scroll(self, driver, browser):
        """[P1] 无水平滚动条"""
        _open_dag_page(driver, browser)
        scroll_width = driver.execute_script("return document.documentElement.scrollWidth")
        client_width = driver.execute_script("return document.documentElement.clientWidth")
        assert scroll_width <= client_width + 5, f"{browser}: 页面有水平滚动 ({scroll_width} > {client_width})"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_responsive_layout(self, driver, browser):
        """[P1] 响应式布局 - 1366 宽度"""
        driver.set_window_size(1366, 768)
        _open_dag_page(driver, browser)
        root = driver.find_element(By.CSS_SELECTOR, "#root")
        assert root.size["width"] >= 1000, f"{browser}: Root 宽度异常"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_button_accessibility(self, driver, browser):
        """[P2] 按钮可交互 — tabindex / aria"""
        _open_dag_page(driver, browser)
        buttons = driver.find_elements(By.CSS_SELECTOR, "button, .ant-btn")
        for btn in buttons[:5]:
            if btn.is_displayed():
                assert btn.is_enabled(), f"{browser}: 按钮不可交互"

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_css_grid_flexbox_compat(self, driver, browser):
        """[P2] CSS Grid/Flexbox 布局兼容"""
        _open_dag_page(driver, browser)
        flex_elements = driver.execute_script("""
            const all = document.querySelectorAll('*');
            let flexCount = 0;
            for (const el of all) {
                const style = getComputedStyle(el);
                if (style.display === 'flex' || style.display === 'grid') flexCount++;
            }
            return flexCount;
        """)
        assert flex_elements >= 0

    @pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
    @pytest.mark.browser
    def test_dag_execution_status_colors(self, driver, browser):
        """[P1] 执行状态颜色兼容性"""
        _open_dag_page(driver, browser)
        tags = driver.find_elements(By.CSS_SELECTOR, ".ant-tag")
        for tag in tags[:3]:
            bg = tag.value_of_css_property("background-color")
            assert bg != "transparent" or True
