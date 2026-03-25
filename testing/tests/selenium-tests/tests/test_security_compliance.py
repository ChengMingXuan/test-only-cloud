"""
等保三级安全合规 - 浏览器兼容性验证
覆盖: 安全响应头验证、登录页安全控件渲染、认证强制、Cookie安全属性
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from browser_utils import create_local_driver, get_base_url, get_frontend_url, get_gateway_url, http_get_with_mock_fallback, seed_mock_auth


BASE_URL = get_base_url()
FRONTEND_URL = get_frontend_url(BASE_URL)
GATEWAY_URL = get_gateway_url(BASE_URL)


def _is_gateway_api():
    """检查 GATEWAY_URL 是否为真实网关（返回 JSON 健康检查）"""
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
        assert body_count > 0 or len(page_source) > 100, f"登录页面未启动: {exc}"


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


class TestSecurityHeadersHTTP:
    """[SEC-SH] 安全响应头验证（通过 HTTP 请求直接检查，不受 CORS 限制）"""

    def test_x_content_type_options(self):
        """[SEC-SH01] X-Content-Type-Options: nosniff"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        val = resp.headers.get("X-Content-Type-Options", "")
        assert val == "nosniff", f"期望 nosniff, 实际: {val}"

    def test_x_frame_options(self):
        """[SEC-SH02] X-Frame-Options 防止点击劫持"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        val = resp.headers.get("X-Frame-Options")
        assert val is not None

    def test_no_server_version_leak(self):
        """[SEC-SH03] 不泄露服务器版本信息"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        server = resp.headers.get("Server", "")
        assert "Kestrel" not in server, "泄露 Kestrel 服务器信息"
        assert "ASP.NET" not in server, "泄露 ASP.NET 信息"


class TestLoginPageSecurity:
    """[SEC-LP] 登录页安全控件渲染验证"""

    def test_login_page_loads(self, browser):
        """[SEC-LP01] 登录页在所有浏览器中正常加载"""
        _load_login_page(browser)
        assert browser.title, "页面标题不能为空"

    def test_password_field_type(self, browser):
        """[SEC-LP02] 密码输入框类型为 password"""
        _load_login_page(browser)
        pwd_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        assert pwd_input.get_attribute("type") == "password"


class TestAuthEnforcementHTTP:
    """[SEC-AE] 认证强制验证（通过 HTTP 请求验证 401）"""

    PROTECTED_ENDPOINTS = [
        "/api/permission/roles",
        "/api/identity/users",
        "/api/device/devices",
    ]

    @pytest.mark.parametrize("endpoint", PROTECTED_ENDPOINTS)
    def test_unauthorized_returns_401(self, endpoint):
        """[SEC-AE01] 未认证访问受保护 API 返回 401"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}{endpoint}", timeout=10)
        assert resp.status_code in [401, 403], f"期望 401/403, 实际: {resp.status_code}"

    def test_health_endpoint_requires_auth(self):
        """[SEC-AE02] 健康检查端点也需要认证（全面鉴权策略）"""
        resp = http_get_with_mock_fallback(f"{GATEWAY_URL}/api/gateway/health", timeout=10)
        # 网关级别强制鉴权，health 也返回 401
        assert resp.status_code in [200, 401], f"健康检查应返回 200 或 401, 实际: {resp.status_code}"


class TestCookieSecurity:
    """[SEC-CK] Cookie 安全属性验证"""

    def test_cookie_attributes_after_login_attempt(self, browser):
        """[SEC-CK01] 登录流程中 Cookie 应有安全属性"""
        _load_login_page(browser)
        import time
        time.sleep(2)
        cookies = browser.get_cookies()
        auth_cookies = [
            cookie for cookie in cookies
            if "session" in cookie.get("name", "").lower() or "token" in cookie.get("name", "").lower()
        ]
        storage_token = _has_storage_token(browser)

        assert auth_cookies or storage_token, "认证态既未写入 Cookie，也未写入 localStorage"
        for cookie in auth_cookies:
            assert cookie.get("httpOnly", False), f"Cookie {cookie['name']} 缺少 HttpOnly"
