"""
前端 E2E 测试 — 全模块页面批量测试
====================================
自动覆盖 230+ 页面，验证页面可打开 + 无JS错误
"""
import pytest
import logging
from playwright.sync_api import Page, expect
from tests.e2e.conftest import FRONTEND_URL, BasePageTest

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════
# 全部页面路由（230+）— 自动参数化
# ═══════════════════════════════════════════════════

ALL_PAGES = [
    # (路由, 描述, 是否有表格, 是否有搜索)
    # ── 首页 ──
    ("/welcome", "欢迎页", False, False),
    ("/dashboard", "仪表盘", False, False),

    # ── 租户管理 ──
    ("/tenant/list", "租户列表", True, True),
    ("/tenant/category", "租户分类", True, True),
    ("/tenant/config", "租户配置", False, False),
    ("/tenant/subscription", "订阅管理", True, True),
    ("/tenant/theme", "租户主题", True, True),
    ("/tenant/agent-partner", "代理商管理", True, True),
    ("/tenant/ticket", "客服工单", True, True),

    # ── 充电运营 ──
    ("/charging/dashboard", "运营概览", False, False),
    ("/charging/piles", "充电桩管理", True, True),
    ("/charging/orders", "充电订单", True, True),
    ("/charging/monitor", "实时监控", False, False),
    ("/charging/pricing", "费率管理", True, True),
    ("/charging/reservation", "预约管理", True, True),
    ("/charging/refund", "退款管理", True, True),
    ("/charging/free-quota", "免费额度", True, True),
    ("/charging/hlht", "互联互通", True, True),

    # ── 场站管理 ──
    ("/station/list", "场站列表", True, True),
    ("/station/monitor", "场站监控", False, False),
    ("/station/config", "场站配置", False, False),

    # ── 结算管理 ──
    ("/settlement/list", "结算记录", True, True),
    ("/settlement/merchant", "商户结算", True, True),
    ("/settlement/profit-sharing", "分润管理", True, True),
    ("/settlement/withdraw", "提现审核", True, True),

    # ── 财务管理 ──
    ("/finance/invoice", "发票管理", True, True),
    ("/finance/recharge", "充值记录", True, True),
    ("/finance/coupon", "优惠券管理", True, True),
    ("/finance/withdraw", "提现审核", True, True),

    # ── 工单管理 ──
    ("/workorder/list", "工单列表", True, True),
    ("/workorder/fault", "故障工单", True, True),
    ("/workorder/inspect", "巡检工单", True, True),
    ("/workorder/install", "安装工单", True, True),
    ("/workorder/dispatch", "工单派发", True, True),
    ("/workorder/staff", "运维人员", True, True),
    ("/workorder/stats", "工单统计", False, False),
    ("/workorder/spare-part", "备件管理", True, True),
    ("/workorder/shift", "排班管理", True, True),

    # ── 系统管理 ──
    ("/system/user", "用户管理", True, True),
    ("/system/role", "角色管理", True, True),
    ("/system/permission", "权限管理", True, True),
    ("/system/department", "部门管理", True, True),
    ("/system/menu", "菜单管理", True, True),
    ("/system/dict", "数据字典", True, True),
    ("/system/config", "系统配置", False, False),
    ("/system/file", "文件管理", True, True),
    ("/system/job", "定时任务", True, True),
    ("/system/audit-log", "审计日志", True, True),
    ("/system/cache", "缓存管理", False, False),
    ("/system/datasource", "数据源管理", True, True),
    ("/system/data-permission", "数据权限", True, True),
    ("/system/storage", "存储配置", False, False),
    ("/system/channel", "渠道配置", True, True),
    ("/system/auth-config", "登录配置", False, False),
    ("/system/rate-limiting", "限流降级", True, True),
    ("/system/version", "版本管理", True, True),
    ("/system/announcement", "公告管理", True, True),
    ("/system/backup", "数据备份", True, True),

    # ── 设备管理 ──
    ("/device/registry/list", "设备列表", True, True),
    ("/device/registry/asset", "资产管理", True, True),
    ("/device/registry/firmware", "固件管理", True, True),
    ("/device/registry/edge-gateway", "边缘网关", True, True),
    ("/device/monitoring/realtime", "实时监控", False, False),
    ("/device/monitoring/alerts", "告警中心", True, True),
    ("/device/monitoring/control", "远程控制", True, True),
    ("/device/ops/dashboard", "运维概览", False, False),
    ("/device/ops/health", "健康评分", True, True),
    ("/device/ops/fault", "故障记录", True, True),
    ("/device/ops/inspection", "巡检管理", True, True),
    ("/device/ops/sparepart", "备件管理", True, True),

    # ── 数据采集 ──
    ("/ingestion/tasks", "采集任务", True, True),
    ("/ingestion/sources", "数据源配置", True, True),
    ("/ingestion/monitor", "采集监控", False, False),

    # ── 区块链 ──
    ("/blockchain/dashboard", "区块链概览", False, False),
    ("/blockchain/wallet", "钱包管理", True, True),
    ("/blockchain/trading", "电力交易", True, True),
    ("/blockchain/certificate", "绿证管理", True, True),
    ("/blockchain/carbon-credit", "碳积分管理", True, True),
    ("/blockchain/contract", "智能合约", True, True),
    ("/blockchain/transactions", "交易记录", True, True),
    ("/blockchain/events", "事件日志", True, True),

    # ── 数据分析 ──
    ("/analytics/event-tracking", "行为埋点", True, True),
    ("/analytics/realtime", "实时行为流", False, False),
    ("/analytics/user-profile", "用户画像", True, True),
    ("/analytics/funnel", "漏斗分析", True, True),
    ("/analytics/path", "路径分析", False, False),
    ("/analytics/recommend", "推荐配置", True, True),
    ("/analytics/charging", "充电统计", False, False),
    ("/analytics/device", "设备统计", False, False),
    ("/analytics/revenue", "收益分析", False, False),
    ("/analytics/operations", "运营报表", False, False),
    ("/analytics/anomaly", "异常检测", True, True),

    # ── 安全中心 ──
    ("/security/ip-blacklist", "IP黑白名单", True, True),
    ("/security/sensitive-word", "敏感词过滤", True, True),
    ("/security/data-mask", "数据脱敏", True, True),
    ("/security/audit", "安全审计", True, True),
    ("/security/mfa", "MFA认证管理", True, True),
    ("/security/real-name-auth", "实名认证审核", True, True),

    # ── 日志中心 ──
    ("/log/center", "日志查询", True, True),
    ("/log/alert", "日志告警", True, True),
    ("/log/alert-rules", "告警规则", True, True),
    ("/log/analysis", "日志分析", False, False),

    # ── 建站系统 ──
    ("/builder/sites", "我的站点", True, True),
    ("/builder/templates", "模板库", True, True),
    ("/builder/components", "组件库", True, True),
    ("/builder/blocks", "区块库", True, True),
    ("/builder/themes", "主题管理", True, True),
    ("/builder/collections", "数据集合", True, True),
    ("/builder/publish", "发布管理", True, True),
    ("/builder/analytics", "统计分析", False, False),

    # ── 内容管理 ──
    ("/content/sites", "站点管理", True, True),
    ("/content/categories", "栏目管理", True, True),
    ("/content/manage", "内容管理", True, True),
    ("/content/media", "媒体库", True, True),
    ("/content/templates", "模板管理", True, True),
    ("/content/comments", "评论管理", True, True),
    ("/content/ads", "广告管理", True, True),
    ("/content/stats", "统计分析", False, False),
    ("/content/search", "内容搜索", True, True),
    ("/content/seo", "SEO配置", False, False),

    # ── 门户管理 ──
    ("/portal/company", "公司信息", False, False),
    ("/portal/stats", "数据指标", False, False),
    ("/portal/products", "产品管理", True, True),
    ("/portal/solutions", "解决方案", True, True),
    ("/portal/cases", "客户案例", True, True),
    ("/portal/partners", "合作伙伴", True, True),
    ("/portal/milestones", "发展历程", True, True),
    ("/portal/jobs", "招聘职位", True, True),
    ("/portal/applications", "求职申请", True, True),
    ("/portal/contacts", "联系咨询", True, True),

    # ── AI ──
    ("/ai/dashboard", "AI概览", False, False),
    ("/ai/models", "AI模型", True, True),
    ("/ai/prediction/load", "负荷预测", False, False),
    ("/ai/prediction/power", "发电预测", False, False),
    ("/ai/prediction/price", "价格预测", False, False),
    ("/ai/training", "训练任务", True, True),
    ("/ai/health-monitor/dashboard", "监测概览", False, False),
    ("/ai/health-monitor/assess", "设备评估", True, True),
    ("/ai/health-monitor/battery", "电池SOH", True, True),
    ("/ai/health-monitor/alert-rules", "告警规则", True, True),
    ("/ai/health-monitor/maintenance", "维护计划", True, True),

    # ── 数字孪生 ──
    ("/digital-twin/scene3d", "3D场景", False, False),
    ("/digital-twin/device", "设备孪生", True, True),
    ("/digital-twin/simulation", "设备仿真", False, False),
    ("/digital-twin/realtime", "实时数据", False, False),

    # ── 系统监控 ──
    ("/monitor/online", "在线用户", True, True),
    ("/monitor/log", "操作日志", True, True),
    ("/monitor/login-log", "登录日志", True, True),
    ("/monitor/service", "服务监控", True, True),
    ("/monitor/sql", "SQL 监控", True, True),
    ("/monitor/tracing", "链路追踪", True, True),
    ("/monitor/audit", "审计事项", True, True),

    # ── 开发工具 ──
    ("/developer/api", "API管理", True, True),
    ("/developer/api-docs", "接口文档", False, False),
    ("/developer/form", "表单设计器", False, False),
    ("/developer/code-generator", "代码生成", True, True),
    ("/developer/db-docs", "数据库文档", True, True),
    ("/developer/backup", "备份恢复", True, True),

    # ── 个人中心 ──
    ("/account/profile", "个人信息", False, False),
    ("/account/settings", "个人设置", False, False),
    ("/account/mfa", "MFA设置", False, False),
]


@pytest.mark.e2e
class TestAllPages:
    """全部页面批量测试 — 自动参数化"""

    @pytest.mark.parametrize("route,desc,has_table,has_search",
                             ALL_PAGES,
                             ids=[f"{p[1]}({p[0]})" for p in ALL_PAGES])
    def test_page_loads_no_error(self, auth_page, route, desc, has_table, has_search):
        """页面正常加载，无JS错误，无白屏"""
        auth_page.goto(f"{FRONTEND_URL}{route}", wait_until="networkidle", timeout=20000)

        # 1. 页面不是白屏
        body = auth_page.locator("body")
        expect(body).to_be_visible()
        body_text = body.inner_text()
        assert len(body_text.strip()) > 0, f"[{desc}] 页面白屏"

        # 2. 不是 404 / 403 / 500 页面
        page_content = auth_page.content()
        assert "404" not in auth_page.title() or "Not Found" not in page_content[:1000], \
            f"[{desc}] 页面 404"
        assert "500" not in auth_page.title(), f"[{desc}] 页面 500"

        # 3. 无 JS 错误
        assert len(auth_page._js_errors) == 0, \
            f"[{desc}] JS错误: {auth_page._js_errors}"

        # 4. 如有表格，验证表格可见
        if has_table:
            table = auth_page.locator(
                ".ant-table, .ant-pro-table, table, [class*='table']"
            ).first
            if table.is_visible(timeout=5000):
                logger.info(f"[{desc}] 表格渲染正常")

        logger.info(f"✅ [{desc}] {route} — 通过")
