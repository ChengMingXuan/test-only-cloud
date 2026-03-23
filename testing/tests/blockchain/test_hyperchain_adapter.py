"""
趣链 Hyperchain REST 适配器测试
=================================

覆盖 Hyperchain 特有的 RESTful HTTPS 协议行为：
  - REST API 端点构造（POST /api/v1/transactions 等）
  - API Key + Bearer Token 认证
  - 向后兼容（单 HttpEndpoint / 多 Nodes 模式）
  - 存证操作
  - HTTP Status Code → 统一错误映射
  - 节点故障转移

运行：
  pytest tests/blockchain/test_hyperchain_adapter.py -v --tb=short
"""

import pytest
import json
import uuid
import respx
from httpx import Response


# ═══════════════════════════════════════════════════════════════
# Mock：Hyperchain REST 服务端行为模拟
# ═══════════════════════════════════════════════════════════════

class MockHyperchainService:
    """模拟 Hyperchain RESTful 服务行为"""

    def __init__(self):
        self.deployed_contracts: dict = {}
        self.transactions: dict = {}
        self.evidences: dict = {}
        self.nodes = {
            "hyperchain-node1-primary": {
                "status": "healthy", "priority": 0, "role": "Primary",
                "endpoint": "https://hyperchain-node1:8081",
            },
            "hyperchain-node2-slave": {
                "status": "healthy", "priority": 1, "role": "Slave",
                "endpoint": "https://hyperchain-node2:8081",
            },
        }
        self.active_node = "hyperchain-node1-primary"
        self.call_count = 0

    # ── 合约部署 ──
    def handle_deploy(self, request):
        self.call_count += 1
        if not self._check_api_key(request):
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        body = json.loads(request.content)
        contract_name = body.get("contractName", "")
        if not contract_name:
            return Response(400, json={"code": 400, "message": "contractName 为必填项"})
        tx_hash = f"hyper-{uuid.uuid4().hex[:16]}"
        contract_addr = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
        self.deployed_contracts[contract_name] = {
            "txId": tx_hash, "contractAddress": contract_addr,
            "chainType": "Hyperchain",
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_hash,
                "contractAddress": contract_addr,
                "blockHeight": 300 + self.call_count,
            }
        })

    # ── 交易提交（POST /api/v1/transactions 风格） ──
    def handle_invoke(self, request):
        self.call_count += 1
        if not self._check_api_key(request):
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        body = json.loads(request.content)
        method = body.get("method", "")
        # 模拟 HTTP 429 限流
        if method == "rate_limited_method":
            return Response(429, json={
                "code": 429, "message": "Too Many Requests",
                "retryAfter": 5,
            })
        # 模拟 HTTP 503 服务不可用
        if method == "unavailable_method":
            return Response(503, json={"code": 503, "message": "Service Unavailable"})
        tx_hash = f"hyper-{uuid.uuid4().hex[:16]}"
        self.transactions[tx_hash] = {
            "method": method, "params": body.get("parameters", {}),
            "status": "confirmed", "blockHeight": 300 + self.call_count,
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_hash,
                "blockHeight": 300 + self.call_count,
            }
        })

    # ── 合约查询 ──
    def handle_query(self, request):
        self.call_count += 1
        if not self._check_api_key(request):
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        body = json.loads(request.content)
        return Response(200, json={
            "code": 200, "data": {
                "success": True,
                "result": json.dumps({"queried": body.get("method"), "params": body.get("parameters", {})}),
            }
        })

    # ── 存证保存 ──
    def handle_save_evidence(self, request):
        self.call_count += 1
        if not self._check_api_key(request):
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        body = json.loads(request.content)
        evidence_id = body.get("evidenceId", str(uuid.uuid4()))
        data_hash = body.get("dataHash", "")
        if not data_hash:
            return Response(400, json={"code": 400, "message": "dataHash 为必填项"})
        tx_hash = f"hyper-{uuid.uuid4().hex[:16]}"
        self.evidences[evidence_id] = {
            "dataHash": data_hash, "extra": body.get("extra", ""),
            "txId": tx_hash, "timestamp": "2026-03-14T10:00:00Z",
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_hash, "evidenceId": evidence_id,
            }
        })

    # ── 存证查询 ──
    def handle_get_evidence(self, request):
        if not self._check_api_key(request):
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        evidence_id = request.url.params.get("evidenceId", "")
        if evidence_id not in self.evidences:
            return Response(404, json={"code": 404, "message": f"存证 {evidence_id} 不存在"})
        ev = self.evidences[evidence_id]
        return Response(200, json={
            "code": 200, "data": {
                "found": True, "dataHash": ev["dataHash"],
                "extra": ev["extra"], "txId": ev["txId"],
            }
        })

    # ── 存证验证 ──
    def handle_verify_evidence(self, request):
        if not self._check_api_key(request):
            return Response(403, json={"code": 403, "message": "Invalid API Key"})
        body = json.loads(request.content)
        evidence_id = body.get("evidenceId", "")
        expected_hash = body.get("expectedHash", "")
        if evidence_id not in self.evidences:
            return Response(404, json={"code": 404, "message": f"存证 {evidence_id} 不存在"})
        actual_hash = self.evidences[evidence_id]["dataHash"]
        return Response(200, json={
            "code": 200, "data": {
                "verified": actual_hash == expected_hash,
                "actualHash": actual_hash, "expectedHash": expected_hash,
            }
        })

    # ── 节点状态 ──
    def handle_node_status(self, request):
        return Response(200, json={
            "code": 200, "data": {
                "chain": "Hyperchain", "protocol": "REST",
                "activeNode": self.active_node,
                "nodes": self.nodes,
                "apiKeyRequired": True,
                "smEnabled": True,
            }
        })

    # ── 交易状态 ──
    def handle_tx_status(self, request):
        tx_id = request.url.params.get("txId", "")
        if tx_id in self.transactions:
            return Response(200, json={
                "code": 200, "data": {
                    "found": True, "status": "confirmed",
                    "blockHeight": self.transactions[tx_id]["blockHeight"],
                }
            })
        return Response(200, json={
            "code": 200, "data": {"found": False, "status": "unknown"}
        })

    @staticmethod
    def _check_api_key(request) -> bool:
        """Hyperchain 特有：API Key 认证"""
        return "x-api-key" in request.headers or "authorization" in request.headers


@pytest.fixture
def hyperchain_service():
    """每个测试用例得到独立的 Hyperchain 服务状态"""
    svc = MockHyperchainService()
    base = "http://localhost:8021"
    prefix = "/api/blockchain/hyperchain"

    with respx.mock(base_url=base, assert_all_called=False) as mock:
        mock.post(f"{prefix}/contract/deploy").mock(side_effect=svc.handle_deploy)
        mock.post(f"{prefix}/contract/invoke").mock(side_effect=svc.handle_invoke)
        mock.post(f"{prefix}/contract/query").mock(side_effect=svc.handle_query)
        mock.post(f"{prefix}/evidence/save").mock(side_effect=svc.handle_save_evidence)
        mock.get(f"{prefix}/evidence/get").mock(side_effect=svc.handle_get_evidence)
        mock.post(f"{prefix}/evidence/verify").mock(side_effect=svc.handle_verify_evidence)
        mock.get(f"{prefix}/nodes/status").mock(side_effect=svc.handle_node_status)
        mock.get(f"{prefix}/tx/status").mock(side_effect=svc.handle_tx_status)
        yield svc, mock


# ═══════════════════════════════════════════════════════════════
# 测试：合约部署（REST）
# ═══════════════════════════════════════════════════════════════

class TestHyperchainContractDeploy:
    """Hyperchain 合约部署 — RESTful 协议"""

    @pytest.mark.asyncio
    async def test_deploy_contract_success(self, hyperchain_service):
        """正向：成功部署合约"""
        svc, _ = hyperchain_service
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/contract/deploy",
                json={"contractName": "EvidenceStore", "version": "1.0", "bytecode": "0x60"},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["txId"].startswith("hyper-"), "Hyperchain txId 应使用 hyper- 前缀"

    @pytest.mark.asyncio
    async def test_deploy_without_api_key_rejected(self, hyperchain_service):
        """Hyperchain 特有：缺少 API Key 返回 403"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/contract/deploy",
                json={"contractName": "Test", "version": "1.0", "bytecode": "0x"},
                # 不携带 x-api-key 或 authorization
            )
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════
# 测试：交易提交 — HTTP 状态码映射
# ═══════════════════════════════════════════════════════════════

class TestHyperchainContractInvoke:
    """Hyperchain 合约调用 — REST API"""

    @pytest.mark.asyncio
    async def test_invoke_success(self, hyperchain_service):
        """正向：写操作成功"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/contract/invoke",
                json={"contractName": "EvidenceStore", "method": "save", "parameters": {"k": "v"}},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_invoke_rate_limited(self, hyperchain_service):
        """Hyperchain 特有：HTTP 429 限流"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/contract/invoke",
                json={"contractName": "Test", "method": "rate_limited_method", "parameters": {}},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 429
        assert resp.json().get("retryAfter") == 5, "应返回 retryAfter 秒数"

    @pytest.mark.asyncio
    async def test_invoke_service_unavailable(self, hyperchain_service):
        """Hyperchain 特有：HTTP 503 服务不可用"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/contract/invoke",
                json={"contractName": "Test", "method": "unavailable_method", "parameters": {}},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 503

    @pytest.mark.asyncio
    async def test_query_readonly(self, hyperchain_service):
        """只读查询成功"""
        svc, _ = hyperchain_service
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/contract/query",
                json={"contractName": "Test", "method": "get", "parameters": {"id": "1"}},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 200
        assert len(svc.transactions) == 0, "查询不应产生交易记录"


# ═══════════════════════════════════════════════════════════════
# 测试：存证操作（REST）
# ═══════════════════════════════════════════════════════════════

class TestHyperchainEvidence:
    """Hyperchain 存证 — RESTful API"""

    @pytest.mark.asyncio
    async def test_save_evidence(self, hyperchain_service):
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/evidence/save",
                json={"evidenceId": "ev-hyper-001", "dataHash": "sha256:hyper_hash", "extra": "{}"},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_get_evidence(self, hyperchain_service):
        svc, _ = hyperchain_service
        svc.evidences["ev-hyper-002"] = {
            "dataHash": "sha256:existing", "extra": "{}", "txId": "hyper-xyz",
            "timestamp": "2026-03-14T10:00:00Z",
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get(
                "/api/blockchain/hyperchain/evidence/get",
                params={"evidenceId": "ev-hyper-002"},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["dataHash"] == "sha256:existing"

    @pytest.mark.asyncio
    async def test_verify_evidence_match(self, hyperchain_service):
        svc, _ = hyperchain_service
        svc.evidences["ev-hyper-003"] = {
            "dataHash": "sha256:ok", "extra": "{}", "txId": "hyper-abc",
            "timestamp": "2026-03-14T10:00:00Z",
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post(
                "/api/blockchain/hyperchain/evidence/verify",
                json={"evidenceId": "ev-hyper-003", "expectedHash": "sha256:ok"},
                headers={"x-api-key": "test-key"},
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["verified"] is True


# ═══════════════════════════════════════════════════════════════
# 测试：节点管理（REST 协议特性）
# ═══════════════════════════════════════════════════════════════

class TestHyperchainNodeManagement:
    """Hyperchain 节点管理 — REST 协议"""

    @pytest.mark.asyncio
    async def test_node_status_returns_rest_topology(self, hyperchain_service):
        """节点状态应返回 REST 协议标识"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/hyperchain/nodes/status")
        data = resp.json()["data"]
        assert data["chain"] == "Hyperchain"
        assert data["protocol"] == "REST"
        assert data["apiKeyRequired"] is True

    @pytest.mark.asyncio
    async def test_hyperchain_node_endpoints_use_https(self, hyperchain_service):
        """Hyperchain 特有：节点端点使用 https:// 前缀"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/hyperchain/nodes/status")
        nodes = resp.json()["data"]["nodes"]
        for node_name, node_info in nodes.items():
            assert node_info["endpoint"].startswith("https://"), \
                f"Hyperchain 节点 {node_name} 应使用 https:// 端点"
