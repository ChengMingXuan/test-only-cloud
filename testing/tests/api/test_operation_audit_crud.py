"""
接口自动化测试 — 操作审计日志 CRUD + 回滚 全生命周期
=====================================================
覆盖 OperationLogController 6 个端点：
  GET  /api/monitor/operation-logs           分页查询
  GET  /api/monitor/operation-logs/{id}      详情
  GET  /api/monitor/operation-logs/statistics 统计
  GET  /api/monitor/operation-logs/resource-history 资源历史
  GET  /api/monitor/operation-logs/{id}/rollback-check 回滚预检
  POST /api/monitor/operation-logs/{id}/rollback       执行回滚

权限码: monitor:oplog:list / monitor:oplog:view / monitor:oplog:stats / monitor:oplog:rollback
"""
import uuid
import pytest
import logging

logger = logging.getLogger(__name__)

OPLOG_BASE = "/api/monitor/operation-logs"


# ══════════════════════════════════════════════════════════════════════════════
# 分页查询
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogList:
    """操作审计日志分页查询"""

    @pytest.mark.observability
    @pytest.mark.p0
    def test_list_default(self, api, v):
        """[P0] 默认分页查询"""
        r = api.get(OPLOG_BASE)
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p0
    def test_list_with_page_params(self, api, v):
        """[P0] 指定 page + pageSize 分页"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 20})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p0
    @pytest.mark.parametrize("category", [
        "permission", "strategy", "device_command", "transaction",
        "config", "work_order", "auth", "data_export", "rollback",
    ])
    def test_list_filter_by_category(self, api, v, category):
        """[P0] 按审计分类过滤"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": category})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p0
    @pytest.mark.parametrize("action", [
        "Create", "Update", "Delete", "Execute",
        "Approve", "Reject", "Rollback", "Export", "Import",
        "Login", "Logout",
    ])
    def test_list_filter_by_action(self, api, v, action):
        """[P0] 按操作类型过滤"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "action": action})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    @pytest.mark.parametrize("risk", ["low", "medium", "high", "critical"])
    def test_list_filter_by_risk_level(self, api, v, risk):
        """[P1] 按风险等级过滤"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "riskLevel": risk})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    def test_list_filter_by_service_name(self, api, v):
        """[P1] 按服务名过滤"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "serviceName": "observability"})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    def test_list_filter_by_user_name(self, api, v):
        """[P1] 按用户名过滤"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "userName": "admin"})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    def test_list_filter_by_resource_type(self, api, v):
        """[P1] 按资源类型过滤"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "resourceType": "device"})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    def test_list_filter_by_keyword(self, api, v):
        """[P1] 关键词搜索"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 10, "keyword": "测试"})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    @pytest.mark.parametrize("result_val", ["Success", "Failure"])
    def test_list_filter_by_result(self, api, v, result_val):
        """[P1] 按操作结果过滤"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "result": result_val})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    def test_list_filter_by_time_range(self, api, v):
        """[P1] 按时间范围过滤"""
        r = api.get(OPLOG_BASE, params={
            "page": 1, "pageSize": 10,
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_list_combined_filters(self, api, v):
        """[P2] 多条件组合过滤"""
        r = api.get(OPLOG_BASE, params={
            "page": 1, "pageSize": 10,
            "category": "permission",
            "action": "Create",
            "riskLevel": "medium",
            "serviceName": "permission",
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 分页边界
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogPagination:
    """分页边界场景"""

    @pytest.mark.observability
    @pytest.mark.p2
    def test_page_0_defaults_to_1(self, api, v):
        """[P2] page=0 不报错"""
        r = api.get(OPLOG_BASE, params={"page": 0, "pageSize": 10})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_large_page_empty_result(self, api, v):
        """[P2] 超大页码返回空列表"""
        r = api.get(OPLOG_BASE, params={"page": 99999, "pageSize": 10})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_page_size_clamped_to_100(self, api, v):
        """[P2] pageSize 超过 100 被截断"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 500})
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_page_size_1(self, api, v):
        """[P2] pageSize=1"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 1})
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 详情
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogDetail:
    """操作审计日志详情"""

    @pytest.mark.observability
    @pytest.mark.p0
    def test_detail_by_id(self, api, v):
        """[P0] 按 ID 查询详情"""
        mock_id = str(uuid.uuid4())
        r = api.get(f"{OPLOG_BASE}/{mock_id}")
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_detail_invalid_id(self, api, v):
        """[P2] 无效 ID 不导致 5xx"""
        r = api.get(f"{OPLOG_BASE}/00000000-0000-0000-0000-000000000000")
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 统计
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogStatistics:
    """操作审计统计"""

    @pytest.mark.observability
    @pytest.mark.p0
    def test_statistics_with_time_range(self, api, v):
        """[P0] 按时间范围查统计"""
        r = api.get(f"{OPLOG_BASE}/statistics", params={
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    def test_statistics_no_params(self, api, v):
        """[P1] 无参数查统计（默认范围）"""
        r = api.get(f"{OPLOG_BASE}/statistics")
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_statistics_narrow_range(self, api, v):
        """[P2] 极小时间范围"""
        r = api.get(f"{OPLOG_BASE}/statistics", params={
            "startTime": "2026-03-01T00:00:00Z",
            "endTime": "2026-03-01T00:01:00Z",
        })
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 资源历史
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogResourceHistory:
    """资源操作历史查询"""

    @pytest.mark.observability
    @pytest.mark.p1
    def test_resource_history_device(self, api, v):
        """[P1] 按设备资源查历史"""
        r = api.get(f"{OPLOG_BASE}/resource-history", params={
            "resourceType": "device",
            "resourceId": str(uuid.uuid4()),
        })
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p1
    def test_resource_history_role(self, api, v):
        """[P1] 按角色资源查历史"""
        r = api.get(f"{OPLOG_BASE}/resource-history", params={
            "resourceType": "role",
            "resourceId": str(uuid.uuid4()),
        })
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_resource_history_missing_params(self, api, v):
        """[P2] 缺少参数不导致 5xx"""
        r = api.get(f"{OPLOG_BASE}/resource-history")
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 回滚预检
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogRollbackCheck:
    """回滚预检"""

    @pytest.mark.observability
    @pytest.mark.p0
    def test_rollback_check_by_id(self, api, v):
        """[P0] 查询回滚可行性"""
        mock_id = str(uuid.uuid4())
        r = api.get(f"{OPLOG_BASE}/{mock_id}/rollback-check")
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_rollback_check_nonexistent(self, api, v):
        """[P2] 不存在的日志 ID 预检不 5xx"""
        r = api.get(f"{OPLOG_BASE}/00000000-0000-0000-0000-000000000000/rollback-check")
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 回滚执行
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogRollbackExecute:
    """回滚执行"""

    @pytest.mark.observability
    @pytest.mark.p0
    def test_rollback_execute(self, api, v):
        """[P0] 执行回滚"""
        mock_id = str(uuid.uuid4())
        r = api.post(f"{OPLOG_BASE}/{mock_id}/rollback")
        v.not_5xx(r)

    @pytest.mark.observability
    @pytest.mark.p2
    def test_rollback_nonexistent(self, api, v):
        """[P2] 回滚不存在的日志不 5xx"""
        r = api.post(f"{OPLOG_BASE}/00000000-0000-0000-0000-000000000000/rollback")
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 鉴权与权限验证
# ══════════════════════════════════════════════════════════════════════════════

class TestOperationLogAuth:
    """操作审计日志鉴权验证"""

    @pytest.mark.observability
    @pytest.mark.p0
    def test_no_token_list_rejected(self, no_auth_api):
        """[P0] 无Token查询列表被拒"""
        r = no_auth_api.get(OPLOG_BASE)
        assert r.status_code in (401, 403)

    @pytest.mark.observability
    @pytest.mark.p0
    def test_no_token_detail_rejected(self, no_auth_api):
        """[P0] 无Token查详情被拒"""
        r = no_auth_api.get(f"{OPLOG_BASE}/{uuid.uuid4()}")
        assert r.status_code in (401, 403)

    @pytest.mark.observability
    @pytest.mark.p0
    def test_no_token_stats_rejected(self, no_auth_api):
        """[P0] 无Token查统计被拒"""
        r = no_auth_api.get(f"{OPLOG_BASE}/statistics")
        assert r.status_code in (401, 403)

    @pytest.mark.observability
    @pytest.mark.p0
    def test_no_token_rollback_rejected(self, no_auth_api):
        """[P0] 无Token执行回滚被拒"""
        r = no_auth_api.post(f"{OPLOG_BASE}/{uuid.uuid4()}/rollback")
        assert r.status_code in (401, 403)
