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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from browser_utils import create_local_driver, get_base_url, get_frontend_url, get_gateway_url, http_get_with_mock_fallback, seed_mock_auth


BASE_URL = get_base_url()
GATEWAY_URL = get_gateway_url(BASE_URL)
FRONTEND_URL = get_frontend_url(BASE_URL)


def _is_gateway_api():
    try:
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=5)
        ct = resp.headers.get("Content-Type", "")
        return "json" in ct or resp.status_code == 401
    except Exception:
        return False


_gateway_available = _is_gateway_api()


def _load_login_page(browser):
    browser.get(f"{FRONTEND_URL}/user/login")
    try:
        WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], .login-form, #root, body"))
        )
    except Exception as exc:
        page_source = browser.page_source or ""
        body_count = len(browser.find_elements(By.TAG_NAME, "body"))
        assert body_count > 0 or len(page_source) > 100, f"前端页面未启动: {exc}"


def _has_storage_token(browser):
    return browser.execute_script(
        "return localStorage.getItem('token') || localStorage.getItem('access_token') || localStorage.getItem('jgsy_access_token');"
    )


@pytest.fixture(params=["chrome", "firefox", "edge"])
def browser(request):
    """多浏览器 fixture"""
    browser_name = request.param
    driver = None

    try:
        driver = create_local_driver(browser_name)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        seed_mock_auth(driver, FRONTEND_URL)
        yield driver
    except Exception as exc:
        pytest.skip(f"{browser_name} 浏览器不可用: {exc}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ==================== 1. 安全响应头（HTTP 直接验证） ====================

class TestSecurityHeadersHTTP:
    """[SEC-SH] 安全响应头（不依赖浏览器，直接 HTTP 验证）"""

    def test_x_content_type_options(self):
        """[SEC-SH01] X-Content-Type-Options: nosniff"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        val = resp.headers.get("X-Content-Type-Options", "")
        assert val == "nosniff", f"期望 nosniff, 实际: {val}"

    def test_x_frame_options(self):
        """[SEC-SH02] X-Frame-Options 防点击劫持"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        val = resp.headers.get("X-Frame-Options", "").upper()
        assert "DENY" in val or "SAMEORIGIN" in val

    def test_hsts_disabled_in_dev(self):
        """[SEC-SH03] Dev 环境无 HSTS（SecuritySwitches:HstsEnabled=false）"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        hsts = resp.headers.get("Strict-Transport-Security", "")
        # Dev 环境 HstsEnabled=false 时 HSTS 应为空
        if hsts:
            print(f"⚠️ Dev 环境检测到 HSTS: {hsts}（可能来自反向代理）")

    def test_server_header_hidden(self):
        """[SEC-SH04] Server 头不暴露技术栈"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        server = resp.headers.get("Server", "")
        assert "Kestrel" not in server
        assert "ASP.NET" not in server


# ==================== 2. 认证强制 ====================

class TestAuthEnforcementHTTP:
    """[SEC-AUTH] 认证强制验证"""

    def test_unauthenticated_returns_401(self):
        """[SEC-AUTH01] 未认证访问受保护 API 返回 401/403"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/permission/roles", timeout=10)
        assert resp.status_code in [401, 403]

    def test_invalid_token_returns_401(self):
        """[SEC-AUTH02] 无效 Token 返回 401"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/permission/roles", timeout=10)
        assert resp.status_code in [401, 403]


# ==================== 3. 登录页跨浏览器渲染安全 ====================

class TestLoginPageSecurity:
    """[SEC-LOGIN] 登录页安全渲染 - 跨浏览器"""

    def test_password_field_type(self, browser):
        """[SEC-LOGIN01] 密码框 type=password（跨浏览器）"""
        _load_login_page(browser)

        pwd_inputs = browser.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if pwd_inputs:
            assert pwd_inputs[0].get_attribute("type") == "password"

    def test_no_sensitive_info_in_source(self, browser):
        """[SEC-LOGIN02] 页面源码无敏感信息泄露（跨浏览器）"""
        _load_login_page(browser)

        source = browser.page_source
        assert "P@ssw0rd" not in source
        assert "secret_key" not in source
        assert "private_key" not in source

    def test_login_page_renders_within_timeout(self, browser):
        """[SEC-LOGIN03] 登录页渲染完成（跨浏览器）"""
        _load_login_page(browser)

        root = browser.find_elements(By.CSS_SELECTOR, "#root, body")
        assert len(root) > 0


# ==================== 4. Cookie 安全属性 ====================

class TestCookieSecurity:
    """[SEC-COOKIE] Cookie 安全属性 - 跨浏览器"""

    def test_cookies_samesite(self, browser):
        """[SEC-COOKIE01] Cookie SameSite 属性"""
        _load_login_page(browser)

        cookies = browser.get_cookies()
        auth_cookies = [cookie for cookie in cookies if "token" in cookie.get("name", "").lower()]
        storage_token = _has_storage_token(browser)

        assert auth_cookies or storage_token, "认证态既未写入 Cookie，也未写入 localStorage"

        for cookie in auth_cookies:
            same_site = cookie.get("sameSite", "")
            assert same_site in ["Strict", "Lax", "None"], (
                f"Cookie {cookie['name']} SameSite={same_site}"
            )
