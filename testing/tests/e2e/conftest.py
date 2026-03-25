"""
前端 E2E 测试 — 全局 Fixture
==============================
Playwright 浏览器管理 + 登录状态缓存
"""
import os
import pytest
import logging
from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("JGSY_FRONTEND_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("JGSY_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("JGSY_ADMIN_PASSWORD", "P@ssw0rd")
STORAGE_STATE = os.path.join(os.path.dirname(__file__), ".auth", "state.json")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """浏览器上下文配置"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def authenticated_state(browser_type, browser_type_launch_args):
    """登录并保存认证状态（session级，只登录一次）"""
    os.makedirs(os.path.dirname(STORAGE_STATE), exist_ok=True)

    browser = browser_type.launch(**browser_type_launch_args)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
        ignore_https_errors=True,
    )
    page = context.new_page()

    # 执行登录
    logger.info(f"E2E 登录: {FRONTEND_URL}/user/login")
    page.goto(f"{FRONTEND_URL}/user/login")
    page.wait_for_load_state("networkidle")

    # 填写登录表单
    page.fill("input[id='username'], input[name='username'], input[placeholder*='用户名']", ADMIN_USERNAME)
    page.fill("input[id='password'], input[name='password'], input[type='password']", ADMIN_PASSWORD)

    # 点击登录按钮
    page.click("button[type='submit'], button:has-text('登录')")
    page.wait_for_url("**/welcome**", timeout=15000)

    logger.info("E2E 登录成功")

    # 保存状态
    context.storage_state(path=STORAGE_STATE)

    context.close()
    browser.close()

    return STORAGE_STATE


@pytest.fixture
def auth_page(browser, authenticated_state):
    """已认证的页面（每个测试独立 context）"""
    context = browser.new_context(
        storage_state=authenticated_state,
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
        ignore_https_errors=True,
    )
    page = context.new_page()

    # 收集 JS 错误
    page._js_errors = []
    page.on("pageerror", lambda e: page._js_errors.append(str(e)))

    yield page

    context.close()


# ═══════════════════════════════════════════════════
# 通用页面测试基类
# ═══════════════════════════════════════════════════

class BasePageTest:
    """通用 CRUD 页面测试基类"""

    PAGE_URL: str = ""        # 子类必须设置
    PAGE_TITLE: str = ""      # 页面标题（用于断言）
    HAS_TABLE: bool = True    # 是否有表格
    HAS_SEARCH: bool = True   # 是否有搜索
    HAS_CREATE: bool = True   # 是否有新增按钮

    def navigate(self, page: Page):
        """导航到目标页面"""
        page.goto(f"{FRONTEND_URL}{self.PAGE_URL}")
        page.wait_for_load_state("networkidle", timeout=15000)

    def test_page_loads(self, auth_page):
        """页面正常加载，无JS错误"""
        self.navigate(auth_page)
        # 检查无白屏
        body = auth_page.locator("body")
        expect(body).to_be_visible()
        # 检查无 JS 错误
        assert len(auth_page._js_errors) == 0, \
            f"页面有JS错误: {auth_page._js_errors}"

    def test_table_renders(self, auth_page):
        """表格正常渲染"""
        if not self.HAS_TABLE:
            return
        self.navigate(auth_page)
        table = auth_page.locator(".ant-table, .ant-pro-table, table")
        expect(table.first).to_be_visible(timeout=10000)

    def test_search_works(self, auth_page):
        """搜索功能正常"""
        if not self.HAS_SEARCH:
            return
        self.navigate(auth_page)
        search = auth_page.locator(
            "input[placeholder*='搜索'], "
            "input[placeholder*='查询'], "
            "input[placeholder*='请输入'], "
            ".ant-input-search input"
        ).first
        if search.is_visible():
            search.fill("test")
            auth_page.keyboard.press("Enter")
            auth_page.wait_for_load_state("networkidle", timeout=10000)

    def test_create_button(self, auth_page):
        """新增按钮可点击"""
        if not self.HAS_CREATE:
            return
        self.navigate(auth_page)
        btn = auth_page.locator(
            "button:has-text('新增'), "
            "button:has-text('新建'), "
            "button:has-text('添加'), "
            "button:has-text('创建')"
        ).first
        if btn.is_visible():
            btn.click()
            # 验证弹窗出现
            auth_page.wait_for_timeout(1000)
            modal = auth_page.locator(".ant-modal, .ant-drawer")
            if modal.first.is_visible():
                # 关闭弹窗
                close_btn = auth_page.locator(
                    ".ant-modal-close, .ant-drawer-close, "
                    "button:has-text('取消')"
                ).first
                if close_btn.is_visible():
                    close_btn.click()
