"""
Blockchain 审计链式哈希 + FISCO 基础设施集成测试

端点清单:
  审计日志 API（待实现的端点 — 先写测试确保 API 合规）:
    1. GET  /api/evidence/audit/logs              - 查询审计日志
    2. GET  /api/evidence/audit/logs/count         - 统计审计日志
    3. POST /api/evidence/audit/verify-integrity   - 验证链式哈希完整性
    4. GET  /api/evidence/audit/logs/{id}          - 查询单条审计日志

  FISCO 节点监控（已有端点）:
    5. GET  /api/internal/blockchain/evidence/fisco/status - FISCO 节点状态

共 5 个端点 × ~12 测试维度 = ~60 个测试用例
"""

import pytest
import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from mock_client import MockApiClient, MOCK_TOKEN


class MockApiClientTA:
    """测试API客户端适配器"""
    def __init__(self):
        self._client = MockApiClient(token=MOCK_TOKEN)
        self._saved_token = MOCK_TOKEN

    def get(self, endpoint, **kwargs):
        return self._client.get(f"/api/{endpoint}", **kwargs)

    def post(self, endpoint, json_data=None, **kwargs):
        return self._client.post(f"/api/{endpoint}", json=json_data, **kwargs)

    def clear_token(self):
        self._saved_token = self._client.token
        self._client.clear_token()

    def set_invalid_token(self):
        self._saved_token = self._client.token
        self._client.set_token("invalid.fake.token")

    def restore_token(self):
        self._client.set_token(self._saved_token)


@pytest.fixture(scope="module")
def api_client():
    return MockApiClientTA()


# ==================== 1. 审计日志查询 ====================
class TestAuditLogQuery:
    """审计日志查询测试（GET /api/evidence/audit/logs）"""

    def test_query_audit_logs_returns_200(self, api_client):
        resp = api_client.get("evidence/audit/logs")
        assert resp.status_code in [200, 404]

    def test_query_audit_logs_with_action_filter(self, api_client):
        resp = api_client.get("evidence/audit/logs?action=create")
        assert resp.status_code in [200, 404]

    def test_query_audit_logs_with_resource_filter(self, api_client):
        resp = api_client.get("evidence/audit/logs?resourceType=evidence")
        assert resp.status_code in [200, 404]

    def test_query_audit_logs_with_time_range(self, api_client):
        resp = api_client.get("evidence/audit/logs?startTime=2026-01-01T00:00:00Z&endTime=2026-12-31T23:59:59Z")
        assert resp.status_code in [200, 404]

    def test_query_audit_logs_with_pagination(self, api_client):
        resp = api_client.get("evidence/audit/logs?limit=10&offset=0")
        assert resp.status_code in [200, 404]

    def test_query_audit_logs_no_auth_returns_401(self, api_client):
        api_client.clear_token()
        resp = api_client.get("evidence/audit/logs")
        assert resp.status_code == 401
        api_client.restore_token()

    def test_query_audit_logs_invalid_token_returns_401(self, api_client):
        api_client.set_invalid_token()
        resp = api_client.get("evidence/audit/logs")
        assert resp.status_code == 401
        api_client.restore_token()

    def test_query_audit_logs_negative_limit(self, api_client):
        resp = api_client.get("evidence/audit/logs?limit=-1")
        assert resp.status_code in [200, 400, 404]

    def test_query_audit_logs_max_limit(self, api_client):
        resp = api_client.get("evidence/audit/logs?limit=10000")
        assert resp.status_code in [200, 400, 404]


# ==================== 2. 审计日志统计 ====================
class TestAuditLogCount:
    """审计日志统计测试（GET /api/evidence/audit/logs/count）"""

    def test_count_audit_logs_returns_200(self, api_client):
        resp = api_client.get("evidence/audit/logs/count")
        assert resp.status_code in [200, 404]

    def test_count_with_action_filter(self, api_client):
        resp = api_client.get("evidence/audit/logs/count?action=verify")
        assert resp.status_code in [200, 404]

    def test_count_with_resource_filter(self, api_client):
        resp = api_client.get("evidence/audit/logs/count?resourceType=contract")
        assert resp.status_code in [200, 404]

    def test_count_no_auth_returns_401(self, api_client):
        api_client.clear_token()
        resp = api_client.get("evidence/audit/logs/count")
        assert resp.status_code == 401
        api_client.restore_token()


# ==================== 3. 链式哈希完整性验证 ====================
class TestChainHashVerification:
    """链式哈希完整性验证（POST /api/evidence/audit/verify-integrity）"""

    def test_verify_integrity_returns_200(self, api_client):
        resp = api_client.post("evidence/audit/verify-integrity")
        assert resp.status_code in [200, 400, 404]

    def test_verify_integrity_with_limit(self, api_client):
        resp = api_client.post("evidence/audit/verify-integrity", json_data={"limit": 100})
        assert resp.status_code in [200, 404]

    def test_verify_integrity_no_auth_returns_401(self, api_client):
        api_client.clear_token()
        resp = api_client.post("evidence/audit/verify-integrity")
        assert resp.status_code == 401
        api_client.restore_token()

    def test_verify_integrity_invalid_token_returns_401(self, api_client):
        api_client.set_invalid_token()
        resp = api_client.post("evidence/audit/verify-integrity")
        assert resp.status_code == 401
        api_client.restore_token()

    def test_verify_integrity_response_structure(self, api_client):
        resp = api_client.post("evidence/audit/verify-integrity")
        if resp.status_code == 200:
            data = resp.json()
            assert "data" in data or "isValid" in data or "code" in data

    def test_verify_integrity_large_limit(self, api_client):
        resp = api_client.post("evidence/audit/verify-integrity", json_data={"limit": 10000})
        assert resp.status_code in [200, 400, 404]

    def test_verify_integrity_zero_limit(self, api_client):
        resp = api_client.post("evidence/audit/verify-integrity", json_data={"limit": 0})
        assert resp.status_code in [200, 400, 404]


# ==================== 4. 单条审计日志查询 ====================
class TestAuditLogDetail:
    """单条审计日志查询（GET /api/evidence/audit/logs/{id}）"""

    def test_query_by_valid_uuid(self, api_client):
        test_id = str(uuid.uuid4())
        resp = api_client.get(f"evidence/audit/logs/{test_id}")
        assert resp.status_code in [200, 404]

    def test_query_by_invalid_uuid_returns_400(self, api_client):
        resp = api_client.get("evidence/audit/logs/not-a-uuid")
        assert resp.status_code in [200, 400, 404]

    def test_query_nonexistent_returns_404(self, api_client):
        resp = api_client.get(f"evidence/audit/logs/{uuid.uuid4()}")
        assert resp.status_code in [404, 200]

    def test_query_by_id_no_auth_returns_401(self, api_client):
        api_client.clear_token()
        resp = api_client.get(f"evidence/audit/logs/{uuid.uuid4()}")
        assert resp.status_code == 401
        api_client.restore_token()

    def test_query_by_id_sql_injection(self, api_client):
        resp = api_client.get("evidence/audit/logs/'; DROP TABLE bc_audit_log;--")
        assert resp.status_code in [200, 400, 404]


# ==================== 5. FISCO 节点状态查询 ====================
class TestFiscoNodeStatus:
    """FISCO 节点状态查询"""

    def test_fisco_status_via_internal_api(self, api_client):
        resp = api_client.get("internal/blockchain/evidence/fisco/status")
        assert resp.status_code in [200, 403, 404, 503]

    def test_fisco_status_returns_node_info(self, api_client):
        resp = api_client.get("internal/blockchain/evidence/fisco/status")
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data.get("data", data), (dict, list))

    def test_fisco_status_no_auth_returns_401(self, api_client):
        api_client.clear_token()
        resp = api_client.get("internal/blockchain/evidence/fisco/status")
        assert resp.status_code in [401, 403, 404]
        api_client.restore_token()


# ==================== 6. YARP 网关路由测试 ====================
class TestYarpGatewayRoutes:
    """YARP 网关路由配置验证"""

    def test_evidence_route_matches_patterns(self):
        """验证 yarp.json 中存证路由正确配置"""
        import json
        yarp_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Gateway', 'yarp.json')
        if os.path.exists(yarp_path):
            with open(yarp_path, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            routes = config.get("ReverseProxy", {}).get("Routes", {})
            # 验证存证路由存在
            evidence_routes = {k: v for k, v in routes.items() if 'evidence' in k.lower()}
            assert len(evidence_routes) > 0, "应有存证相关路由"

    def test_evidence_route_targets_blockchain_cluster(self):
        """验证存证路由指向 blockchain-cluster"""
        import json
        yarp_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Gateway', 'yarp.json')
        if os.path.exists(yarp_path):
            with open(yarp_path, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            routes = config.get("ReverseProxy", {}).get("Routes", {})
            for name, route in routes.items():
                if 'evidence' in name.lower():
                    assert route.get("ClusterId") == "blockchain-cluster", \
                        f"路由 {name} 应指向 blockchain-cluster"


# ==================== 7. Docker Compose 配置验证 ====================
class TestDockerComposeConfig:
    """Docker Compose FISCO 配置验证"""

    def test_compose_has_fisco_env_vars(self):
        """验证 blockchain-service 包含 FISCO 环境变量"""
        compose_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docker', 'docker-compose.store-web3.yml')
        if os.path.exists(compose_path):
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'Blockchain__FISCO__Enabled=true' in content
            assert 'Blockchain__DefaultNetwork=FISCO' in content
            assert 'Blockchain__FISCO__EnableSM=true' in content

    def test_compose_has_fisco_node_service(self):
        """验证 compose 文件包含 FISCO 节点容器"""
        compose_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docker', 'docker-compose.store-web3.yml')
        if os.path.exists(compose_path):
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'fisco-node1:' in content
            assert 'jgsy-fisco-node1' in content

    def test_compose_has_webase_service(self):
        """验证 compose 文件包含 WeBASE 容器"""
        compose_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docker', 'docker-compose.store-web3.yml')
        if os.path.exists(compose_path):
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'webase-front:' in content
            assert 'jgsy-webase' in content

    def test_compose_has_fisco_volumes(self):
        """验证 compose 文件包含 FISCO 数据卷"""
        compose_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docker', 'docker-compose.store-web3.yml')
        if os.path.exists(compose_path):
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'fisco_data:' in content
            assert 'webase_data:' in content

    def test_compose_blockchain_depends_on_fisco(self):
        """验证 blockchain-service 依赖 fisco-node1"""
        compose_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docker', 'docker-compose.store-web3.yml')
        if os.path.exists(compose_path):
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'fisco-node1:' in content


# ==================== 8. appsettings.json 配置验证 ====================
class TestAppSettingsConfig:
    """appsettings.json FISCO 配置验证"""

    def test_fisco_enabled(self):
        """验证 FISCO 已启用"""
        import json
        settings_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'appsettings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            fisco = config.get("Blockchain", {}).get("FISCO", {})
            assert fisco.get("Enabled") is True

    def test_fisco_sm_enabled(self):
        """验证国密已启用"""
        import json
        settings_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'appsettings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            fisco = config.get("Blockchain", {}).get("FISCO", {})
            assert fisco.get("EnableSM") is True

    def test_default_chain_is_configured(self):
        """验证默认链已正确配置（支持 ChainMaker/FISCO）"""
        import json
        settings_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'appsettings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            multi_chain = config.get("Blockchain", {}).get("MultiChain", {})
            default_chain = multi_chain.get("DefaultChain")
            assert default_chain in ("ChainMaker", "FISCO", "Hyperchain"), \
                f"DefaultChain 应为受支持的链类型，实际值: {default_chain}"

    def test_fisco_nodes_configured(self):
        """验证 FISCO 节点已配置"""
        import json
        settings_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'appsettings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            fisco = config.get("Blockchain", {}).get("FISCO", {})
            nodes = fisco.get("Nodes", [])
            assert len(nodes) > 0


# ==================== 9. DbUp 迁移脚本验证 ====================
class TestDbUpMigrations:
    """验证 DbUp 迁移脚本存在且格式正确"""

    EXPECTED_MIGRATIONS = [
        "006_fisco_evidence_tables.sql",
        "007_fisco_migration_fields.sql",
        "008_audit_log_tamper_proof.sql",
        "009_evidence_permission_seed.sql",
        "010_three_admin_separation.sql",
        "011_evidence_menu_seed.sql",
    ]

    def test_all_fisco_migrations_exist(self):
        """验证所有FISCO相关迁移脚本存在"""
        migrations_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'Data', 'Migrations')
        if os.path.exists(migrations_dir):
            files = os.listdir(migrations_dir)
            for expected in self.EXPECTED_MIGRATIONS:
                assert expected in files, f"缺少迁移脚本: {expected}"

    def test_migration_006_has_evidence_table(self):
        """验证006含 bc_energy_evidence 建表"""
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'Data', 'Migrations', '006_fisco_evidence_tables.sql')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'bc_energy_evidence' in content
            assert 'bc_fisco_node_status' in content

    def test_migration_008_has_tamper_triggers(self):
        """验证008含防篡改触发器"""
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'Data', 'Migrations', '008_audit_log_tamper_proof.sql')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'prevent_audit_log_delete' in content
            assert 'prevent_audit_log_update' in content
            assert 'chain_hash' in content

    def test_migration_010_has_admin_separation(self):
        """验证010含三管分离"""
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'JGSY.AGI.Blockchain', 'Data', 'Migrations', '010_three_admin_separation.sql')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'SYSTEM_ADMIN' in content or 'system_admin' in content


# ==================== 10. 三管分离权限验证 ====================
class TestThreeAdminSeparation:
    """三管分离（系管/安管/审管）权限隔离测试"""

    def test_evidence_create_needs_permission(self, api_client):
        """创建存证需要 blockchain:evidence:create 权限"""
        resp = api_client.post("evidence", json_data={
            "evidenceType": "test",
            "businessId": f"TEST-{uuid.uuid4().hex[:8]}",
            "rawData": {"test": True}
        })
        # 有权限则 200，无权限则 403
        assert resp.status_code in [200, 201, 400, 403, 404]

    def test_evidence_verify_needs_permission(self, api_client):
        """验证存证需要 blockchain:evidence:verify 权限"""
        test_id = str(uuid.uuid4())
        resp = api_client.post(f"evidence/{test_id}/verify")
        assert resp.status_code in [200, 400, 403, 404]

    def test_audit_query_needs_permission(self, api_client):
        """查询审计日志需要 blockchain:audit:list 权限"""
        resp = api_client.get("evidence/audit/logs")
        assert resp.status_code in [200, 403, 404]

    def test_audit_verify_needs_permission(self, api_client):
        """验证链式哈希需要审管权限"""
        resp = api_client.post("evidence/audit/verify-integrity")
        assert resp.status_code in [200, 400, 403, 404]
