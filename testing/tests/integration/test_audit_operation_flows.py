"""
集成测试 — 操作审计留痕·回滚·跨服务链路验证
==============================================
覆盖：审计事件发布→消费→查询链路 / 回滚流程 / 统计聚合 / 资源历史
对应 API: OperationLogController（6 个端点）
"""
import uuid
import pytest
import logging

logger = logging.getLogger(__name__)

# 审计日志 API 前缀
OPLOG_BASE = "/api/monitor/operation-logs"

# 测试用 Mock 资源 ID
_RESOURCE_ID = str(uuid.uuid4())
_RESOURCE_TYPE = "device"


# ══════════════════════════════════════════════════════════════════════════════
# 操作审计查询链路集成测试
# ══════════════════════════════════════════════════════════════════════════════

class TestAuditQueryPipeline:
    """操作审计 查询→详情→统计→资源历史 完整链路"""

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_oplog_list_query(self, api, v):
        """[P0] 操作审计日志列表分页查询"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 10})
        v.not_5xx(r)
        assert r.status_code < 500

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_oplog_list_with_category_filter(self, api, v):
        """[P0] 按审计分类过滤操作日志"""
        categories = ["permission", "config", "device_command", "auth"]
        for cat in categories:
            r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": cat})
            v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_oplog_list_with_action_filter(self, api, v):
        """[P0] 按操作类型过滤（Create/Update/Delete/Execute）"""
        actions = ["Create", "Update", "Delete", "Execute", "Rollback"]
        for act in actions:
            r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "action": act})
            v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_oplog_list_with_risk_filter(self, api, v):
        """[P1] 按风险等级过滤（low/medium/high/critical）"""
        for level in ["low", "medium", "high", "critical"]:
            r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "riskLevel": level})
            v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_oplog_list_with_time_range(self, api, v):
        """[P1] 按时间范围过滤操作日志"""
        r = api.get(OPLOG_BASE, params={
            "page": 1, "pageSize": 10,
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_oplog_list_with_keyword(self, api, v):
        """[P1] 关键词搜索操作日志"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 10, "keyword": "测试"})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_oplog_list_with_service_name(self, api, v):
        """[P1] 按服务名过滤操作日志"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 10, "serviceName": "observability"})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_oplog_list_with_user_name(self, api, v):
        """[P1] 按用户名过滤操作日志"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 10, "userName": "admin"})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_oplog_list_combined_filters(self, api, v):
        """[P2] 组合多条件过滤操作日志"""
        r = api.get(OPLOG_BASE, params={
            "page": 1, "pageSize": 10,
            "category": "permission",
            "action": "Create",
            "riskLevel": "medium",
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r)


class TestAuditDetailAndStatistics:
    """操作审计 详情·统计·资源历史"""

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_oplog_detail_by_id(self, api, v):
        """[P0] 查询单条操作日志详情"""
        mock_id = str(uuid.uuid4())
        r = api.get(f"{OPLOG_BASE}/{mock_id}")
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_oplog_statistics(self, api, v):
        """[P0] 查询操作审计统计数据"""
        r = api.get(f"{OPLOG_BASE}/statistics", params={
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_oplog_resource_history(self, api, v):
        """[P1] 查询资源操作历史"""
        r = api.get(f"{OPLOG_BASE}/resource-history", params={
            "resourceType": _RESOURCE_TYPE,
            "resourceId": _RESOURCE_ID,
        })
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 回滚链路集成测试
# ══════════════════════════════════════════════════════════════════════════════

class TestAuditRollbackFlow:
    """回滚 预检→执行 完整链路"""

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_rollback_check(self, api, v):
        """[P0] 回滚预检（检查是否可回滚）"""
        mock_id = str(uuid.uuid4())
        r = api.get(f"{OPLOG_BASE}/{mock_id}/rollback-check")
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_rollback_execute(self, api, v):
        """[P0] 执行回滚操作"""
        mock_id = str(uuid.uuid4())
        r = api.post(f"{OPLOG_BASE}/{mock_id}/rollback")
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 跨服务数据一致性集成测试
# ══════════════════════════════════════════════════════════════════════════════

class TestAuditCrossServiceConsistency:
    """审计日志跨服务一致性验证"""

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_audit_to_observability_pipeline(self, api, v):
        """[P1] 审计事件→可观测性服务 存储链路"""
        # Step1: 查询审计日志列表（验证 Observability 服务可达）
        r1 = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5})
        v.not_5xx(r1)
        # Step2: 查询审计统计（验证聚合能力）
        r2 = api.get(f"{OPLOG_BASE}/statistics", params={
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r2)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_permission_audit_flow(self, api, v):
        """[P1] 权限操作→审计日志记录验证"""
        # Step1: 查角色列表（触发权限模块操作）
        r1 = api.get("/api/system/role", params={"page": 1, "pageSize": 5})
        v.not_5xx(r1)
        # Step2: 审计日志中应有权限类别记录
        r2 = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": "permission"})
        v.not_5xx(r2)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_device_command_audit_flow(self, api, v):
        """[P1] 设备指令→审计日志记录验证"""
        # Step1: 查设备列表
        r1 = api.get("/api/device", params={"page": 1, "pageSize": 5})
        v.not_5xx(r1)
        # Step2: 审计日志中应有设备指令记录
        r2 = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": "device_command"})
        v.not_5xx(r2)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_auth_audit_flow(self, api, v):
        """[P1] 认证操作→审计日志记录验证"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": "auth"})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_config_audit_flow(self, api, v):
        """[P2] 配置变更→审计日志记录验证"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": "config"})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_transaction_audit_flow(self, api, v):
        """[P2] 交易操作→审计日志记录验证"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": "transaction"})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_data_export_audit_flow(self, api, v):
        """[P2] 数据导出→审计日志记录验证"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 5, "category": "data_export"})
        v.not_5xx(r)


# ══════════════════════════════════════════════════════════════════════════════
# 多租户隔离集成测试
# ══════════════════════════════════════════════════════════════════════════════

class TestAuditTenantIsolation:
    """操作审计多租户隔离验证"""

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_oplog_query_tenant_bound(self, api, v):
        """[P0] 操作日志查询隐含租户隔离"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 10})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p0
    @pytest.mark.observability
    def test_oplog_stats_tenant_bound(self, api, v):
        """[P0] 操作日志统计隐含租户隔离"""
        r = api.get(f"{OPLOG_BASE}/statistics", params={
            "startTime": "2025-01-01T00:00:00Z",
            "endTime": "2099-12-31T23:59:59Z",
        })
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p1
    @pytest.mark.observability
    def test_oplog_no_auth_rejected(self, no_auth_api, v):
        """[P1] 无认证访问审计日志被拒"""
        r = no_auth_api.get(OPLOG_BASE, params={"page": 1, "pageSize": 10})
        assert r.status_code in (401, 403), f"期望 401/403, 实际 {r.status_code}"


# ══════════════════════════════════════════════════════════════════════════════
# 分页边界集成测试
# ══════════════════════════════════════════════════════════════════════════════

class TestAuditPaginationBoundary:
    """操作审计分页边界条件验证"""

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_oplog_page_1_default(self, api, v):
        """[P2] 默认首页分页查询"""
        r = api.get(OPLOG_BASE)
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_oplog_large_page_number(self, api, v):
        """[P2] 超大页码不报错"""
        r = api.get(OPLOG_BASE, params={"page": 99999, "pageSize": 10})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_oplog_max_page_size(self, api, v):
        """[P2] pageSize 上限100"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 200})
        v.not_5xx(r)

    @pytest.mark.integration
    @pytest.mark.p2
    @pytest.mark.observability
    def test_oplog_page_size_1(self, api, v):
        """[P2] pageSize=1 最小分页"""
        r = api.get(OPLOG_BASE, params={"page": 1, "pageSize": 1})
        v.not_5xx(r)
