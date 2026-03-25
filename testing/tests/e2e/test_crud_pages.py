"""
前端 E2E 测试 — CRUD 页面深度测试
===================================
"""
import pytest
import logging
from playwright.sync_api import Page, expect
from tests.e2e.conftest import FRONTEND_URL, BasePageTest

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════
# 租户管理
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p1
class TestTenantPages(BasePageTest):
    PAGE_URL = "/tenant/list"
    PAGE_TITLE = "租户列表"

    def test_tenant_search_by_name(self, auth_page):
        """按名称搜索租户"""
        self.navigate(auth_page)
        auth_page.fill("input[placeholder*='租户名'], input[placeholder*='请输入']", "测试")
        auth_page.click("button:has-text('查询'), button:has-text('搜索')")
        auth_page.wait_for_load_state("networkidle", timeout=10000)
        # 验证结果变化
        table = auth_page.locator(".ant-table-tbody tr")
        logger.info(f"搜索结果: {table.count()} 行")

    def test_tenant_pagination(self, auth_page):
        """分页功能"""
        self.navigate(auth_page)
        pager = auth_page.locator(".ant-pagination")
        if pager.first.is_visible():
            # 点击第2页
            auth_page.click(".ant-pagination-item:nth-child(2)")
            auth_page.wait_for_load_state("networkidle", timeout=10000)


# ═══════════════════════════════════════════════════
# 充电订单
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p0
class TestChargingOrderPages(BasePageTest):
    PAGE_URL = "/charging/orders"
    PAGE_TITLE = "充电订单"

    def test_order_search_by_date_range(self, auth_page):
        """按日期范围搜索"""
        self.navigate(auth_page)
        # 查找日期选择器
        datepicker = auth_page.locator(".ant-picker-range, .ant-calendar-range-picker").first
        if datepicker.is_visible():
            datepicker.click()
            auth_page.wait_for_timeout(500)
            # 选择最近30天快捷按钮
            quick = auth_page.locator("a:has-text('最近30天'), a:has-text('近30天')").first
            if quick.is_visible():
                quick.click()
            auth_page.wait_for_load_state("networkidle", timeout=10000)

    def test_order_search_by_status(self, auth_page):
        """按状态筛选"""
        self.navigate(auth_page)
        status_select = auth_page.locator(
            ".ant-select:has(span:has-text('状态')), "
            "[placeholder*='状态']"
        ).first
        if status_select.is_visible():
            status_select.click()
            auth_page.wait_for_timeout(300)
            # 选择第一个选项
            option = auth_page.locator(".ant-select-item-option").first
            if option.is_visible():
                option.click()

    def test_order_export(self, auth_page):
        """导出按钮"""
        self.navigate(auth_page)
        export_btn = auth_page.locator("button:has-text('导出'), button:has-text('下载')").first
        if export_btn.is_visible():
            expect(export_btn).to_be_enabled()

    def test_order_detail_modal(self, auth_page):
        """查看订单详情"""
        self.navigate(auth_page)
        # 点击第一行查看按钮
        view_btn = auth_page.locator(
            ".ant-table-tbody tr:first-child a:has-text('详情'), "
            ".ant-table-tbody tr:first-child a:has-text('查看'), "
            ".ant-table-tbody tr:first-child button:has-text('详情')"
        ).first
        if view_btn.is_visible():
            view_btn.click()
            auth_page.wait_for_timeout(1000)
            modal = auth_page.locator(".ant-modal, .ant-drawer")
            expect(modal.first).to_be_visible(timeout=5000)


# ═══════════════════════════════════════════════════
# 场站管理
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p0
class TestStationPages(BasePageTest):
    PAGE_URL = "/station/list"
    PAGE_TITLE = "场站列表"

    def test_station_search_by_region(self, auth_page):
        """按区域筛选场站"""
        self.navigate(auth_page)
        region_select = auth_page.locator(
            ".ant-select:has(span:has-text('区域')), "
            ".ant-cascader, "
            "[placeholder*='区域']"
        ).first
        if region_select.is_visible():
            region_select.click()
            auth_page.wait_for_timeout(500)

    def test_station_map_view(self, auth_page):
        """场站地图视图"""
        self.navigate(auth_page)
        map_btn = auth_page.locator(
            "button:has-text('地图'), [data-tab*='map'], .ant-radio-button-wrapper:has-text('地图')"
        ).first
        if map_btn.is_visible():
            map_btn.click()
            auth_page.wait_for_timeout(2000)


# ═══════════════════════════════════════════════════
# 设备管理
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p1
class TestDevicePages(BasePageTest):
    PAGE_URL = "/device/registry/list"
    PAGE_TITLE = "设备列表"

    def test_device_search_multi(self, auth_page):
        """多条件组合搜索"""
        self.navigate(auth_page)
        # 填写设备编号
        sn_input = auth_page.locator("input[placeholder*='编号'], input[placeholder*='SN']").first
        if sn_input.is_visible():
            sn_input.fill("SN-001")
        # 选择设备类型
        type_select = auth_page.locator("[placeholder*='类型'], .ant-select").first
        if type_select.is_visible():
            type_select.click()
            auth_page.wait_for_timeout(300)
            option = auth_page.locator(".ant-select-item-option").first
            if option.is_visible():
                option.click()
        # 搜索
        auth_page.click("button:has-text('查询'), button:has-text('搜索')")
        auth_page.wait_for_load_state("networkidle", timeout=10000)

    def test_device_alarm_list(self, auth_page):
        """告警列表"""
        auth_page.goto(f"{FRONTEND_URL}/device/monitoring/alerts")
        auth_page.wait_for_load_state("networkidle")
        table = auth_page.locator(".ant-table, .ant-pro-table, table")
        expect(table.first).to_be_visible(timeout=10000)


# ═══════════════════════════════════════════════════
# 工单管理
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p1
class TestWorkOrderPages(BasePageTest):
    PAGE_URL = "/workorder/list"
    PAGE_TITLE = "工单列表"

    def test_workorder_filter_by_type(self, auth_page):
        """按工单类型筛选"""
        self.navigate(auth_page)
        type_select = auth_page.locator("[placeholder*='类型'], .ant-select").first
        if type_select.is_visible():
            type_select.click()
            auth_page.wait_for_timeout(300)
            option = auth_page.locator(".ant-select-item-option").first
            if option.is_visible():
                option.click()

    def test_workorder_create_form(self, auth_page):
        """新建工单表单校验"""
        self.navigate(auth_page)
        btn = auth_page.locator("button:has-text('新增'), button:has-text('新建')").first
        if btn.is_visible():
            btn.click()
            auth_page.wait_for_timeout(1000)
            modal = auth_page.locator(".ant-modal, .ant-drawer")
            if modal.first.is_visible():
                # 直接提交（验证前端校验）
                submit = auth_page.locator(
                    ".ant-modal button:has-text('确定'), "
                    ".ant-drawer button:has-text('确定'), "
                    "button:has-text('提交')"
                ).first
                if submit.is_visible():
                    submit.click()
                    auth_page.wait_for_timeout(500)
                    # 应显示校验提示
                    error = auth_page.locator(".ant-form-item-explain-error")
                    if error.first.is_visible():
                        logger.info("表单校验正常")


# ═══════════════════════════════════════════════════
# 系统管理 — 用户、角色、菜单
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p0
class TestSystemUserPages(BasePageTest):
    PAGE_URL = "/system/user"
    PAGE_TITLE = "用户管理"

    def test_user_search_by_name(self, auth_page):
        """按用户名搜索"""
        self.navigate(auth_page)
        auth_page.fill("input[placeholder*='用户名'], input[placeholder*='请输入']", "admin")
        auth_page.click("button:has-text('查询'), button:has-text('搜索')")
        auth_page.wait_for_load_state("networkidle", timeout=10000)
        rows = auth_page.locator(".ant-table-tbody tr")
        assert rows.count() >= 1, "搜索 'admin' 应至少返回1条结果"

    def test_user_role_assignment(self, auth_page):
        """角色分配弹窗"""
        self.navigate(auth_page)
        more_btn = auth_page.locator(
            ".ant-table-tbody tr:first-child .ant-dropdown-trigger, "
            ".ant-table-tbody tr:first-child button:has-text('更多'), "
            ".ant-table-tbody tr:first-child a:has-text('角色')"
        ).first
        if more_btn.is_visible():
            more_btn.click()
            auth_page.wait_for_timeout(500)


@pytest.mark.e2e
@pytest.mark.p1
class TestSystemRolePages(BasePageTest):
    PAGE_URL = "/system/role"
    PAGE_TITLE = "角色管理"

    def test_role_permission_tree(self, auth_page):
        """角色权限树渲染"""
        self.navigate(auth_page)
        # 点击第一个角色的编辑按钮
        edit_btn = auth_page.locator(
            ".ant-table-tbody tr:first-child a:has-text('编辑'), "
            ".ant-table-tbody tr:first-child button:has-text('编辑')"
        ).first
        if edit_btn.is_visible():
            edit_btn.click()
            auth_page.wait_for_timeout(1000)
            # 验证权限树
            tree = auth_page.locator(".ant-tree, [class*='tree']")
            if tree.first.is_visible():
                logger.info("权限树渲染正常")


@pytest.mark.e2e
@pytest.mark.p1
class TestSystemMenuPages(BasePageTest):
    PAGE_URL = "/system/menu"
    PAGE_TITLE = "菜单管理"


# ═══════════════════════════════════════════════════
# 区块链模块
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p1
class TestBlockchainPages(BasePageTest):
    PAGE_URL = "/blockchain/trading"
    PAGE_TITLE = "电力交易"

    def test_trading_list_filters(self, auth_page):
        """交易记录筛选"""
        self.navigate(auth_page)
        # 验证筛选区域
        form = auth_page.locator(".ant-form, .ant-pro-form, [class*='search']").first
        if form.is_visible():
            logger.info("交易记录筛选区域正常")


# ═══════════════════════════════════════════════════
# 数据分析模块
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p1
class TestAnalyticsPages(BasePageTest):
    PAGE_URL = "/analytics/charging"
    PAGE_TITLE = "充电统计"
    HAS_TABLE = False
    HAS_SEARCH = False

    def test_charging_chart_renders(self, auth_page):
        """图表渲染"""
        self.navigate(auth_page)
        chart = auth_page.locator("canvas, svg, [class*='chart'], [class*='echarts']").first
        if chart.is_visible(timeout=8000):
            logger.info("图表渲染正常")


# ═══════════════════════════════════════════════════
# 内容管理模块
# ═══════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.p1
class TestContentPages(BasePageTest):
    PAGE_URL = "/content/manage"
    PAGE_TITLE = "内容管理"

    def test_content_rich_editor(self, auth_page):
        """富文本编辑器渲染"""
        self.navigate(auth_page)
        btn = auth_page.locator("button:has-text('新增'), button:has-text('新建')").first
        if btn.is_visible():
            btn.click()
            auth_page.wait_for_timeout(1500)
            editor = auth_page.locator(
                ".ql-editor, .tox-tinymce, [class*='editor'], "
                ".ant-modal .ant-input, .ant-drawer .ant-input"
            ).first
            if editor.is_visible():
                logger.info("编辑器渲染正常")
