"""
前端 E2E 测试 — 登录页面
=========================
"""
import pytest
import logging
from playwright.sync_api import Page, expect
from tests.e2e.conftest import FRONTEND_URL

logger = logging.getLogger(__name__)


@pytest.mark.e2e
@pytest.mark.p0
class TestLoginPage:
    """登录页面测试"""

    def test_login_page_loads(self, page: Page):
        """登录页面正常加载"""
        page.goto(f"{FRONTEND_URL}/user/login")
        page.wait_for_load_state("networkidle")

        # 页面有登录表单
        form = page.locator("form, .ant-form, .login-form, [class*='login']")
        expect(form.first).to_be_visible(timeout=10000)

    def test_login_form_elements(self, page: Page):
        """登录表单元素完整"""
        page.goto(f"{FRONTEND_URL}/user/login")
        page.wait_for_load_state("networkidle")

        # 用户名输入框
        username = page.locator("input[id='username'], input[name='username'], input[placeholder*='用户名']")
        expect(username.first).to_be_visible()

        # 密码输入框
        password = page.locator("input[type='password']")
        expect(password.first).to_be_visible()

        # 登录按钮
        submit = page.locator("button[type='submit'], button:has-text('登录')")
        expect(submit.first).to_be_visible()

    def test_login_success(self, page: Page):
        """正常登录 → 跳转到首页"""
        page.goto(f"{FRONTEND_URL}/user/login")
        page.wait_for_load_state("networkidle")

        page.fill("input[id='username'], input[name='username'], input[placeholder*='用户名']", "admin")
        page.fill("input[type='password']", "P@ssw0rd")
        page.click("button[type='submit'], button:has-text('登录')")

        # 等待跳转
        page.wait_for_url("**/welcome**", timeout=15000)
        expect(page).to_have_url(f"{FRONTEND_URL}/welcome")

    def test_login_wrong_password(self, page: Page):
        """错误密码 → 提示错误"""
        page.goto(f"{FRONTEND_URL}/user/login")
        page.wait_for_load_state("networkidle")

        page.fill("input[id='username'], input[name='username'], input[placeholder*='用户名']", "admin")
        page.fill("input[type='password']", "wrong_password")
        page.click("button[type='submit'], button:has-text('登录')")

        page.wait_for_timeout(2000)
        # 应停留在登录页
        assert "/user/login" in page.url or "/login" in page.url

    def test_login_empty_fields(self, page: Page):
        """空表单提交 → 显示验证提示"""
        page.goto(f"{FRONTEND_URL}/user/login")
        page.wait_for_load_state("networkidle")

        page.click("button[type='submit'], button:has-text('登录')")
        page.wait_for_timeout(1000)

        # 应显示验证错误提示
        error = page.locator(".ant-form-item-explain-error, .ant-form-explain, [role='alert']")
        expect(error.first).to_be_visible(timeout=5000)
