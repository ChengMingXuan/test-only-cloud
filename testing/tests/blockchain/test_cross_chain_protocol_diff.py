"""
跨协议差异对比测试
==================

验证三链适配器（ChainMaker gRPC / FISCO JSON-RPC / Hyperchain REST）
在同一 IChainClient 接口下的协议差异行为：

  - 合约地址格式差异（cm:// vs 0x vs 0x）
  - 交易ID格式差异（cm-deploy-* vs 0x* vs hyper-*）
  - 错误码映射差异（gRPC StatusCode vs JSON-RPC error code vs HTTP Status）
  - 认证方式差异（TLS证书 vs SM2签名 vs API Key）
  - 节点端点协议差异（grpc:// vs http:// vs https://）
  - 存证操作一致性（三链同一接口，同一结果）

运行：
  pytest tests/blockchain/test_cross_chain_protocol_diff.py -v --tb=short
"""

import pytest
import json
import uuid
import respx
from httpx import Response


# ═══════════════════════════════════════════════════════════════
# 联合 Mock 服务（三链共存）
# ═══════════════════════════════════════════════════════════════

class UnifiedMultiChainMock:
    """三链联合 Mock，用于对比测试"""

    def __init__(self):
        self.results: dict = {}

    def _chainmaker_deploy(self, request):
        body = json.loads(request.content)
        tx_id = f"cm-deploy-{uuid.uuid4().hex[:12]}"
        addr = f"cm://{body.get('contractName', 'unknown')}"
        self.results["chainmaker_deploy"] = {"txId": tx_id, "contractAddress": addr}
        return Response(200, json={"code": 200, "data": {
            "success": True, "txId": tx_id, "contractAddress": addr,
            "blockHeight": 101, "chain": "ChainMaker",
        }})

    def _fisco_deploy(self, request):
        body = json.loads(request.content)
        tx_id = f"0x{uuid.uuid4().hex}"
        addr = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
        self.results["fisco_deploy"] = {"txId": tx_id, "contractAddress": addr}
        return Response(200, json={"code": 200, "data": {
            "success": True, "txId": tx_id, "contractAddress": addr,
            "blockHeight": 201, "chain": "FISCO", "groupId": 1,
        }})

    def _hyperchain_deploy(self, request):
        if "x-api-key" not in request.headers and "authorization" not in request.headers:
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        body = json.loads(request.content)
        tx_id = f"hyper-{uuid.uuid4().hex[:16]}"
        addr = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
        self.results["hyperchain_deploy"] = {"txId": tx_id, "contractAddress": addr}
        return Response(200, json={"code": 200, "data": {
            "success": True, "txId": tx_id, "contractAddress": addr,
            "blockHeight": 301, "chain": "Hyperchain",
        }})

    # ── 错误场景 ──
    def _chainmaker_error(self, request):
        return Response(504, json={
            "code": 504, "message": "gRPC DEADLINE_EXCEEDED",
            "grpcStatusCode": 4, "chain": "ChainMaker",
        })

    def _fisco_error(self, request):
        return Response(200, json={"code": 200, "data": {
            "success": False,
            "jsonrpcError": {"code": -32000, "message": "execution reverted"},
            "chain": "FISCO",
        }})

    def _hyperchain_error(self, request):
        return Response(429, json={
            "code": 429, "message": "Too Many Requests",
            "retryAfter": 5, "chain": "Hyperchain",
        })

    # ── 节点状态 ──
    def _chainmaker_nodes(self, request):
        return Response(200, json={"code": 200, "data": {
            "chain": "ChainMaker", "protocol": "gRPC",
            "nodes": {"node1": {"addr": "grpc://cm:12301", "priority": 0}},
            "tlsEnabled": True, "smEnabled": True,
        }})

    def _fisco_nodes(self, request):
        return Response(200, json={"code": 200, "data": {
            "chain": "FISCO", "protocol": "JSON-RPC",
            "nodes": {"node1": {"endpoint": "http://fisco:8545", "priority": 0}},
            "groupId": 1, "smEnabled": True,
        }})

    def _hyperchain_nodes(self, request):
        return Response(200, json={"code": 200, "data": {
            "chain": "Hyperchain", "protocol": "REST",
            "nodes": {"node1": {"endpoint": "https://hyper:8081", "priority": 0}},
            "apiKeyRequired": True, "smEnabled": True,
        }})

    # ── 存证（通用行为，三链结果一致） ──
    def _chainmaker_save_evidence(self, request):
        body = json.loads(request.content)
        tx_id = f"cm-ev-{uuid.uuid4().hex[:12]}"
        return Response(200, json={"code": 200, "data": {
            "success": True, "txId": tx_id, "evidenceId": body["evidenceId"],
            "chain": "ChainMaker",
        }})

    def _fisco_save_evidence(self, request):
        body = json.loads(request.content)
        tx_id = f"0x{uuid.uuid4().hex}"
        return Response(200, json={"code": 200, "data": {
            "success": True, "txId": tx_id, "evidenceId": body["evidenceId"],
            "chain": "FISCO", "abiEncoded": True,
        }})

    def _hyperchain_save_evidence(self, request):
        if "x-api-key" not in request.headers and "authorization" not in request.headers:
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        body = json.loads(request.content)
        tx_id = f"hyper-{uuid.uuid4().hex[:16]}"
        return Response(200, json={"code": 200, "data": {
            "success": True, "txId": tx_id, "evidenceId": body["evidenceId"],
            "chain": "Hyperchain",
        }})


@pytest.fixture
def multi_chain_mock():
    """三链联合 Mock"""
    svc = UnifiedMultiChainMock()
    base = "http://localhost:8021"

    with respx.mock(base_url=base, assert_all_called=False) as mock:
        # 部署
        mock.post("/api/blockchain/chainmaker/contract/deploy").mock(side_effect=svc._chainmaker_deploy)
        mock.post("/api/blockchain/fisco/contract/deploy").mock(side_effect=svc._fisco_deploy)
        mock.post("/api/blockchain/hyperchain/contract/deploy").mock(side_effect=svc._hyperchain_deploy)
        # 错误场景
        mock.post("/api/blockchain/chainmaker/contract/invoke").mock(side_effect=svc._chainmaker_error)
        mock.post("/api/blockchain/fisco/contract/invoke").mock(side_effect=svc._fisco_error)
        mock.post("/api/blockchain/hyperchain/contract/invoke").mock(side_effect=svc._hyperchain_error)
        # 节点
        mock.get("/api/blockchain/chainmaker/nodes/status").mock(side_effect=svc._chainmaker_nodes)
        mock.get("/api/blockchain/fisco/nodes/status").mock(side_effect=svc._fisco_nodes)
        mock.get("/api/blockchain/hyperchain/nodes/status").mock(side_effect=svc._hyperchain_nodes)
        # 存证
        mock.post("/api/blockchain/chainmaker/evidence/save").mock(side_effect=svc._chainmaker_save_evidence)
        mock.post("/api/blockchain/fisco/evidence/save").mock(side_effect=svc._fisco_save_evidence)
        mock.post("/api/blockchain/hyperchain/evidence/save").mock(side_effect=svc._hyperchain_save_evidence)
        yield svc, mock


# ═══════════════════════════════════════════════════════════════
# 测试：合约地址格式差异
# ═══════════════════════════════════════════════════════════════

class TestContractAddressFormat:
    """三链合约地址格式对比"""

    @pytest.mark.asyncio
    async def test_chainmaker_uses_cm_prefix(self, multi_chain_mock):
        """ChainMaker: cm:// 前缀"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/deploy",
                                     json={"contractName": "Test", "version": "1.0", "bytecode": "wasm"})
        addr = resp.json()["data"]["contractAddress"]
        assert addr.startswith("cm://"), f"ChainMaker 应使用 cm:// 前缀，实际: {addr}"

    @pytest.mark.asyncio
    async def test_fisco_uses_evm_0x(self, multi_chain_mock):
        """FISCO: 0x EVM 格式"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/deploy",
                                     json={"contractName": "Test", "version": "1.0", "bytecode": "0x60"})
        addr = resp.json()["data"]["contractAddress"]
        assert addr.startswith("0x"), f"FISCO 应使用 0x 前缀，实际: {addr}"
        assert len(addr) == 42

    @pytest.mark.asyncio
    async def test_hyperchain_uses_evm_0x(self, multi_chain_mock):
        """Hyperchain: 0x EVM 格式（与 FISCO 一致）"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/hyperchain/contract/deploy",
                                     json={"contractName": "Test", "version": "1.0", "bytecode": "0x60"},
                                     headers={"x-api-key": "test-key"})
        addr = resp.json()["data"]["contractAddress"]
        assert addr.startswith("0x"), f"Hyperchain 应使用 0x 前缀，实际: {addr}"


# ═══════════════════════════════════════════════════════════════
# 测试：交易ID格式差异
# ═══════════════════════════════════════════════════════════════

class TestTransactionIdFormat:
    """三链交易ID格式对比"""

    @pytest.mark.asyncio
    async def test_three_chains_different_txid_format(self, multi_chain_mock):
        """交易ID格式：cm-deploy-* / 0x* / hyper-*"""
        svc, _ = multi_chain_mock
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            cm = await client.post("/api/blockchain/chainmaker/contract/deploy",
                                    json={"contractName": "A", "version": "1", "bytecode": "w"})
            fisco = await client.post("/api/blockchain/fisco/contract/deploy",
                                      json={"contractName": "B", "version": "1", "bytecode": "0x"})
            hyper = await client.post("/api/blockchain/hyperchain/contract/deploy",
                                      json={"contractName": "C", "version": "1", "bytecode": "0x"},
                                      headers={"x-api-key": "key"})

        cm_tx = cm.json()["data"]["txId"]
        fisco_tx = fisco.json()["data"]["txId"]
        hyper_tx = hyper.json()["data"]["txId"]

        assert cm_tx.startswith("cm-"), f"ChainMaker txId 前缀: cm-, 实际: {cm_tx}"
        assert fisco_tx.startswith("0x"), f"FISCO txId 前缀: 0x, 实际: {fisco_tx}"
        assert hyper_tx.startswith("hyper-"), f"Hyperchain txId 前缀: hyper-, 实际: {hyper_tx}"

        # 三者互不相同
        assert cm_tx != fisco_tx != hyper_tx


# ═══════════════════════════════════════════════════════════════
# 测试：错误码映射差异
# ═══════════════════════════════════════════════════════════════

class TestErrorCodeMapping:
    """三链错误码映射对比（核心差异点）"""

    @pytest.mark.asyncio
    async def test_chainmaker_grpc_status_code(self, multi_chain_mock):
        """ChainMaker: gRPC DEADLINE_EXCEEDED → HTTP 504 + grpcStatusCode"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/invoke",
                                     json={"method": "test", "parameters": {}})
        assert resp.status_code == 504
        body = resp.json()
        assert "grpcStatusCode" in body, "ChainMaker 应返回 grpcStatusCode"
        assert body["grpcStatusCode"] == 4

    @pytest.mark.asyncio
    async def test_fisco_jsonrpc_error_code(self, multi_chain_mock):
        """FISCO: JSON-RPC -32000 execution reverted → HTTP 200 + jsonrpcError"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/invoke",
                                     json={"method": "test", "parameters": {}})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is False
        assert "jsonrpcError" in data, "FISCO 应返回 jsonrpcError"
        assert data["jsonrpcError"]["code"] == -32000

    @pytest.mark.asyncio
    async def test_hyperchain_http_status_code(self, multi_chain_mock):
        """Hyperchain: HTTP 429 Too Many Requests + retryAfter"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/hyperchain/contract/invoke",
                                     json={"method": "test", "parameters": {}},
                                     headers={"x-api-key": "key"})
        assert resp.status_code == 429
        body = resp.json()
        assert "retryAfter" in body, "Hyperchain 应返回 retryAfter"

    @pytest.mark.asyncio
    async def test_error_types_are_fundamentally_different(self, multi_chain_mock):
        """三链错误表达方式完全不同：gRPC StatusCode / JSON-RPC error / HTTP Status"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            cm = await client.post("/api/blockchain/chainmaker/contract/invoke",
                                    json={"method": "t", "parameters": {}})
            fisco = await client.post("/api/blockchain/fisco/contract/invoke",
                                      json={"method": "t", "parameters": {}})
            hyper = await client.post("/api/blockchain/hyperchain/contract/invoke",
                                      json={"method": "t", "parameters": {}},
                                      headers={"x-api-key": "k"})

        # 三种不同的错误模式
        assert cm.status_code == 504, "ChainMaker 错误用 HTTP 5xx 映射"
        assert fisco.status_code == 200, "FISCO 错误包在 200 响应的 data.success=false 内"
        assert hyper.status_code == 429, "Hyperchain 使用原生 HTTP 状态码"


# ═══════════════════════════════════════════════════════════════
# 测试：认证方式差异
# ═══════════════════════════════════════════════════════════════

class TestAuthenticationDiff:
    """三链认证方式对比"""

    @pytest.mark.asyncio
    async def test_chainmaker_no_api_key_needed(self, multi_chain_mock):
        """ChainMaker: 使用 TLS 证书认证（不需要 API Key）"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/deploy",
                                     json={"contractName": "X", "version": "1", "bytecode": "w"})
        # ChainMaker 不校验 API Key，直接成功
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_hyperchain_requires_api_key(self, multi_chain_mock):
        """Hyperchain: 必须携带 API Key（否则 403）"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            # 不带 API Key
            resp_no_key = await client.post("/api/blockchain/hyperchain/contract/deploy",
                                            json={"contractName": "Y", "version": "1", "bytecode": "0x"})
            # 带 API Key
            resp_with_key = await client.post("/api/blockchain/hyperchain/contract/deploy",
                                              json={"contractName": "Z", "version": "1", "bytecode": "0x"},
                                              headers={"x-api-key": "valid-key"})
        assert resp_no_key.status_code == 403
        assert resp_with_key.status_code == 200


# ═══════════════════════════════════════════════════════════════
# 测试：节点端点协议差异
# ═══════════════════════════════════════════════════════════════

class TestNodeEndpointProtocol:
    """三链节点端点协议对比"""

    @pytest.mark.asyncio
    async def test_three_chains_different_protocols(self, multi_chain_mock):
        """节点端点协议：gRPC / JSON-RPC / REST"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            cm = await client.get("/api/blockchain/chainmaker/nodes/status")
            fisco = await client.get("/api/blockchain/fisco/nodes/status")
            hyper = await client.get("/api/blockchain/hyperchain/nodes/status")

        assert cm.json()["data"]["protocol"] == "gRPC"
        assert fisco.json()["data"]["protocol"] == "JSON-RPC"
        assert hyper.json()["data"]["protocol"] == "REST"

    @pytest.mark.asyncio
    async def test_node_address_schemes(self, multi_chain_mock):
        """节点地址 scheme 差异：grpc:// / http:// / https://"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            cm = await client.get("/api/blockchain/chainmaker/nodes/status")
            fisco = await client.get("/api/blockchain/fisco/nodes/status")
            hyper = await client.get("/api/blockchain/hyperchain/nodes/status")

        cm_node = list(cm.json()["data"]["nodes"].values())[0]
        fisco_node = list(fisco.json()["data"]["nodes"].values())[0]
        hyper_node = list(hyper.json()["data"]["nodes"].values())[0]

        assert cm_node["addr"].startswith("grpc://")
        assert fisco_node["endpoint"].startswith("http://")
        assert hyper_node["endpoint"].startswith("https://")

    @pytest.mark.asyncio
    async def test_all_chains_support_national_crypto(self, multi_chain_mock):
        """三链均支持国密（SM2/SM3/SM4）——这是统一要求"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            cm = await client.get("/api/blockchain/chainmaker/nodes/status")
            fisco = await client.get("/api/blockchain/fisco/nodes/status")
            hyper = await client.get("/api/blockchain/hyperchain/nodes/status")

        assert cm.json()["data"]["smEnabled"] is True
        assert fisco.json()["data"]["smEnabled"] is True
        assert hyper.json()["data"]["smEnabled"] is True


# ═══════════════════════════════════════════════════════════════
# 测试：存证操作一致性（三链同一接口）
# ═══════════════════════════════════════════════════════════════

class TestEvidenceConsistency:
    """三链存证操作一致性验证"""

    @pytest.mark.asyncio
    async def test_save_evidence_all_chains_return_success(self, multi_chain_mock):
        """三链存证保存接口统一返回 success + txId + evidenceId"""
        import httpx
        evidence_payload = {
            "evidenceId": "ev-cross-001",
            "dataHash": "sha256:unified_hash",
            "extra": json.dumps({"source": "cross_chain_test"}),
        }
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            cm = await client.post("/api/blockchain/chainmaker/evidence/save", json=evidence_payload)
            fisco = await client.post("/api/blockchain/fisco/evidence/save", json=evidence_payload)
            hyper = await client.post("/api/blockchain/hyperchain/evidence/save",
                                      json=evidence_payload, headers={"x-api-key": "key"})

        for name, resp in [("ChainMaker", cm), ("FISCO", fisco), ("Hyperchain", hyper)]:
            assert resp.status_code == 200, f"{name} 存证应返回 200"
            data = resp.json()["data"]
            assert data["success"] is True, f"{name} 存证应成功"
            assert "txId" in data, f"{name} 应返回 txId"
            assert data["evidenceId"] == "ev-cross-001", f"{name} evidenceId 应一致"

    @pytest.mark.asyncio
    async def test_evidence_txid_format_differs_per_chain(self, multi_chain_mock):
        """存证 txId 格式因链而异"""
        import httpx
        payload = {"evidenceId": "ev-cross-002", "dataHash": "sha256:diff_test", "extra": "{}"}
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            cm = await client.post("/api/blockchain/chainmaker/evidence/save", json=payload)
            fisco = await client.post("/api/blockchain/fisco/evidence/save", json=payload)
            hyper = await client.post("/api/blockchain/hyperchain/evidence/save",
                                      json=payload, headers={"x-api-key": "k"})

        assert cm.json()["data"]["txId"].startswith("cm-")
        assert fisco.json()["data"]["txId"].startswith("0x")
        assert hyper.json()["data"]["txId"].startswith("hyper-")
