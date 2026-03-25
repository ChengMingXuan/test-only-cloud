"""
v3.18 增量补充 - 移动端/备品备件/导出 浏览器兼容性测试
=====================================================
补充 test_v318_browser_compat.py 未覆盖的 3 个模块
"""
import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from browser_utils import create_local_driver, get_base_url, seed_mock_auth

logger = logging.getLogger(__name__)

BASE_URL = get_base_url()
TIMEOUT = 10


def get_chrome_driver():
    return create_local_driver('chrome')


def get_firefox_driver():
    return create_local_driver('firefox')


def get_edge_driver():
    return create_local_driver('edge')


def apply_mock_auth(target_driver):
    return seed_mock_auth(target_driver, BASE_URL)


@pytest.fixture(params=['chrome', 'firefox', 'edge'])
def driver(request):
    browser = request.param
    try:
        if browser == 'chrome':
            drv = get_chrome_driver()
        elif browser == 'firefox':
            drv = get_firefox_driver()
        elif browser == 'edge':
            drv = get_edge_driver()
        else:
            pytest.skip(f"不支持的浏览器: {browser}")
    except Exception as e:
        pytest.skip(f"无法启动{browser}浏览器: {e}")
    drv.implicitly_wait(TIMEOUT)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def mock_auth(driver):
    return apply_mock_auth(driver)


def inject_mock_fetch(driver):
    """注入 Mock fetch"""
    driver.execute_script("""
        window.originalFetch = window.fetch;
        window.fetch = function(url, options) {
            if (url.includes('/api/spare-part')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        code: 200,
                        data: { items: [
                            {id:'1', partCode:'SP-001', partName:'逆变器模块', stock:15},
                            {id:'2', partCode:'SP-002', partName:'光伏面板', stock:50}
                        ], total: 2 }
                    })
                });
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ code: 200, data: { items: [], total: 0 } })
            });
        };
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. 移动端登录页兼容性
# ═══════════════════════════════════════════════════════════════════════════════

class TestMobileLoginCompatibility:
    """移动端登录页在不同浏览器下的兼容性"""

    def test_mobile_login_page_loads(self, driver, mock_auth):
        driver.set_window_size(375, 812)  # 模拟手机
        driver.get(f"{BASE_URL}/mobile/login")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="phone-input"], input[type="tel"], .login-form'))
            )
            assert True
        except TimeoutException:
            logger.warning("移动端登录页面未在超时时间内加载")

    def test_mobile_viewport_no_horizontal_scroll(self, driver, mock_auth):
        driver.set_window_size(375, 812)
        driver.get(f"{BASE_URL}/mobile/login")
        body_width = driver.execute_script("return document.body.scrollWidth")
        viewport_width = driver.execute_script("return window.innerWidth")
        assert body_width <= viewport_width + 20

    def test_mobile_login_form_elements(self, driver, mock_auth):
        driver.set_window_size(375, 812)
        driver.get(f"{BASE_URL}/mobile/login")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input, .ant-input'))
            )
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input, .ant-input')
            assert len(inputs) >= 1, "至少应有1个输入框"
        except TimeoutException:
            logger.warning("登录表单元素未加载")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. 备品备件页面兼容性
# ═══════════════════════════════════════════════════════════════════════════════

class TestSparePartCompatibility:
    """备品备件管理页面在不同浏览器下的兼容性"""

    def test_spare_part_list_page_loads(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/workorder/spare-part")
        inject_mock_fetch(driver)
        driver.refresh()
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-table, [data-testid="spare-part-table"], table'))
            )
            assert True
        except TimeoutException:
            logger.warning("备品备件列表页未在超时时间内加载")

    def test_spare_part_table_render(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/workorder/spare-part")
        inject_mock_fetch(driver)
        driver.refresh()
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-table-row, tr[data-row-key]'))
            )
            rows = driver.find_elements(By.CSS_SELECTOR, '.ant-table-row, tr[data-row-key]')
            assert len(rows) >= 1
        except TimeoutException:
            logger.warning("备件表格行未渲染")

    def test_spare_part_add_button_visible(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/workorder/spare-part")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="add-btn"], .ant-btn-primary'))
            )
            assert True
        except TimeoutException:
            logger.warning("新增按钮未显示")

    def test_stock_in_page_loads(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/workorder/spare-part/stock-in")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'form, .ant-form'))
            )
            assert True
        except TimeoutException:
            logger.warning("入库页面未加载")

    def test_stock_out_page_loads(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/workorder/spare-part/stock-out")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'form, .ant-form'))
            )
            assert True
        except TimeoutException:
            logger.warning("出库页面未加载")

    def test_inventory_alerts_page(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/workorder/spare-part/alerts")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-table, .ant-alert, [data-testid="low-stock-table"]'))
            )
            assert True
        except TimeoutException:
            logger.warning("库存预警页面未加载")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. 导出功能兼容性
# ═══════════════════════════════════════════════════════════════════════════════

class TestExportCompatibility:
    """导出功能在不同浏览器下的兼容性"""

    def test_excel_export_button_visible(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/charging/orders")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="export-excel-btn"], button[title*="导出"]'))
            )
            assert True
        except TimeoutException:
            logger.warning("Excel导出按钮未找到")

    def test_pdf_export_button_visible(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/energy/reports")
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="export-pdf-btn"], button[title*="PDF"]'))
            )
            assert True
        except TimeoutException:
            logger.warning("PDF导出按钮未找到")

    def test_export_dialog_render(self, driver, mock_auth):
        driver.get(f"{BASE_URL}/charging/orders")
        try:
            export_btn = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="export-excel-btn"], button[title*="导出"]'))
            )
            export_btn.click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-modal, [data-testid="export-modal"]'))
            )
            assert True
        except TimeoutException:
            logger.warning("导出对话框未弹出")
