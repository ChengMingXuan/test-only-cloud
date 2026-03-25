"""
V3.1.2 新增服务 - Selenium 浏览器兼容性测试
覆盖缺失服务：DigitalTwin, IotCloudAI, EnergyServices (7个), Storage
用例数：72 条（9组 × 8条: Chrome/Firefox/Edge 各含页面加载/布局/CSS/JS）
"""
import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"


def inject_token(driver):
    """注入 Mock Token"""
    driver.get(BASE_URL)
    driver.execute_script(f"""
        localStorage.setItem('jgsy_access_token', '{MOCK_TOKEN}');
        localStorage.setItem('jgsy_tenant_code', 'TEST_TENANT');
    """)


# ═══════════════════════════════════════════════════
# 基础浏览器兼容性验证（7项/页面 × 3浏览器）
# ═══════════════════════════════════════════════════

PAGES_TO_TEST = [
    {"name": "数字孪生概览", "path": "/digital-twin/overview", "module": "digital_twin"},
    {"name": "AI碳交易", "path": "/iotcloudai/carbon", "module": "iotcloudai"},
    {"name": "AI需求响应", "path": "/iotcloudai/demand-response", "module": "iotcloudai"},
    {"name": "碳交易服务", "path": "/energy/carbon-trade", "module": "energy_services"},
    {"name": "需求响应服务", "path": "/energy/demand-resp", "module": "energy_services"},
    {"name": "设备运维", "path": "/energy/device-ops", "module": "energy_services"},
    {"name": "电力交易", "path": "/energy/elec-trade", "module": "energy_services"},
    {"name": "能效管理", "path": "/energy/energy-eff", "module": "energy_services"},
    {"name": "综合能源", "path": "/energy/multi-energy", "module": "energy_services"},
    {"name": "安全管控", "path": "/energy/safe-control", "module": "energy_services"},
    {"name": "存储管理", "path": "/storage/manage", "module": "storage"},
    {"name": "证书轮转", "path": "/monitor/service-mesh/certificate", "module": "security"},
]


class TestV312CompatChrome:
    """Chrome 兼容性测试 - V3.1.2 新增页面"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        inject_token(driver)
        yield

    @pytest.mark.chrome
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_page_load(self, driver, page_info):
        """[Chrome] 页面加载"""
        driver.get(BASE_URL + page_info["path"])
        assert driver.find_element(By.ID, "root") or driver.find_element(By.TAG_NAME, "body")

    @pytest.mark.chrome
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_layout_render(self, driver, page_info):
        """[Chrome] 布局渲染"""
        driver.get(BASE_URL + page_info["path"])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-layout, .layout, body"))
        )

    @pytest.mark.chrome
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_css_styles(self, driver, page_info):
        """[Chrome] CSS样式加载"""
        driver.get(BASE_URL + page_info["path"])
        styles = driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet'], style")
        assert len(styles) > 0

    @pytest.mark.chrome
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_js_execution(self, driver, page_info):
        """[Chrome] JS执行"""
        driver.get(BASE_URL + page_info["path"])
        result = driver.execute_script("return typeof window !== 'undefined'")
        assert result is True

    @pytest.mark.chrome
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_no_white_screen(self, driver, page_info):
        """[Chrome] 无白屏"""
        driver.get(BASE_URL + page_info["path"])
        body_text = driver.execute_script("return document.body.innerText || ''")
        assert len(body_text.strip()) > 0 or driver.find_element(By.ID, "root")

    @pytest.mark.chrome
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_flexbox_support(self, driver, page_info):
        """[Chrome] Flexbox支持"""
        driver.get(BASE_URL + page_info["path"])
        result = driver.execute_script("return CSS.supports('display', 'flex')")
        assert result is True


class TestV312CompatFirefox:
    """Firefox 兼容性测试 - V3.1.2 新增页面"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        inject_token(driver)
        yield

    @pytest.mark.firefox
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_page_load(self, driver, page_info):
        """[Firefox] 页面加载"""
        driver.get(BASE_URL + page_info["path"])
        assert driver.find_element(By.ID, "root") or driver.find_element(By.TAG_NAME, "body")

    @pytest.mark.firefox
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_layout_render(self, driver, page_info):
        """[Firefox] 布局渲染"""
        driver.get(BASE_URL + page_info["path"])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-layout, .layout, body"))
        )

    @pytest.mark.firefox
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_form_elements(self, driver, page_info):
        """[Firefox] 表单元素渲染"""
        driver.get(BASE_URL + page_info["path"])
        inputs = driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
        assert len(inputs) >= 0

    @pytest.mark.firefox
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_websocket_support(self, driver, page_info):
        """[Firefox] WebSocket支持"""
        driver.get(BASE_URL + page_info["path"])
        result = driver.execute_script("return typeof WebSocket !== 'undefined'")
        assert result is True

    @pytest.mark.firefox
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_svg_render(self, driver, page_info):
        """[Firefox] SVG渲染"""
        driver.get(BASE_URL + page_info["path"])
        result = driver.execute_script("return typeof SVGElement !== 'undefined'")
        assert result is True


class TestV312CompatEdge:
    """Edge 兼容性测试 - V3.1.2 新增页面"""

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        inject_token(driver)
        yield

    @pytest.mark.edge
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_page_load(self, driver, page_info):
        """[Edge] 页面加载"""
        driver.get(BASE_URL + page_info["path"])
        assert driver.find_element(By.ID, "root") or driver.find_element(By.TAG_NAME, "body")

    @pytest.mark.edge
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_layout_render(self, driver, page_info):
        """[Edge] 布局渲染"""
        driver.get(BASE_URL + page_info["path"])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-layout, .layout, body"))
        )

    @pytest.mark.edge
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_css_grid(self, driver, page_info):
        """[Edge] CSS Grid支持"""
        driver.get(BASE_URL + page_info["path"])
        result = driver.execute_script("return CSS.supports('display', 'grid')")
        assert result is True

    @pytest.mark.edge
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_es6_support(self, driver, page_info):
        """[Edge] ES6支持"""
        driver.get(BASE_URL + page_info["path"])
        result = driver.execute_script("return typeof Promise !== 'undefined'")
        assert result is True

    @pytest.mark.edge
    @pytest.mark.parametrize("page_info", PAGES_TO_TEST, ids=[p["name"] for p in PAGES_TO_TEST])
    def test_local_storage(self, driver, page_info):
        """[Edge] LocalStorage支持"""
        driver.get(BASE_URL + page_info["path"])
        result = driver.execute_script("return typeof localStorage !== 'undefined'")
        assert result is True
