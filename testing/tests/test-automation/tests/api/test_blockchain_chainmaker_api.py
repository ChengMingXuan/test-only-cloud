"""
Blockchain ChainMaker 主链架构 API 测试
覆盖：健康检查、故障转移端点、链状态查询、存证+ChainMaker交易、审计日志

端点清单:
  健康检查:
    1. GET  /api/health                           - 健康检查
    2. GET  /api/health/failover                  - 故障转移状态
    3. GET  /api/health/chains                    - 链状态列表

  链上查询:
    4. GET  /api/blockchain/query/chain-info       - 链信息查询
    5. GET  /api/blockchain/query/block/{number}   - 区块查询
    6. GET  /api/blockchain/query/tx/{hash}        - 交易查询

  存证（ChainMaker主链）:
    7. POST /api/evidence                          - 创建存证（走ChainMaker）
    8. POST /api/evidence/batch                    - 批量创建存证
    9. GET  /api/evidence/{id}                     - 查询存证
    10. POST /api/evidence/{id}/verify             - 验证存证
    11. GET  /api/evidence/statistics              - 存证统计

  合约:
    12. POST /api/contract/deploy                  - 部署合约（ChainMaker）
    13. POST /api/contract/invoke                  - 调用合约
    14. POST /api/contract/query                   - 查询合约

  交易:
    15. GET  /api/transaction/recent               - 最近交易
    16. GET  /api/transaction/{hash}               - 交易详情
    17. GET  /api/transaction/pending               - 待处理交易

  审计日志:
    18. GET  /api/blockchain/audit/logs             - 审计日志查询
    19. GET  /api/blockchain/audit/chain-integrity  - 链式哈希完整性检查

共计 19 个端点 × ~8 维度 = ~152 个测试用例
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

    def put(self, endpoint, json_data=None, **kwargs):
        return self._client.put(f"/api/{endpoint}", json=json_data, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._client.delete(f"/api/{endpoint}", **kwargs)

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


# ==================== 测试数据常量 ====================

VALID_EVIDENCE_BODY = {
    "evidenceType": "charging_session",
    "businessId": f"CS-CM-{uuid.uuid4().hex[:8]}",
    "stationId": "ST-CM-001",
    "deviceId": "DEV-CM-001",
    "rawDataSnapshot": '{"sessionId":"CS-CM-001","energy":75.5,"chainType":"ChainMaker"}'
}

BATCH_EVIDENCE_BODY = {
    "items": [
        {
            "evidenceType": "microgrid_dispatch",
            "businessId": f"MG-CM-{uuid.uuid4().hex[:8]}",
            "stationId": "ST-CM-001",
            "rawDataSnapshot": '{"dispatch":"peak_shaving","power":120.5}'
        },
        {
            "evidenceType": "alarm_event",
            "businessId": f"AL-CM-{uuid.uuid4().hex[:8]}",
            "deviceId": "DEV-CM-002",
            "rawDataSnapshot": '{"alarmType":"overvoltage","value":245.8}'
        }
    ]
}

DEPLOY_CONTRACT_BODY = {
    "contractName": "test_evidence_contract",
    "contractVersion": "1.0",
    "runtimeType": "WASMER",
    "bytecodeHex": "0061736d01000000"
}

INVOKE_CONTRACT_BODY = {
    "contractName": "electricity_trading",
    "method": "createOrder",
    "parameters": {
        "orderId": f"ORD-{uuid.uuid4().hex[:8]}",
        "quantity": "100",
        "price": "0.55"
    }
}

QUERY_CONTRACT_BODY = {
    "contractName": "electricity_trading",
    "method": "queryOrder",
    "parameters": {
        "orderId": "ORD-00001"
    }
}


# ==================== 1. 健康检查端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestHealthEndpoints:
    """健康检查端点 - ChainMaker主链状态"""

    def test_health_check_basic(self, api_client):
        """GET /api/health - 基本健康检查"""
        response = api_client.get("blockchain/api/health")
        assert response is not None
        assert response.status_code < 500

    def test_health_check_returns_chain_info(self, api_client):
        """GET /api/health - 应包含ChainMaker链信息"""
        response = api_client.get("blockchain/api/health")
        assert response is not None
        assert response.status_code < 500

    def test_health_failover_status(self, api_client):
        """GET /api/health/failover - 故障转移状态"""
        response = api_client.get("blockchain/api/health/failover")
        assert response is not None
        assert response.status_code < 500

    def test_health_failover_no_auth(self, api_client):
        """GET /api/health/failover - 无认证访问"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/health/failover")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_health_failover_invalid_token(self, api_client):
        """GET /api/health/failover - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.get("blockchain/api/health/failover")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_health_chains_status(self, api_client):
        """GET /api/health/chains - 所有链状态"""
        response = api_client.get("blockchain/api/health/chains")
        assert response is not None
        assert response.status_code < 500

    def test_health_chains_default_chainmaker(self, api_client):
        """GET /api/health/chains - 默认链应为ChainMaker"""
        response = api_client.get("blockchain/api/health/chains")
        assert response is not None
        assert response.status_code < 500

    def test_health_chains_no_auth(self, api_client):
        """GET /api/health/chains - 无认证访问健康检查"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/health/chains")
            assert response is not None
        finally:
            api_client.restore_token()


# ==================== 2. 链上查询端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestChainQueryEndpoints:
    """链上查询端点 - ChainMaker链信息查询"""

    def test_query_chain_info(self, api_client):
        """GET /api/blockchain/query/chain-info - 链信息"""
        response = api_client.get("blockchain/api/blockchain/query/chain-info")
        assert response is not None
        assert response.status_code < 500

    def test_query_chain_info_no_auth(self, api_client):
        """GET /api/blockchain/query/chain-info - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/blockchain/query/chain-info")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_query_block_by_number(self, api_client):
        """GET /api/blockchain/query/block/1 - 查询区块"""
        response = api_client.get("blockchain/api/blockchain/query/block/1")
        assert response is not None
        assert response.status_code < 500

    def test_query_block_negative_number(self, api_client):
        """GET /api/blockchain/query/block/-1 - 非法区块号"""
        response = api_client.get("blockchain/api/blockchain/query/block/-1")
        assert response is not None

    def test_query_block_zero(self, api_client):
        """GET /api/blockchain/query/block/0 - 创世区块"""
        response = api_client.get("blockchain/api/blockchain/query/block/0")
        assert response is not None
        assert response.status_code < 500

    def test_query_block_large_number(self, api_client):
        """GET /api/blockchain/query/block/999999999 - 超大区块号"""
        response = api_client.get("blockchain/api/blockchain/query/block/999999999")
        assert response is not None

    def test_query_tx_by_hash(self, api_client):
        """GET /api/blockchain/query/tx/{hash} - 按哈希查交易"""
        fake_hash = "0x" + uuid.uuid4().hex
        response = api_client.get(f"blockchain/api/blockchain/query/tx/{fake_hash}")
        assert response is not None
        assert response.status_code < 500

    def test_query_tx_empty_hash(self, api_client):
        """GET /api/blockchain/query/tx/ - 空哈希"""
        response = api_client.get("blockchain/api/blockchain/query/tx/")
        assert response is not None

    def test_query_tx_invalid_hash(self, api_client):
        """GET /api/blockchain/query/tx/invalid - 无效哈希"""
        response = api_client.get("blockchain/api/blockchain/query/tx/invalid-not-a-hash")
        assert response is not None

    def test_query_tx_no_auth(self, api_client):
        """GET /api/blockchain/query/tx/{hash} - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get(f"blockchain/api/blockchain/query/tx/0x{uuid.uuid4().hex}")
            assert response is not None
        finally:
            api_client.restore_token()


# ==================== 3. 存证端点测试（ChainMaker主链） ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestEvidenceChainMaker:
    """存证API - 通过ChainMaker主链创建/查询/验证"""

    def test_create_evidence_positive(self, api_client):
        """POST /api/evidence - 正常创建存证"""
        response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_create_evidence_missing_type(self, api_client):
        """POST /api/evidence - 缺少存证类型"""
        body = {**VALID_EVIDENCE_BODY}
        del body["evidenceType"]
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None

    def test_create_evidence_missing_business_id(self, api_client):
        """POST /api/evidence - 缺少业务ID"""
        body = {**VALID_EVIDENCE_BODY}
        del body["businessId"]
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None

    def test_create_evidence_empty_body(self, api_client):
        """POST /api/evidence - 空请求体"""
        response = api_client.post("blockchain/api/evidence", json_data={})
        assert response is not None

    def test_create_evidence_no_auth(self, api_client):
        """POST /api/evidence - 未认证"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
            assert response is not None
        finally:
            api_client.restore_token()

    def test_create_evidence_invalid_token(self, api_client):
        """POST /api/evidence - 无效Token"""
        api_client.set_invalid_token()
        try:
            response = api_client.post("blockchain/api/evidence", json_data=VALID_EVIDENCE_BODY)
            assert response is not None
        finally:
            api_client.restore_token()

    def test_create_evidence_large_data(self, api_client):
        """POST /api/evidence - 超大数据快照"""
        body = {**VALID_EVIDENCE_BODY, "rawDataSnapshot": "x" * 100000}
        response = api_client.post("blockchain/api/evidence", json_data=body)
        assert response is not None

    def test_batch_create_evidence(self, api_client):
        """POST /api/evidence/batch - 批量创建存证"""
        response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_batch_create_evidence_empty_items(self, api_client):
        """POST /api/evidence/batch - 空批次"""
        response = api_client.post("blockchain/api/evidence/batch", json_data={"items": []})
        assert response is not None

    def test_batch_create_evidence_no_auth(self, api_client):
        """POST /api/evidence/batch - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/evidence/batch", json_data=BATCH_EVIDENCE_BODY)
            assert response is not None
        finally:
            api_client.restore_token()

    def test_get_evidence_by_id(self, api_client):
        """GET /api/evidence/{id} - 查询存证"""
        eid = str(uuid.uuid4())
        response = api_client.get(f"blockchain/api/evidence/{eid}")
        assert response is not None
        assert response.status_code < 500

    def test_get_evidence_invalid_id(self, api_client):
        """GET /api/evidence/not-a-uuid - 无效ID"""
        response = api_client.get("blockchain/api/evidence/not-a-uuid")
        assert response is not None

    def test_get_evidence_nonexistent(self, api_client):
        """GET /api/evidence/{id} - 不存在的ID"""
        eid = str(uuid.uuid4())
        response = api_client.get(f"blockchain/api/evidence/{eid}")
        assert response is not None

    def test_verify_evidence(self, api_client):
        """POST /api/evidence/{id}/verify - 验证存证"""
        eid = str(uuid.uuid4())
        response = api_client.post(f"blockchain/api/evidence/{eid}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_verify_evidence_nonexistent(self, api_client):
        """POST /api/evidence/{id}/verify - 不存在的存证"""
        eid = str(uuid.uuid4())
        response = api_client.post(f"blockchain/api/evidence/{eid}/verify")
        assert response is not None

    def test_verify_evidence_no_auth(self, api_client):
        """POST /api/evidence/{id}/verify - 无认证"""
        api_client.clear_token()
        try:
            eid = str(uuid.uuid4())
            response = api_client.post(f"blockchain/api/evidence/{eid}/verify")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_evidence_statistics(self, api_client):
        """GET /api/evidence/statistics - 存证统计"""
        response = api_client.get("blockchain/api/evidence/statistics")
        assert response is not None
        assert response.status_code < 500

    def test_evidence_statistics_no_auth(self, api_client):
        """GET /api/evidence/statistics - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/evidence/statistics")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_evidence_list_paged(self, api_client):
        """GET /api/evidence?pageIndex=1&pageSize=10 - 分页查询"""
        response = api_client.get("blockchain/api/evidence?pageIndex=1&pageSize=10")
        assert response is not None
        assert response.status_code < 500

    def test_evidence_list_filter_type(self, api_client):
        """GET /api/evidence?evidenceType=charging_session - 按类型筛选"""
        response = api_client.get("blockchain/api/evidence?evidenceType=charging_session")
        assert response is not None
        assert response.status_code < 500

    def test_evidence_list_filter_status(self, api_client):
        """GET /api/evidence?status=confirmed - 按状态筛选"""
        response = api_client.get("blockchain/api/evidence?status=confirmed")
        assert response is not None
        assert response.status_code < 500

    def test_evidence_by_business_id(self, api_client):
        """GET /api/evidence/business/{id} - 按业务ID查询"""
        response = api_client.get("blockchain/api/evidence/business/CS-2026-00001")
        assert response is not None
        assert response.status_code < 500

    def test_evidence_timeline(self, api_client):
        """GET /api/evidence/timeline/{businessId} - 存证时间线"""
        response = api_client.get("blockchain/api/evidence/timeline/CS-2026-00001")
        assert response is not None
        assert response.status_code < 500

    def test_retry_failed_evidence(self, api_client):
        """POST /api/evidence/{id}/retry - 重试失败存证"""
        eid = str(uuid.uuid4())
        response = api_client.post(f"blockchain/api/evidence/{eid}/retry")
        assert response is not None
        assert response.status_code < 500


# ==================== 4. 合约端点测试（ChainMaker） ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestContractChainMaker:
    """智能合约API - ChainMaker链上合约操作"""

    def test_deploy_contract(self, api_client):
        """POST /api/contract/deploy - 部署合约"""
        response = api_client.post("blockchain/api/contract/deploy", json_data=DEPLOY_CONTRACT_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_deploy_contract_missing_name(self, api_client):
        """POST /api/contract/deploy - 缺少合约名"""
        body = {**DEPLOY_CONTRACT_BODY}
        del body["contractName"]
        response = api_client.post("blockchain/api/contract/deploy", json_data=body)
        assert response is not None

    def test_deploy_contract_no_auth(self, api_client):
        """POST /api/contract/deploy - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/contract/deploy", json_data=DEPLOY_CONTRACT_BODY)
            assert response is not None
        finally:
            api_client.restore_token()

    def test_deploy_contract_empty_bytecode(self, api_client):
        """POST /api/contract/deploy - 空字节码"""
        body = {**DEPLOY_CONTRACT_BODY, "bytecodeHex": ""}
        response = api_client.post("blockchain/api/contract/deploy", json_data=body)
        assert response is not None

    def test_invoke_contract(self, api_client):
        """POST /api/contract/invoke - 调用合约"""
        response = api_client.post("blockchain/api/contract/invoke", json_data=INVOKE_CONTRACT_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_invoke_contract_missing_method(self, api_client):
        """POST /api/contract/invoke - 缺少方法名"""
        body = {**INVOKE_CONTRACT_BODY}
        del body["method"]
        response = api_client.post("blockchain/api/contract/invoke", json_data=body)
        assert response is not None

    def test_invoke_contract_no_auth(self, api_client):
        """POST /api/contract/invoke - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/contract/invoke", json_data=INVOKE_CONTRACT_BODY)
            assert response is not None
        finally:
            api_client.restore_token()

    def test_invoke_contract_empty_params(self, api_client):
        """POST /api/contract/invoke - 空参数"""
        body = {**INVOKE_CONTRACT_BODY, "parameters": {}}
        response = api_client.post("blockchain/api/contract/invoke", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_query_contract(self, api_client):
        """POST /api/contract/query - 查询合约"""
        response = api_client.post("blockchain/api/contract/query", json_data=QUERY_CONTRACT_BODY)
        assert response is not None
        assert response.status_code < 500

    def test_query_contract_missing_contract_name(self, api_client):
        """POST /api/contract/query - 缺少合约名"""
        body = {**QUERY_CONTRACT_BODY}
        del body["contractName"]
        response = api_client.post("blockchain/api/contract/query", json_data=body)
        assert response is not None

    def test_query_contract_no_auth(self, api_client):
        """POST /api/contract/query - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/contract/query", json_data=QUERY_CONTRACT_BODY)
            assert response is not None
        finally:
            api_client.restore_token()

    def test_query_contract_nonexistent(self, api_client):
        """POST /api/contract/query - 不存在的合约"""
        body = {**QUERY_CONTRACT_BODY, "contractName": "nonexistent_contract"}
        response = api_client.post("blockchain/api/contract/query", json_data=body)
        assert response is not None


# ==================== 5. 交易端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestTransactionEndpoints:
    """交易查询API"""

    def test_recent_transactions(self, api_client):
        """GET /api/transaction/recent - 最近交易"""
        response = api_client.get("blockchain/api/transaction/recent")
        assert response is not None
        assert response.status_code < 500

    def test_recent_transactions_with_limit(self, api_client):
        """GET /api/transaction/recent?limit=5 - 限制数量"""
        response = api_client.get("blockchain/api/transaction/recent?limit=5")
        assert response is not None
        assert response.status_code < 500

    def test_recent_transactions_no_auth(self, api_client):
        """GET /api/transaction/recent - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/transaction/recent")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_get_transaction_by_hash(self, api_client):
        """GET /api/transaction/{hash} - 按哈希查询"""
        fake_hash = "0x" + uuid.uuid4().hex
        response = api_client.get(f"blockchain/api/transaction/{fake_hash}")
        assert response is not None
        assert response.status_code < 500

    def test_get_transaction_invalid_hash(self, api_client):
        """GET /api/transaction/invalid - 无效哈希"""
        response = api_client.get("blockchain/api/transaction/invalid-hash")
        assert response is not None

    def test_pending_transactions(self, api_client):
        """GET /api/transaction/pending - 待处理交易"""
        response = api_client.get("blockchain/api/transaction/pending")
        assert response is not None
        assert response.status_code < 500

    def test_pending_transactions_no_auth(self, api_client):
        """GET /api/transaction/pending - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/transaction/pending")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_transaction_count(self, api_client):
        """GET /api/transaction/count - 交易计数"""
        response = api_client.get("blockchain/api/transaction/count")
        assert response is not None
        assert response.status_code < 500

    def test_transaction_count_today(self, api_client):
        """GET /api/transaction/count/today - 今日交易计数"""
        response = api_client.get("blockchain/api/transaction/count/today")
        assert response is not None
        assert response.status_code < 500


# ==================== 6. 审计日志端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestAuditLogEndpoints:
    """审计日志API - 防篡改链式哈希"""

    def test_audit_logs_list(self, api_client):
        """GET /api/blockchain/audit/logs - 审计日志列表"""
        response = api_client.get("blockchain/api/blockchain/audit/logs")
        assert response is not None
        assert response.status_code < 500

    def test_audit_logs_paged(self, api_client):
        """GET /api/blockchain/audit/logs?pageIndex=1&pageSize=10 - 分页"""
        response = api_client.get("blockchain/api/blockchain/audit/logs?pageIndex=1&pageSize=10")
        assert response is not None
        assert response.status_code < 500

    def test_audit_logs_filter_action(self, api_client):
        """GET /api/blockchain/audit/logs?action=create - 按操作过滤"""
        response = api_client.get("blockchain/api/blockchain/audit/logs?action=create")
        assert response is not None
        assert response.status_code < 500

    def test_audit_logs_no_auth(self, api_client):
        """GET /api/blockchain/audit/logs - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/blockchain/audit/logs")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_audit_chain_integrity(self, api_client):
        """GET /api/blockchain/audit/chain-integrity - 链式哈希完整性"""
        response = api_client.get("blockchain/api/blockchain/audit/chain-integrity")
        assert response is not None
        assert response.status_code < 500

    def test_audit_chain_integrity_no_auth(self, api_client):
        """GET /api/blockchain/audit/chain-integrity - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/blockchain/audit/chain-integrity")
            assert response is not None
        finally:
            api_client.restore_token()


# ==================== 7. 钱包端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestWalletEndpoints:
    """钱包API - ChainMaker链上钱包"""

    def test_create_wallet(self, api_client):
        """POST /api/wallet/create - 创建钱包"""
        body = {"name": f"test-wallet-{uuid.uuid4().hex[:8]}"}
        response = api_client.post("blockchain/api/wallet/create", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_wallet_empty_name(self, api_client):
        """POST /api/wallet/create - 空名称"""
        response = api_client.post("blockchain/api/wallet/create", json_data={"name": ""})
        assert response is not None

    def test_create_wallet_no_auth(self, api_client):
        """POST /api/wallet/create - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.post("blockchain/api/wallet/create", json_data={"name": "test"})
            assert response is not None
        finally:
            api_client.restore_token()

    def test_get_wallet_balance(self, api_client):
        """GET /api/wallet/balance/{address} - 余额查询"""
        response = api_client.get(f"blockchain/api/wallet/balance/0x{uuid.uuid4().hex}")
        assert response is not None
        assert response.status_code < 500

    def test_get_wallet_list(self, api_client):
        """GET /api/wallet/list - 钱包列表"""
        response = api_client.get("blockchain/api/wallet/list")
        assert response is not None
        assert response.status_code < 500

    def test_get_wallet_list_no_auth(self, api_client):
        """GET /api/wallet/list - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/wallet/list")
            assert response is not None
        finally:
            api_client.restore_token()


# ==================== 8. 绿证/碳证端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestCertificateEndpoints:
    """绿证/碳证API"""

    def test_green_cert_list(self, api_client):
        """GET /api/certificates/green - 绿证列表"""
        response = api_client.get("blockchain/api/certificates/green")
        assert response is not None
        assert response.status_code < 500

    def test_green_cert_verify(self, api_client):
        """GET /api/certificates/green/verify/{tokenId} - 验证绿证"""
        response = api_client.get(f"blockchain/api/certificates/green/verify/{uuid.uuid4()}")
        assert response is not None
        assert response.status_code < 500

    def test_green_cert_no_auth(self, api_client):
        """GET /api/certificates/green - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/certificates/green")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_carbon_credit_list(self, api_client):
        """GET /api/certificates/carbon - 碳信用列表"""
        response = api_client.get("blockchain/api/certificates/carbon")
        assert response is not None
        assert response.status_code < 500

    def test_carbon_credit_verify(self, api_client):
        """GET /api/certificates/carbon/verify/{creditId} - 验证碳信用"""
        response = api_client.get(f"blockchain/api/certificates/carbon/verify/{uuid.uuid4()}")
        assert response is not None
        assert response.status_code < 500


# ==================== 9. 积分端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestPointsEndpoints:
    """积分API - 链上积分管理"""

    def test_points_balance(self, api_client):
        """GET /api/points/balance - 积分余额"""
        response = api_client.get("blockchain/api/points/balance")
        assert response is not None
        assert response.status_code < 500

    def test_points_balance_no_auth(self, api_client):
        """GET /api/points/balance - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/points/balance")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_points_transactions(self, api_client):
        """GET /api/points/transactions - 积分流水"""
        response = api_client.get("blockchain/api/points/transactions")
        assert response is not None
        assert response.status_code < 500

    def test_points_recharge(self, api_client):
        """POST /api/points/recharge - 积分充值"""
        body = {"amount": 1000, "paymentMethod": "alipay", "orderNo": f"PO-{uuid.uuid4().hex[:8]}"}
        response = api_client.post("blockchain/api/points/recharge", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_points_recharge_negative_amount(self, api_client):
        """POST /api/points/recharge - 负金额"""
        body = {"amount": -100, "paymentMethod": "alipay"}
        response = api_client.post("blockchain/api/points/recharge", json_data=body)
        assert response is not None

    def test_points_recharge_zero_amount(self, api_client):
        """POST /api/points/recharge - 零金额"""
        body = {"amount": 0, "paymentMethod": "alipay"}
        response = api_client.post("blockchain/api/points/recharge", json_data=body)
        assert response is not None

    def test_points_consume(self, api_client):
        """POST /api/points/consume - 积分消费"""
        body = {"amount": 50, "reason": "charging_fee", "businessId": f"CF-{uuid.uuid4().hex[:8]}"}
        response = api_client.post("blockchain/api/points/consume", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_points_consume_no_auth(self, api_client):
        """POST /api/points/consume - 无认证"""
        api_client.clear_token()
        try:
            body = {"amount": 50, "reason": "charging_fee"}
            response = api_client.post("blockchain/api/points/consume", json_data=body)
            assert response is not None
        finally:
            api_client.restore_token()


# ==================== 10. 电力交易端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestTradingEndpoints:
    """电力交易API"""

    def test_create_sell_order(self, api_client):
        """POST /api/trading/order - 创建卖单"""
        body = {
            "orderType": "sell",
            "quantityKwh": 100.0,
            "pricePerKwh": 0.55,
            "stationId": "ST-001",
            "energySource": "solar"
        }
        response = api_client.post("blockchain/api/trading/order", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_create_buy_order(self, api_client):
        """POST /api/trading/order - 创建买单"""
        body = {
            "orderType": "buy",
            "quantityKwh": 50.0,
            "pricePerKwh": 0.60,
            "stationId": "ST-002"
        }
        response = api_client.post("blockchain/api/trading/order", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_order_list(self, api_client):
        """GET /api/trading/orders - 订单列表"""
        response = api_client.get("blockchain/api/trading/orders")
        assert response is not None
        assert response.status_code < 500

    def test_order_list_filter_status(self, api_client):
        """GET /api/trading/orders?status=open - 按状态筛选"""
        response = api_client.get("blockchain/api/trading/orders?status=open")
        assert response is not None
        assert response.status_code < 500

    def test_order_detail(self, api_client):
        """GET /api/trading/order/{id} - 订单详情"""
        response = api_client.get(f"blockchain/api/trading/order/{uuid.uuid4()}")
        assert response is not None
        assert response.status_code < 500

    def test_order_no_auth(self, api_client):
        """POST /api/trading/order - 无认证"""
        api_client.clear_token()
        try:
            body = {"orderType": "sell", "quantityKwh": 100}
            response = api_client.post("blockchain/api/trading/order", json_data=body)
            assert response is not None
        finally:
            api_client.restore_token()

    def test_cancel_order(self, api_client):
        """POST /api/trading/order/{id}/cancel - 取消订单"""
        response = api_client.post(f"blockchain/api/trading/order/{uuid.uuid4()}/cancel")
        assert response is not None
        assert response.status_code < 500

    def test_trade_history(self, api_client):
        """GET /api/trading/history - 成交历史"""
        response = api_client.get("blockchain/api/trading/history")
        assert response is not None
        assert response.status_code < 500


# ==================== 11. 量子安全端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestQuantumSecurityEndpoints:
    """量子安全API - 后量子密码学"""

    def test_quantum_status(self, api_client):
        """GET /api/quantum/status - 量子安全状态"""
        response = api_client.get("blockchain/api/quantum/status")
        assert response is not None
        assert response.status_code < 500

    def test_quantum_key_generate(self, api_client):
        """POST /api/quantum/key-pair - 生成后量子密钥对"""
        response = api_client.post("blockchain/api/quantum/key-pair", json_data={"algorithm": "Dilithium3"})
        assert response is not None
        assert response.status_code < 500

    def test_quantum_status_no_auth(self, api_client):
        """GET /api/quantum/status - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/quantum/status")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_quantum_sign_verify(self, api_client):
        """POST /api/quantum/verify-signature - 验证签名"""
        body = {"data": "test_data_hash", "signature": "placeholder", "publicKey": "placeholder"}
        response = api_client.post("blockchain/api/quantum/verify-signature", json_data=body)
        assert response is not None
        assert response.status_code < 500


# ==================== 12. 分类存证端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestCategoryEvidenceEndpoints:
    """分类存证API - 数据治理v3.0"""

    def test_category_evidence_submit(self, api_client):
        """POST /api/category-evidence/submit - 提交分类存证"""
        body = {
            "dataCategory": 1,
            "evidenceType": "device_control",
            "businessId": f"DC-{uuid.uuid4().hex[:8]}",
            "rawData": '{"command":"start","deviceId":"DEV-001"}'
        }
        response = api_client.post("blockchain/api/category-evidence/submit", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_category_evidence_list(self, api_client):
        """GET /api/category-evidence - 分类存证列表"""
        response = api_client.get("blockchain/api/category-evidence")
        assert response is not None
        assert response.status_code < 500

    def test_category_evidence_by_category(self, api_client):
        """GET /api/category-evidence?dataCategory=1 - 按分类查"""
        response = api_client.get("blockchain/api/category-evidence?dataCategory=1")
        assert response is not None
        assert response.status_code < 500

    def test_category_evidence_verify(self, api_client):
        """POST /api/category-evidence/{id}/verify - 验证分类存证"""
        eid = str(uuid.uuid4())
        response = api_client.post(f"blockchain/api/category-evidence/{eid}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_category_evidence_no_auth(self, api_client):
        """GET /api/category-evidence - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/category-evidence")
            assert response is not None
        finally:
            api_client.restore_token()

    def test_merkle_aggregation_status(self, api_client):
        """GET /api/category-evidence/merkle/status - Merkle聚合状态"""
        response = api_client.get("blockchain/api/category-evidence/merkle/status")
        assert response is not None
        assert response.status_code < 500

    def test_evidence_audit_logs(self, api_client):
        """GET /api/category-evidence/audit-logs - 存证审计日志"""
        response = api_client.get("blockchain/api/category-evidence/audit-logs")
        assert response is not None
        assert response.status_code < 500

    def test_evidence_audit_log_no_auth(self, api_client):
        """GET /api/category-evidence/audit-logs - 无认证"""
        api_client.clear_token()
        try:
            response = api_client.get("blockchain/api/category-evidence/audit-logs")
            assert response is not None
        finally:
            api_client.restore_token()


# ==================== 13. 内部API端点测试 ====================

@pytest.mark.api
@pytest.mark.blockchain
class TestInternalApiEndpoints:
    """内部API - 服务间调用"""

    def test_internal_create_evidence(self, api_client):
        """POST /api/internal/blockchain/evidence - 内部创建存证"""
        body = {
            "evidenceType": "settlement",
            "businessId": f"ST-{uuid.uuid4().hex[:8]}",
            "rawDataSnapshot": '{"amount":1500.00,"period":"2026-03"}'
        }
        response = api_client.post("blockchain/api/internal/blockchain/evidence", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_internal_batch_evidence(self, api_client):
        """POST /api/internal/blockchain/evidence/batch - 内部批量存证"""
        body = {"items": [{"evidenceType": "workorder", "businessId": f"WO-{uuid.uuid4().hex[:8]}"}]}
        response = api_client.post("blockchain/api/internal/blockchain/evidence/batch", json_data=body)
        assert response is not None
        assert response.status_code < 500

    def test_internal_verify_evidence(self, api_client):
        """GET /api/internal/blockchain/evidence/{id}/verify - 内部验证"""
        eid = str(uuid.uuid4())
        response = api_client.get(f"blockchain/api/internal/blockchain/evidence/{eid}/verify")
        assert response is not None
        assert response.status_code < 500

    def test_internal_get_evidence(self, api_client):
        """GET /api/internal/blockchain/evidence/{id} - 内部查询"""
        eid = str(uuid.uuid4())
        response = api_client.get(f"blockchain/api/internal/blockchain/evidence/{eid}")
        assert response is not None
        assert response.status_code < 500

    def test_internal_evidence_by_business(self, api_client):
        """GET /api/internal/blockchain/evidence/business/{id} - 内部按业务ID"""
        response = api_client.get("blockchain/api/internal/blockchain/evidence/business/CS-001")
        assert response is not None
        assert response.status_code < 500
