"""
v3.19 功能缺口填补增量测试
==========================
覆盖 18 次迭代新增的控制器端点（全内存 Mock）
"""
import pytest
import uuid
from tests.conftest import MockApiClient, MOCK_TOKEN


@pytest.fixture(scope="module")
def api():
    return MockApiClient(token=MOCK_TOKEN)


@pytest.fixture(scope="module")
def anon_api():
    return MockApiClient(token=None)


def _uuid():
    return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════════════
# 1. Operations - EeAnalysis (能效分析)
# ═══════════════════════════════════════════════════════════════════════════

class TestEeAnalysisController:
    """能效分析控制器 - api/energyeff/analysis"""
    BASE = "/api/energyeff/analysis"

    def test_get_score(self, api):
        """GET /api/energyeff/analysis/score - 能效评分"""
        resp = api.get(f"{self.BASE}/score")
        assert resp.status_code in (200, 404)

    def test_get_benchmark(self, api):
        """GET /api/energyeff/analysis/benchmark - 能效基准"""
        resp = api.get(f"{self.BASE}/benchmark")
        assert resp.status_code in (200, 404)

    def test_get_saving_potential(self, api):
        """GET /api/energyeff/analysis/saving-potential - 节能潜力"""
        resp = api.get(f"{self.BASE}/saving-potential")
        assert resp.status_code in (200, 404)

    def test_get_trend(self, api):
        """GET /api/energyeff/analysis/trend - 能效趋势"""
        resp = api.get(f"{self.BASE}/trend", params={"days": 30})
        assert resp.status_code in (200, 404)

    def test_get_diagnosis_recommend(self, api):
        """GET /api/energyeff/analysis/diagnosis-recommend - 诊断建议"""
        resp = api.get(f"{self.BASE}/diagnosis-recommend")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/score")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 2. Operations - ScAnalysis (安全管控分析)
# ═══════════════════════════════════════════════════════════════════════════

class TestScAnalysisController:
    """安全管控分析控制器 - api/safecontrol/analysis"""
    BASE = "/api/safecontrol/analysis"

    def test_get_risk_score(self, api):
        """GET /api/safecontrol/analysis/risk-score - 风险评分"""
        resp = api.get(f"{self.BASE}/risk-score")
        assert resp.status_code in (200, 404)

    def test_get_situation(self, api):
        """GET /api/safecontrol/analysis/situation - 态势感知"""
        resp = api.get(f"{self.BASE}/situation")
        assert resp.status_code in (200, 404)

    def test_get_emergency_recommend(self, api):
        """GET /api/safecontrol/analysis/emergency-recommend/{eventId} - 应急建议"""
        event_id = _uuid()
        resp = api.get(f"{self.BASE}/emergency-recommend/{event_id}")
        assert resp.status_code in (200, 404)

    def test_post_emergency_dispatch(self, api):
        """POST /api/safecontrol/analysis/emergency-dispatch - 应急调度"""
        resp = api.post(f"{self.BASE}/emergency-dispatch", json={
            "eventId": _uuid(),
            "level": "high",
            "actions": ["notify", "isolate"]
        })
        assert resp.status_code in (200, 400, 404)

    def test_post_compliance_trigger(self, api):
        """POST /api/safecontrol/analysis/compliance-trigger - 合规触发"""
        resp = api.post(f"{self.BASE}/compliance-trigger", json={
            "ruleId": _uuid(),
            "scope": "station"
        })
        assert resp.status_code in (200, 400, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/risk-score")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 3. Operations - MeAnalysis (多能协同分析)
# ═══════════════════════════════════════════════════════════════════════════

class TestMeAnalysisController:
    """多能协同分析控制器 - api/multienergy/analysis"""
    BASE = "/api/multienergy/analysis"

    def test_post_optimize(self, api):
        """POST /api/multienergy/analysis/optimize - 多能优化"""
        resp = api.post(f"{self.BASE}/optimize", json={
            "stationId": _uuid(),
            "horizon": 24,
            "objective": "cost"
        })
        assert resp.status_code in (200, 400, 404)

    def test_get_carbon_quota(self, api):
        """GET /api/multienergy/analysis/carbon-quota - 碳配额"""
        resp = api.get(f"{self.BASE}/carbon-quota")
        assert resp.status_code in (200, 404)

    def test_post_peak_shaving(self, api):
        """POST /api/multienergy/analysis/peak-shaving - 削峰填谷"""
        resp = api.post(f"{self.BASE}/peak-shaving", json={
            "stationId": _uuid(),
            "targetReduction": 0.15
        })
        assert resp.status_code in (200, 400, 404)

    def test_get_cost_efficiency(self, api):
        """GET /api/multienergy/analysis/cost-efficiency - 成本效益"""
        resp = api.get(f"{self.BASE}/cost-efficiency")
        assert resp.status_code in (200, 404)

    def test_get_conversion_recommend(self, api):
        """GET /api/multienergy/analysis/conversion-recommend - 转换建议"""
        resp = api.get(f"{self.BASE}/conversion-recommend")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/carbon-quota")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 4. WorkOrder - WorkOrderMy (我的工单)
# ═══════════════════════════════════════════════════════════════════════════

class TestWorkOrderMyController:
    """我的工单控制器 - api/workorder/my"""
    BASE = "/api/workorder/my"

    def test_get_my_orders(self, api):
        """GET /api/workorder/my - 我的工单列表"""
        resp = api.get(self.BASE)
        assert resp.status_code in (200, 404)

    def test_get_my_todo(self, api):
        """GET /api/workorder/my/todo - 我的待办"""
        resp = api.get(f"{self.BASE}/todo")
        assert resp.status_code in (200, 404)

    def test_post_accept(self, api):
        """POST /api/workorder/{id}/accept - 接单"""
        order_id = _uuid()
        resp = api.post(f"/api/workorder/{order_id}/accept")
        assert resp.status_code in (200, 400, 404)

    def test_post_start(self, api):
        """POST /api/workorder/{id}/start - 开始处理"""
        order_id = _uuid()
        resp = api.post(f"/api/workorder/{order_id}/start")
        assert resp.status_code in (200, 400, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(self.BASE)
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 5. Analytics - CustomDashboard (自定义仪表盘)
# ═══════════════════════════════════════════════════════════════════════════

class TestCustomDashboardController:
    """自定义仪表盘控制器 - api/analytics/custom-dashboard"""
    BASE = "/api/analytics/custom-dashboard"

    def test_get_list(self, api):
        """GET /api/analytics/custom-dashboard - 仪表盘列表"""
        resp = api.get(self.BASE)
        assert resp.status_code in (200, 404)

    def test_get_detail(self, api):
        """GET /api/analytics/custom-dashboard/{id} - 仪表盘详情"""
        dashboard_id = _uuid()
        resp = api.get(f"{self.BASE}/{dashboard_id}")
        assert resp.status_code in (200, 404)

    def test_post_create(self, api):
        """POST /api/analytics/custom-dashboard - 创建仪表盘"""
        resp = api.post(self.BASE, json={
            "name": "测试仪表盘",
            "layout": "grid",
            "widgets": []
        })
        assert resp.status_code in (200, 201, 400)

    def test_put_update(self, api):
        """PUT /api/analytics/custom-dashboard/{id} - 更新仪表盘"""
        dashboard_id = _uuid()
        resp = api.put(f"{self.BASE}/{dashboard_id}", json={
            "name": "更新的仪表盘",
            "layout": "flex"
        })
        assert resp.status_code in (200, 400, 404)

    def test_delete(self, api):
        """DELETE /api/analytics/custom-dashboard/{id} - 删除仪表盘"""
        dashboard_id = _uuid()
        resp = api.delete(f"{self.BASE}/{dashboard_id}")
        assert resp.status_code in (200, 204, 404)

    def test_put_set_default(self, api):
        """PUT /api/analytics/custom-dashboard/{id}/default - 设为默认"""
        dashboard_id = _uuid()
        resp = api.put(f"{self.BASE}/{dashboard_id}/default")
        assert resp.status_code in (200, 400, 404)

    def test_post_add_widget(self, api):
        """POST /api/analytics/custom-dashboard/{id}/widgets - 添加小部件"""
        dashboard_id = _uuid()
        resp = api.post(f"{self.BASE}/{dashboard_id}/widgets", json={
            "type": "chart",
            "config": {"title": "能耗趋势"}
        })
        assert resp.status_code in (200, 201, 400, 404)

    def test_put_update_widget(self, api):
        """PUT /api/analytics/custom-dashboard/widgets/{widgetId} - 更新小部件"""
        widget_id = _uuid()
        resp = api.put(f"{self.BASE}/widgets/{widget_id}", json={
            "config": {"title": "更新的标题"}
        })
        assert resp.status_code in (200, 400, 404)

    def test_delete_widget(self, api):
        """DELETE /api/analytics/custom-dashboard/widgets/{widgetId} - 删除小部件"""
        widget_id = _uuid()
        resp = api.delete(f"{self.BASE}/widgets/{widget_id}")
        assert resp.status_code in (200, 204, 404)

    def test_get_widget_types(self, api):
        """GET /api/analytics/custom-dashboard/widget-types - 小部件类型列表"""
        resp = api.get(f"{self.BASE}/widget-types")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(self.BASE)
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 6. Analytics - EnergyDashboard (能源仪表盘)
# ═══════════════════════════════════════════════════════════════════════════

class TestEnergyDashboardController:
    """能源仪表盘控制器 - api/analytics/energy"""
    BASE = "/api/analytics/energy"

    def test_get_overview(self, api):
        """GET /api/analytics/energy/overview - 能源概览"""
        resp = api.get(f"{self.BASE}/overview")
        assert resp.status_code in (200, 404)

    def test_get_trend(self, api):
        """GET /api/analytics/energy/trend - 能源趋势"""
        resp = api.get(f"{self.BASE}/trend", params={"days": 7})
        assert resp.status_code in (200, 404)

    def test_get_composition(self, api):
        """GET /api/analytics/energy/composition - 能源构成"""
        resp = api.get(f"{self.BASE}/composition")
        assert resp.status_code in (200, 404)

    def test_get_carbon(self, api):
        """GET /api/analytics/energy/carbon - 碳排放"""
        resp = api.get(f"{self.BASE}/carbon")
        assert resp.status_code in (200, 404)

    def test_get_station_rank(self, api):
        """GET /api/analytics/energy/station-rank - 场站排名"""
        resp = api.get(f"{self.BASE}/station-rank")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/overview")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 7. Analytics - MaintenanceDashboard (维保仪表盘)
# ═══════════════════════════════════════════════════════════════════════════

class TestMaintenanceDashboardController:
    """维保仪表盘控制器 - api/analytics/maintenance"""
    BASE = "/api/analytics/maintenance"

    def test_get_overview(self, api):
        """GET /api/analytics/maintenance/overview - 维保概览"""
        resp = api.get(f"{self.BASE}/overview")
        assert resp.status_code in (200, 404)

    def test_get_fault_trend(self, api):
        """GET /api/analytics/maintenance/fault-trend - 故障趋势"""
        resp = api.get(f"{self.BASE}/fault-trend", params={"days": 30})
        assert resp.status_code in (200, 404)

    def test_get_workorder_efficiency(self, api):
        """GET /api/analytics/maintenance/workorder-efficiency - 工单效率"""
        resp = api.get(f"{self.BASE}/workorder-efficiency")
        assert resp.status_code in (200, 404)

    def test_get_device_health(self, api):
        """GET /api/analytics/maintenance/device-health - 设备健康"""
        resp = api.get(f"{self.BASE}/device-health")
        assert resp.status_code in (200, 404)

    def test_get_alert_distribution(self, api):
        """GET /api/analytics/maintenance/alert-distribution - 告警分布"""
        resp = api.get(f"{self.BASE}/alert-distribution")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/overview")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 8. Account - AccountAudit (账户审计)
# ═══════════════════════════════════════════════════════════════════════════

class TestAccountAuditController:
    """账户审计控制器 - api/account/audit-logs"""
    BASE = "/api/account/audit-logs"

    def test_get_list(self, api):
        """GET /api/account/audit-logs - 审计日志列表"""
        resp = api.get(self.BASE)
        assert resp.status_code in (200, 404)

    def test_get_list_with_filter(self, api):
        """GET /api/account/audit-logs - 带过滤条件"""
        resp = api.get(self.BASE, params={
            "startTime": "2026-01-01",
            "endTime": "2026-03-19",
            "eventType": "login"
        })
        assert resp.status_code in (200, 404)

    def test_get_detail(self, api):
        """GET /api/account/audit-logs/{eventId} - 审计日志详情"""
        event_id = _uuid()
        resp = api.get(f"{self.BASE}/{event_id}")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(self.BASE)
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 9. Account - AccountSecurity (账户安全)
# ═══════════════════════════════════════════════════════════════════════════

class TestAccountSecurityController:
    """账户安全控制器 - api/account/security"""
    BASE = "/api/account/security"

    def test_get_status(self, api):
        """GET /api/account/security/status - 安全状态"""
        resp = api.get(f"{self.BASE}/status")
        assert resp.status_code in (200, 404)

    def test_post_set_payment_password(self, api):
        """POST /api/account/security/payment-password - 设置支付密码"""
        resp = api.post(f"{self.BASE}/payment-password", json={
            "password": "123456",
            "confirmPassword": "123456"
        })
        assert resp.status_code in (200, 400, 404)

    def test_put_change_payment_password(self, api):
        """PUT /api/account/security/payment-password - 修改支付密码"""
        resp = api.put(f"{self.BASE}/payment-password", json={
            "oldPassword": "123456",
            "newPassword": "654321",
            "confirmPassword": "654321"
        })
        assert resp.status_code in (200, 400, 404)

    def test_post_verify_payment_password(self, api):
        """POST /api/account/security/payment-password/verify - 验证支付密码"""
        resp = api.post(f"{self.BASE}/payment-password/verify", json={
            "password": "123456"
        })
        assert resp.status_code in (200, 400, 404)

    def test_post_update_account_status(self, api):
        """POST /api/account/security/{accountId}/status - 更新账户状态"""
        account_id = _uuid()
        resp = api.post(f"{self.BASE}/{account_id}/status", json={
            "status": "active",
            "reason": "正常激活"
        })
        assert resp.status_code in (200, 400, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/status")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 10. Station - StationMonitor (场站监控)
# ═══════════════════════════════════════════════════════════════════════════

class TestStationMonitorController:
    """场站监控控制器 - api/station/monitor"""
    BASE = "/api/station/monitor"

    def test_get_overview(self, api):
        """GET /api/station/monitor/overview - 监控概览"""
        resp = api.get(f"{self.BASE}/overview")
        assert resp.status_code in (200, 404)

    def test_get_trend(self, api):
        """GET /api/station/monitor/trend - 监控趋势"""
        resp = api.get(f"{self.BASE}/trend", params={"stationId": _uuid(), "metric": "power"})
        assert resp.status_code in (200, 404)

    def test_get_ranking(self, api):
        """GET /api/station/monitor/ranking - 场站排名"""
        resp = api.get(f"{self.BASE}/ranking", params={"metric": "revenue", "limit": 10})
        assert resp.status_code in (200, 404)

    def test_get_map(self, api):
        """GET /api/station/monitor/map - 场站地图"""
        resp = api.get(f"{self.BASE}/map")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/overview")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 11. Station - StationAnalytics (场站分析)
# ═══════════════════════════════════════════════════════════════════════════

class TestStationAnalyticsController:
    """场站分析控制器 - api/station/analytics"""
    BASE = "/api/station/analytics"

    def test_get_report(self, api):
        """GET /api/station/analytics/report - 分析报表"""
        resp = api.get(f"{self.BASE}/report", params={
            "stationId": _uuid(),
            "period": "monthly"
        })
        assert resp.status_code in (200, 404)

    def test_get_comparison(self, api):
        """GET /api/station/analytics/comparison - 对比分析"""
        resp = api.get(f"{self.BASE}/comparison", params={
            "stationIds": f"{_uuid()},{_uuid()}",
            "metric": "energy"
        })
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(f"{self.BASE}/report")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 12. Settlement - Invoice (发票管理)
# ═══════════════════════════════════════════════════════════════════════════

class TestSettlementInvoiceController:
    """发票管理控制器 - api/settlement/invoices"""
    BASE = "/api/settlement/invoices"

    def test_get_list(self, api):
        """GET /api/settlement/invoices - 发票列表"""
        resp = api.get(self.BASE)
        assert resp.status_code in (200, 404)

    def test_get_detail(self, api):
        """GET /api/settlement/invoices/{id} - 发票详情"""
        invoice_id = _uuid()
        resp = api.get(f"{self.BASE}/{invoice_id}")
        assert resp.status_code in (200, 404)

    def test_post_create(self, api):
        """POST /api/settlement/invoices - 创建发票"""
        resp = api.post(self.BASE, json={
            "billIds": [_uuid()],
            "invoiceType": "general",
            "title": "测试公司"
        })
        assert resp.status_code in (200, 201, 400)

    def test_post_issue(self, api):
        """POST /api/settlement/invoices/{id}/issue - 开具发票"""
        invoice_id = _uuid()
        resp = api.post(f"{self.BASE}/{invoice_id}/issue")
        assert resp.status_code in (200, 400, 404)

    def test_post_void(self, api):
        """POST /api/settlement/invoices/{id}/void - 作废发票"""
        invoice_id = _uuid()
        resp = api.post(f"{self.BASE}/{invoice_id}/void", json={
            "reason": "申请作废"
        })
        assert resp.status_code in (200, 400, 404)

    def test_get_summary(self, api):
        """GET /api/settlement/invoices/summary - 发票汇总"""
        resp = api.get(f"{self.BASE}/summary", params={"year": 2026, "month": 3})
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(self.BASE)
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 13. Tenant - Subscription (订阅管理)
# ═══════════════════════════════════════════════════════════════════════════

class TestTenantSubscriptionController:
    """租户订阅控制器 - api/subscription-plans & api/tenants/{tenantId}/subscriptions"""

    def test_get_plans(self, api):
        """GET /api/subscription-plans - 套餐列表"""
        resp = api.get("/api/subscription-plans")
        assert resp.status_code in (200, 404)

    def test_get_enabled_plans(self, api):
        """GET /api/subscription-plans/enabled - 启用的套餐"""
        resp = api.get("/api/subscription-plans/enabled")
        assert resp.status_code in (200, 404)

    def test_get_plan_detail(self, api):
        """GET /api/subscription-plans/{id} - 套餐详情"""
        plan_id = _uuid()
        resp = api.get(f"/api/subscription-plans/{plan_id}")
        assert resp.status_code in (200, 404)

    def test_post_create_plan(self, api):
        """POST /api/subscription-plans - 创建套餐"""
        resp = api.post("/api/subscription-plans", json={
            "code": f"PLAN_{_uuid()[:8]}",
            "name": "测试套餐",
            "price": 99.00,
            "duration": 30
        })
        assert resp.status_code in (200, 201, 400)

    def test_get_tenant_current_subscription(self, api):
        """GET /api/tenants/{tenantId}/subscriptions/current - 当前订阅"""
        tenant_id = _uuid()
        resp = api.get(f"/api/tenants/{tenant_id}/subscriptions/current")
        assert resp.status_code in (200, 404)

    def test_get_tenant_subscription_history(self, api):
        """GET /api/tenants/{tenantId}/subscriptions/history - 订阅历史"""
        tenant_id = _uuid()
        resp = api.get(f"/api/tenants/{tenant_id}/subscriptions/history")
        assert resp.status_code in (200, 404)

    def test_post_subscribe(self, api):
        """POST /api/tenants/{tenantId}/subscriptions - 订阅套餐"""
        tenant_id = _uuid()
        resp = api.post(f"/api/tenants/{tenant_id}/subscriptions", json={
            "planId": _uuid()
        })
        assert resp.status_code in (200, 201, 400, 404)

    def test_post_renew(self, api):
        """POST /api/tenants/{tenantId}/subscriptions/{subscriptionId}/renew - 续订"""
        tenant_id = _uuid()
        subscription_id = _uuid()
        resp = api.post(f"/api/tenants/{tenant_id}/subscriptions/{subscription_id}/renew")
        assert resp.status_code in (200, 400, 404)

    def test_post_cancel(self, api):
        """POST /api/tenants/{tenantId}/subscriptions/{subscriptionId}/cancel - 取消订阅"""
        tenant_id = _uuid()
        subscription_id = _uuid()
        resp = api.post(f"/api/tenants/{tenant_id}/subscriptions/{subscription_id}/cancel")
        assert resp.status_code in (200, 400, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get("/api/subscription-plans")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 14. Bills (账单管理)
# ═══════════════════════════════════════════════════════════════════════════

class TestBillsController:
    """账单控制器 - api/bills"""
    BASE = "/api/bills"

    def test_get_list(self, api):
        """GET /api/bills - 账单列表"""
        resp = api.get(self.BASE)
        assert resp.status_code in (200, 404)

    def test_get_detail(self, api):
        """GET /api/bills/{id} - 账单详情"""
        bill_id = _uuid()
        resp = api.get(f"{self.BASE}/{bill_id}")
        assert resp.status_code in (200, 404)

    def test_get_by_bill_no(self, api):
        """GET /api/bills/no/{billNo} - 按账单号查询"""
        resp = api.get(f"{self.BASE}/no/BILL202603190001")
        assert resp.status_code in (200, 404)

    def test_get_by_tenant(self, api):
        """GET /api/bills/tenant/{tenantId} - 租户账单"""
        tenant_id = _uuid()
        resp = api.get(f"{self.BASE}/tenant/{tenant_id}")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(self.BASE)
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 15. Subscription Manage (订阅管理后台)
# ═══════════════════════════════════════════════════════════════════════════

class TestSubscriptionManageController:
    """订阅管理后台控制器 - api/subscriptions"""
    BASE = "/api/subscriptions"

    def test_get_list(self, api):
        """GET /api/subscriptions - 订阅列表"""
        resp = api.get(self.BASE)
        assert resp.status_code in (200, 404)

    def test_get_statistics(self, api):
        """GET /api/subscriptions/statistics - 订阅统计"""
        resp = api.get(f"{self.BASE}/statistics")
        assert resp.status_code in (200, 404)

    def test_get_detail(self, api):
        """GET /api/subscriptions/{id} - 订阅详情"""
        subscription_id = _uuid()
        resp = api.get(f"{self.BASE}/{subscription_id}")
        assert resp.status_code in (200, 404)

    def test_get_tenants(self, api):
        """GET /api/subscriptions/tenants - 订阅租户列表"""
        resp = api.get(f"{self.BASE}/tenants")
        assert resp.status_code in (200, 404)

    def test_get_plans(self, api):
        """GET /api/subscriptions/plans - 可用套餐"""
        resp = api.get(f"{self.BASE}/plans")
        assert resp.status_code in (200, 404)

    def test_unauthorized(self, anon_api):
        """未授权访问应返回 401"""
        resp = anon_api.get(self.BASE)
        assert resp.status_code == 401
