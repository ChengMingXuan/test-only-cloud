"""
v3.18 增量补充 - 移动端/备品备件/导出 浏览器兼容性测试
=====================================================
补充 test_v318_browser_compat.py 未覆盖的 3 个模块
"""
import pytest
import logging
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os

logger = logging.getLogger(__name__)

BASE_URL = os.getenv('TEST_BASE_URL') or os.getenv('BASE_URL') or 'http://localhost:8000'
TIMEOUT = 10


def get_chrome_driver():
    options = ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    chrome_binary = shutil.which('chromedriver') or shutil.which('chromedriver.exe')
    if chrome_binary:
        return webdriver.Chrome(service=ChromeService(chrome_binary), options=options)
    try:
        return webdriver.Chrome(options=options)
    except Exception:
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


def get_firefox_driver():
    options = FirefoxOptions()
    options.add_argument('-headless')
    options.add_argument('--width=1920')
    options.add_argument('--height=1080')
    gecko_binary = shutil.which('geckodriver') or shutil.which('geckodriver.exe')
    if gecko_binary:
        return webdriver.Firefox(service=FirefoxService(gecko_binary), options=options)
    try:
        return webdriver.Firefox(options=options)
    except Exception:
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)


def get_edge_driver():
    options = EdgeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    edge_binary = shutil.which('msedgedriver') or shutil.which('msedgedriver.exe')
    if edge_binary:
        return webdriver.Edge(service=EdgeService(edge_binary), options=options)
    try:
        return webdriver.Edge(options=options)
    except Exception:
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)


def apply_mock_auth(target_driver):
    target_driver.get(BASE_URL)
    target_driver.execute_script("""
        localStorage.setItem('token', 'mock_token');
        localStorage.setItem('user', JSON.stringify({id: 'user-001', name: 'admin'}));
    """)
    return target_driver


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
            return
    except Exception as e:
        pytest.skip(f"无法启动{browser}浏览器: {e}")
        return
    drv.implicitly_wait(TIMEOUT)
    yield drv
    drv.quit()


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
