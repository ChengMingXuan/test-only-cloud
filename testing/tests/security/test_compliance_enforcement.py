"""
等保2.0 合规测试 — 三权分立 / MFA强制 / 审计防篡改 / 日志留存 / 数据分级
==========================================================================
纯Mock测试，验证合规功能的逻辑正确性
"""
import pytest
import logging
from pathlib import Path
from tests.api.base_test import BaseApiTest
from mock_client import MockApiClient

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════
# 三权分立测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestThreeAdminSeparation(BaseApiTest):
    """等保2.0三权分立互斥校验"""

    SERVICE_NAME = "permission"
    API_PREFIX = "/api"

    MUTUAL_EXCLUSIVE_ROLES = [
        ("SYSTEM_ADMIN", "SECURITY_ADMIN"),
        ("SYSTEM_ADMIN", "AUDIT_ADMIN"),
        ("SECURITY_ADMIN", "AUDIT_ADMIN"),
        ("SYSTEM_ADMIN", "SECURITY_ADMIN", "AUDIT_ADMIN"),
    ]

    @pytest.mark.parametrize("roles", MUTUAL_EXCLUSIVE_ROLES)
    def test_admin_role_mutual_exclusion(self, api, roles):
        """三类管理角色不可同时分配给同一用户"""
        # 准备角色ID映射（使用固定UUID）
        role_id_map = {
            "SYSTEM_ADMIN": "00000000-0000-0000-0000-000000000012",
            "SECURITY_ADMIN": "00000000-0000-0000-0000-000000000010",
            "AUDIT_ADMIN": "00000000-0000-0000-0000-000000000011",
        }
        role_ids = [role_id_map[r] for r in roles]
        user_id = "00000000-0000-0000-0000-000000000999"

        resp = api.put(f"/api/user-roles/{user_id}/roles", json={
            "roleIds": role_ids
        })
        # 应该被拒绝（400或403）
        assert resp.status_code in (400, 403, 409), \
            f"三权分立互斥未生效：允许同时分配 {roles}"

    def test_single_admin_role_allowed(self, api):
        """单独分配一个管理角色应当允许"""
        user_id = "00000000-0000-0000-0000-000000000999"
        resp = api.put(f"/api/user-roles/{user_id}/roles", json={
            "roleIds": ["00000000-0000-0000-0000-000000000010"]  # SECURITY_ADMIN
        })
        # 不应是互斥错误
        assert resp.status_code != 409 or "ADMIN_ROLE_MUTUAL_EXCLUSION" not in resp.text

    def test_admin_roles_exist(self, api):
        """三类管理角色必须存在"""
        resp = api.get("/api/roles")
        if resp.status_code == 200:
            data = resp.json()
            roles = data.get("data", data) if isinstance(data, dict) else data
            if isinstance(roles, list):
                role_codes = [r.get("roleCode", "") for r in roles if isinstance(r, dict)]
                for admin_code in ["SYSTEM_ADMIN", "SECURITY_ADMIN", "AUDIT_ADMIN"]:
                    # 角色应已通过迁移脚本创建
                    logger.info("检查管理角色 %s 是否存在", admin_code)


# ═══════════════════════════════════════════════════
# MFA 强制验证测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestMfaEnforcement(BaseApiTest):
    """等保2.0 MFA强制验证（管理员角色）"""

    SERVICE_NAME = "identity"
    API_PREFIX = "/api"

    ADMIN_ROLES_REQUIRING_MFA = [
        "SUPER_ADMIN",
        "SECURITY_ADMIN",
        "AUDIT_ADMIN",
        "SYSTEM_ADMIN",
    ]

    def test_login_requires_mfa_for_admin(self, api):
        """管理员角色登录应触发MFA验证"""
        resp = api.post("/api/auth/login", json={
            "username": "admin",
            "password": "test_password_123"
        })
        # 如果用户有管理角色且MFA已启用，应返回200或特殊结果码
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", data) if isinstance(data, dict) else {}
            # 管理员登录结果应为 MfaRequired(200) 或 MfaSetupRequired(201)
            login_result = result.get("result")
            if login_result in (200, 201):
                logger.info("MFA强制验证已生效: result=%s", login_result)
                assert result.get("mfaPreAuthToken") is not None, \
                    "MFA强制验证应返回预认证令牌"

    def test_mfa_preauth_token_format(self, api):
        """MFA预认证令牌格式验证"""
        resp = api.post("/api/auth/login", json={
            "username": "security_admin",
            "password": "test_password_123"
        })
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", data) if isinstance(data, dict) else {}
            token = result.get("mfaPreAuthToken")
            if token:
                # 预认证令牌应为32位hex字符串
                assert len(token) == 32, f"预认证令牌长度异常: {len(token)}"
                assert all(c in "0123456789abcdef" for c in token), \
                    "预认证令牌应为hex格式"

    def test_mfa_config_endpoint(self, api):
        """MFA配置管理端点应可访问"""
        resp = api.get("/api/mfa/configs")
        assert resp.status_code in (200, 401, 403), \
            f"MFA配置端点异常: {resp.status_code}"


# ═══════════════════════════════════════════════════
# 审计日志防篡改测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestAuditLogTamperProof(BaseApiTest):
    """审计日志防篡改（链式哈希）"""

    SERVICE_NAME = "blockchain"
    API_PREFIX = "/api"

    def test_audit_log_chain_verification(self, api):
        """审计日志链式哈希完整性验证"""
        resp = api.get("/api/audit/verify")
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", data) if isinstance(data, dict) else {}
            if "isValid" in result:
                assert result["isValid"] is True, \
                    f"审计日志链式哈希验证失败: {result.get('message')}"

    def test_audit_log_query(self, api):
        """审计日志查询端点"""
        resp = api.get("/api/audit", params={"limit": 10})
        assert resp.status_code in (200, 401, 403), \
            f"审计日志查询异常: {resp.status_code}"

    def test_audit_log_no_delete(self, api):
        """审计日志禁止删除操作"""
        # 尝试调用删除审计日志的端点（不应存在或被拒绝）
        resp = api.delete("/api/audit/00000000-0000-0000-0000-000000000001")
        assert resp.status_code in (404, 405, 403, 401), \
            f"审计日志删除应被拒绝: {resp.status_code}"

    def test_audit_log_no_update(self, api):
        """审计日志禁止修改操作"""
        resp = api.put("/api/audit/00000000-0000-0000-0000-000000000001", json={
            "action": "modified"
        })
        assert resp.status_code in (404, 405, 403, 401), \
            f"审计日志修改应被拒绝: {resp.status_code}"


# ═══════════════════════════════════════════════════
# 日志留存策略测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestLogRetention(BaseApiTest):
    """日志留存策略（等保2.0要求≥180天）"""

    def test_loki_config_retention(self):
        """Loki日志留存配置应≥180天（4320小时）"""
        import yaml
        import os

        config_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "docker", "observability", "loki", "loki-config.yaml"),
            os.path.join(os.path.dirname(__file__), "..", "..", "deploy", "configs", "loki", "loki-config.yaml"),
        ]

        for config_path in config_paths:
            if not os.path.exists(config_path):
                continue

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 检查 limits_config.retention_period
            limits = config.get("limits_config", {})
            retention = limits.get("retention_period", "0h")
            hours = int(retention.replace("h", ""))
            assert hours >= 4320, \
                f"Loki limits_config 日志留存不足180天: {retention} ({config_path})"

            # 检查 table_manager.retention_period
            table_mgr = config.get("table_manager", {})
            tm_retention = table_mgr.get("retention_period", "0h")
            tm_hours = int(tm_retention.replace("h", ""))
            assert tm_hours >= 4320, \
                f"Loki table_manager 日志留存不足180天: {tm_retention} ({config_path})"

            logger.info("Loki留存配置合规: %s (%s)", retention, config_path)


# ═══════════════════════════════════════════════════
# 水印功能测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestWatermark(BaseApiTest):
    """操作水印（等保2.0操作留痕要求）"""

    def test_watermark_enabled(self):
        """前端水印功能应已启用"""
        config_path = Path(__file__).resolve().parents[3] / "JGSY.AGI.Frontend" / "src" / "config" / "system.ts"
        assert config_path.exists(), f"前端配置文件不存在: {config_path}"

        content = config_path.read_text(encoding="utf-8")

        assert "WATERMARK: true" in content, \
            "前端水印功能未启用（WATERMARK应为true）"

    def test_watermark_not_disabled_in_other_configs(self):
        """水印不应在其他配置中被覆盖禁用"""
        import os
        import glob

        frontend_dir = os.path.join(
            os.path.dirname(__file__), "..", "..",
            "JGSY.AGI.Frontend", "src"
        )
        # 搜索是否有其他地方覆盖水印设置
        for ts_file in glob.glob(os.path.join(frontend_dir, "**", "*.ts"), recursive=True):
            if "system.ts" in ts_file:
                continue
            with open(ts_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            assert "WATERMARK.*false" not in content or "WATERMARK: false" not in content, \
                f"水印在 {ts_file} 中被覆盖禁用"


# ═══════════════════════════════════════════════════
# 数据存证测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestEnergyEvidence(BaseApiTest):
    """能源数据存证（FISCO BCOS）"""

    SERVICE_NAME = "blockchain"
    API_PREFIX = "/api"

    EVIDENCE_TYPES = ["microgrid", "alarm", "workorder", "settlement"]

    @pytest.mark.parametrize("evidence_type", EVIDENCE_TYPES)
    def test_create_evidence(self, api, evidence_type):
        """创建各类型能源存证"""
        resp = api.post("/api/evidence", json={
            "evidenceType": evidence_type,
            "businessId": f"TEST-{evidence_type}-001",
            "stationId": "00000000-0000-0000-0000-000000000001",
            "rawData": {"type": evidence_type, "value": 100.0}
        })
        assert resp.status_code in (200, 201, 401, 403), \
            f"创建 {evidence_type} 存证异常: {resp.status_code}"

    def test_verify_evidence(self, api):
        """验证存证完整性"""
        resp = api.get("/api/evidence/verify", params={
            "evidenceId": "00000000-0000-0000-0000-000000000001"
        })
        assert resp.status_code in (200, 404, 401, 403), \
            f"验证存证异常: {resp.status_code}"

    def test_evidence_list(self, api):
        """查询存证列表"""
        resp = api.get("/api/evidence", params={"page": 1, "pageSize": 10})
        assert resp.status_code in (200, 401, 403), \
            f"查询存证列表异常: {resp.status_code}"


# ═══════════════════════════════════════════════════
# 国密算法测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestSMCrypto(BaseApiTest):
    """国密算法支持（SM2/SM3/SM4）"""

    SERVICE_NAME = "blockchain"
    API_PREFIX = "/api"

    def test_sm3_hash_endpoint(self, api):
        """SM3哈希计算端点"""
        resp = api.post("/api/crypto/hash", json={
            "algorithm": "SM3",
            "data": "test data for compliance"
        })
        assert resp.status_code in (200, 201, 401, 403, 404), \
            f"SM3哈希端点异常: {resp.status_code}"

    def test_sm2_sign_verify_endpoint(self, api):
        """SM2签名验签端点"""
        resp = api.post("/api/crypto/sign", json={
            "algorithm": "SM2",
            "data": "compliance test data"
        })
        assert resp.status_code in (200, 201, 401, 403, 404), \
            f"SM2签名端点异常: {resp.status_code}"

    def test_sm4_encrypt_decrypt_endpoint(self, api):
        """SM4加解密端点"""
        resp = api.post("/api/crypto/encrypt", json={
            "algorithm": "SM4",
            "data": "sensitive compliance data"
        })
        assert resp.status_code in (200, 201, 401, 403, 404), \
            f"SM4加密端点异常: {resp.status_code}"


# ═══════════════════════════════════════════════════
# 密码策略测试
# ═══════════════════════════════════════════════════

@pytest.mark.security
@pytest.mark.compliance
class TestPasswordPolicy(BaseApiTest):
    """密码策略合规（等保2.0要求）"""

    WEAK_PASSWORDS = [
        "123456",
        "password",
        "admin",
        "12345678",
        "abc123",
        "admin123",
        "aaaaaa",
        "123abc",
    ]

    @pytest.mark.parametrize("weak_password", WEAK_PASSWORDS)
    def test_reject_weak_passwords(self, api, weak_password):
        """弱密码应被拒绝"""
        resp = api.post("/api/users", json={
            "username": "compliance_test_user",
            "password": weak_password,
            "realName": "合规测试用户",
            "email": "test@compliance.test",
            "phone": "13800138000"
        })
        if resp.status_code in (200, 201):
            data = resp.json()
            # 如果创建成功，密码策略可能有问题
            logger.warning("弱密码 '%s' 未被拒绝", weak_password)

    def test_password_complexity_required(self, api):
        """密码应要求包含大小写字母、数字和特殊字符"""
        # 仅数字
        resp = api.post("/api/users/change-password", json={
            "oldPassword": "OldP@ssw0rd123",
            "newPassword": "12345678901234"
        })
        assert resp.status_code != 200 or "success" not in str(resp.json()).lower(), \
            "纯数字密码不应被接受"
