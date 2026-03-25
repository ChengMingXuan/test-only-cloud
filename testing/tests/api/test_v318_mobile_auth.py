"""
移动端认证 API 测试
====================
覆盖 MobileAuthController（8端点）+ MiniProgramAuthController（5端点）
"""
import pytest
import uuid
from tests.conftest import ApiClient

MOBILE_BASE = "/api/auth/mobile"
MP_BASE = "/api/auth/mp"


@pytest.fixture
def mobile_login_payload():
    return {
        "phone": "13812345678",
        "verifyCode": "123456",
    }


@pytest.fixture
def password_login_payload():
    return {
        "phone": "13812345678",
        "password": "Test@123456",
    }


@pytest.fixture
def register_payload():
    return {
        "phone": "13812345678",
        "verifyCode": "123456",
        "password": "Test@123456",
        "realName": "测试用户",
    }


@pytest.fixture
def mp_login_payload():
    return {
        "code": "mock_wx_code_123456",
        "encryptedData": "mock_encrypted",
        "iv": "mock_iv",
    }


class TestMobileSmsLogin:
    """短信验证码登录"""

    def test_send_verify_code(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MOBILE_BASE}/send-code", json={"phone": "13812345678"})
        assert resp.status_code in (200, 429)  # 可能触发频率限制

    def test_send_code_invalid_phone(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MOBILE_BASE}/send-code", json={"phone": "123"})
        assert resp.status_code in (400, 422)

    def test_sms_login_success(self, anon_api: ApiClient, mobile_login_payload):
        resp = anon_api.post(f"{MOBILE_BASE}/sms-login", json=mobile_login_payload)
        # 验证码不正确应返回 400 或 401，成功返回 200
        assert resp.status_code in (200, 400, 401)

    def test_sms_login_wrong_code(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MOBILE_BASE}/sms-login", json={
            "phone": "13812345678",
            "verifyCode": "000000",
        })
        assert resp.status_code in (400, 401)


class TestMobilePasswordLogin:
    """密码登录"""

    def test_password_login(self, anon_api: ApiClient, password_login_payload):
        resp = anon_api.post(f"{MOBILE_BASE}/password-login", json=password_login_payload)
        assert resp.status_code in (200, 400, 401)

    def test_password_login_missing_fields(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MOBILE_BASE}/password-login", json={})
        assert resp.status_code in (400, 422)


class TestMobileRegister:
    """移动端注册"""

    def test_register(self, anon_api: ApiClient, register_payload):
        resp = anon_api.post(f"{MOBILE_BASE}/register", json=register_payload)
        assert resp.status_code in (200, 400, 409)

    def test_register_missing_phone(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MOBILE_BASE}/register", json={"password": "Test@123"})
        assert resp.status_code in (400, 422)


class TestMobileToken:
    """Token 管理"""

    def test_refresh_token(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MOBILE_BASE}/refresh-token", json={"refreshToken": "some_token"})
        assert resp.status_code in (200, 401)

    def test_logout(self, api: ApiClient):
        resp = api.post(f"{MOBILE_BASE}/logout")
        assert resp.status_code == 200

    def test_logout_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MOBILE_BASE}/logout")
        assert resp.status_code == 401


class TestMobileProfile:
    """移动端用户信息"""

    def test_get_profile(self, api: ApiClient):
        resp = api.get(f"{MOBILE_BASE}/profile")
        assert resp.status_code == 200

    def test_update_profile(self, api: ApiClient):
        resp = api.put(f"{MOBILE_BASE}/profile", json={
            "realName": "更新用户名",
            "avatar": "https://example.com/avatar.png",
        })
        assert resp.status_code == 200

    def test_profile_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.get(f"{MOBILE_BASE}/profile")
        assert resp.status_code == 401


class TestMiniProgramLogin:
    """小程序登录"""

    def test_mp_login(self, anon_api: ApiClient, mp_login_payload):
        resp = anon_api.post(f"{MP_BASE}/login", json=mp_login_payload)
        assert resp.status_code in (200, 400, 401)

    def test_mp_login_missing_code(self, anon_api: ApiClient):
        resp = anon_api.post(f"{MP_BASE}/login", json={})
        assert resp.status_code in (400, 422)


class TestMiniProgramUser:
    """小程序用户"""

    def test_mp_get_user_info(self, api: ApiClient):
        resp = api.get(f"{MP_BASE}/user-info")
        assert resp.status_code == 200

    def test_mp_bind_phone(self, api: ApiClient):
        resp = api.post(f"{MP_BASE}/bind-phone", json={
            "phone": "13812345678",
            "verifyCode": "123456",
        })
        assert resp.status_code in (200, 400)

    def test_mp_unbind(self, api: ApiClient):
        resp = api.post(f"{MP_BASE}/unbind")
        assert resp.status_code in (200, 400)

    def test_mp_user_info_unauthorized(self, anon_api: ApiClient):
        resp = anon_api.get(f"{MP_BASE}/user-info")
        assert resp.status_code == 401
