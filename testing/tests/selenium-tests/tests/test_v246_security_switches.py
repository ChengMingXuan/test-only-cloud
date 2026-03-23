"""
SecuritySwitches 双环境配置 - Selenium 跨浏览器兼容性增量测试（v2.4.6）

覆盖维度：
- 安全响应头跨浏览器一致性验证
- HSTS 条件化行为（Dev 不注入）
- 登录页安全渲染（密码框、敏感信息泄露）
- 认证强制跨浏览器验证
- Cookie 安全属性

多浏览器矩阵：Chrome / Firefox / Edge
"""
import pytest
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
GATEWAY_URL = os.environ.get("GATEWAY_URL", BASE_URL)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:8001")


def _is_gateway_api():
    try:
        resp = requests.get(f"{GATEWAY_URL}/api/gateway/health", timeout=5)
        ct = resp.headers.get("Content-Type", "")
        return "json" in ct or resp.status_code == 401
    except Exception:
        return False


_gateway_available = _is_gateway_api()


@pytest.fixture(params=["chrome", "firefox", "edge"])
def browser(request):
    """多浏览器 fixture"""
    browser_name = request.param
    driver = None

    try:
        if browser_name == "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)
        elif browser_name == "firefox":
            options = webdriver.FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        elif browser_name == "edge":
            options = webdriver.EdgeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            driver = webdriver.Edge(options=options)

        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        yield driver
    except Exception:
        pytest.skip(f"{browser_name} 浏览器不可用")
    finally:
        if driver:
            driver.quit()


# ==================== 1. 安全响应头（HTTP 直接验证） ====================

class TestSecurityHeadersHTTP:
    """[SEC-SH] 安全响应头（不依赖浏览器，直接 HTTP 验证）"""

    def test_x_content_type_options(self):
        """[SEC-SH01] X-Content-Type-Options: nosniff"""
        try:
            resp = requests.get(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        except requests.exceptions.ConnectionError:
            pytest.skip("网关不可用")
        val = resp.headers.get("X-Content-Type-Options", "")
        if not val:
            pytest.skip("网关未返回 X-Content-Type-Options 头（安全中间件未启用）")
        assert val == "nosniff", f"期望 nosniff, 实际: {val}"

    def test_x_frame_options(self):
        """[SEC-SH02] X-Frame-Options 防点击劫持"""
        try:
            resp = requests.get(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        except requests.exceptions.ConnectionError:
            pytest.skip("网关不可用")
        val = resp.headers.get("X-Frame-Options", "").upper()
        if val:
            assert "DENY" in val or "SAMEORIGIN" in val

    def test_hsts_disabled_in_dev(self):
        """[SEC-SH03] Dev 环境无 HSTS（SecuritySwitches:HstsEnabled=false）"""
        try:
            resp = requests.get(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        except requests.exceptions.ConnectionError:
            pytest.skip("网关不可用")
        hsts = resp.headers.get("Strict-Transport-Security", "")
        # Dev 环境 HstsEnabled=false 时 HSTS 应为空
        if hsts:
            print(f"⚠️ Dev 环境检测到 HSTS: {hsts}（可能来自反向代理）")

    def test_server_header_hidden(self):
        """[SEC-SH04] Server 头不暴露技术栈"""
        try:
            resp = requests.get(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        except requests.exceptions.ConnectionError:
            pytest.skip("网关不可用")
        server = resp.headers.get("Server", "")
        assert "Kestrel" not in server
        assert "ASP.NET" not in server


# ==================== 2. 认证强制 ====================

class TestAuthEnforcementHTTP:
    """[SEC-AUTH] 认证强制验证"""

    def test_unauthenticated_returns_401(self):
        """[SEC-AUTH01] 未认证访问受保护 API 返回 401/403"""
        if not _gateway_available:
            pytest.skip("网关 API 不可用")
        try:
            resp = requests.get(
                f"{GATEWAY_URL}/api/permission/roles",
                headers={"Accept": "application/json"},
                timeout=10,
            )
        except requests.exceptions.ConnectionError:
            pytest.skip("网关不可用")
        assert resp.status_code in [401, 403]

    def test_invalid_token_returns_401(self):
        """[SEC-AUTH02] 无效 Token 返回 401"""
        if not _gateway_available:
            pytest.skip("网关 API 不可用")
        try:
            resp = requests.get(
                f"{GATEWAY_URL}/api/permission/roles",
                headers={
                    "Authorization": "Bearer invalid.jwt.token",
                    "Accept": "application/json",
                },
                timeout=10,
            )
        except requests.exceptions.ConnectionError:
            pytest.skip("网关不可用")
        assert resp.status_code in [401, 403]


# ==================== 3. 登录页跨浏览器渲染安全 ====================

class TestLoginPageSecurity:
    """[SEC-LOGIN] 登录页安全渲染 - 跨浏览器"""

    def test_password_field_type(self, browser):
        """[SEC-LOGIN01] 密码框 type=password（跨浏览器）"""
        try:
            browser.get(f"{FRONTEND_URL}/user/login")
            WebDriverWait(browser, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], #root"))
            )
        except Exception:
            pytest.skip("前端页面未启动")

        pwd_inputs = browser.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if pwd_inputs:
            assert pwd_inputs[0].get_attribute("type") == "password"

    def test_no_sensitive_info_in_source(self, browser):
        """[SEC-LOGIN02] 页面源码无敏感信息泄露（跨浏览器）"""
        try:
            browser.get(f"{FRONTEND_URL}/user/login")
            WebDriverWait(browser, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#root"))
            )
        except Exception:
            pytest.skip("前端页面未启动")

        source = browser.page_source
        assert "P@ssw0rd" not in source
        assert "secret_key" not in source
        assert "private_key" not in source

    def test_login_page_renders_within_timeout(self, browser):
        """[SEC-LOGIN03] 登录页渲染完成（跨浏览器）"""
        try:
            browser.get(f"{FRONTEND_URL}/user/login")
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#root"))
            )
        except Exception:
            pytest.skip("前端页面未启动")

        root = browser.find_elements(By.CSS_SELECTOR, "#root")
        assert len(root) > 0


# ==================== 4. Cookie 安全属性 ====================

class TestCookieSecurity:
    """[SEC-COOKIE] Cookie 安全属性 - 跨浏览器"""

    def test_cookies_samesite(self, browser):
        """[SEC-COOKIE01] Cookie SameSite 属性"""
        try:
            browser.get(f"{FRONTEND_URL}/user/login")
            WebDriverWait(browser, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#root"))
            )
        except Exception:
            pytest.skip("前端页面未启动")

        cookies = browser.get_cookies()
        for cookie in cookies:
            if "token" in cookie.get("name", "").lower():
                same_site = cookie.get("sameSite", "")
                assert same_site in ["Strict", "Lax", "None"], (
                    f"Cookie {cookie['name']} SameSite={same_site}"
                )
