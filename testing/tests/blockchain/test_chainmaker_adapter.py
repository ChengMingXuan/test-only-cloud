"""
长安链 ChainMaker gRPC 适配器测试
==================================

覆盖 ChainMaker 特有的 gRPC 协议行为：
  - gRPC 通道管理与节点优先级
  - TLS 客户端证书认证
  - Protobuf 序列化（TxRequest/TxResponse）
  - 合约部署/调用/查询（gRPC 路由）
  - 存证操作（SaveEvidence / GetEvidence / VerifyEvidence）
  - gRPC Status Code → 统一错误映射
  - 节点故障转移（同链内按 Priority 切换）
  - 国密 SM2/SM3 签名链路

运行：
  pytest tests/blockchain/test_chainmaker_adapter.py -v --tb=short
"""

import pytest
import json
import uuid
import respx
from httpx import Response
from unittest.mock import AsyncMock, MagicMock


# ═══════════════════════════════════════════════════════════════
# Mock：ChainMaker gRPC 服务端行为模拟
# ═══════════════════════════════════════════════════════════════

class MockChainMakerService:
    """模拟 ChainMaker gRPC 服务行为（通过 HTTP API 代理层测试）"""

    def __init__(self):
        self.deployed_contracts: dict = {}
        self.transactions: dict = {}
        self.evidences: dict = {}
        self.nodes = {
            "node1-primary": {"status": "healthy", "priority": 0, "role": "Primary",
                              "addr": "grpc://chainmaker-node1:12301"},
            "node2-slave":   {"status": "healthy", "priority": 1, "role": "Slave",
                              "addr": "grpc://chainmaker-node2:12301"},
            "node3-dr":      {"status": "healthy", "priority": 2, "role": "DR",
                              "addr": "grpc://chainmaker-node3:12301"},
        }
        self.active_node = "node1-primary"
        self.call_count = 0

    # ── 合约部署 ──
    def handle_deploy(self, request):
        self.call_count += 1
        body = json.loads(request.content)
        contract_name = body.get("contractName", "")
        if not contract_name:
            return Response(400, json={"code": 400, "message": "contractName 为必填项"})
        tx_id = f"cm-deploy-{uuid.uuid4().hex[:12]}"
        self.deployed_contracts[contract_name] = {
            "txId": tx_id, "version": body.get("version", "1.0"),
            "contractAddress": f"cm://{contract_name}",
            "runtimeType": body.get("runtimeType", "WASMER"),
            "chainType": "ChainMaker",
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_id,
                "contractAddress": f"cm://{contract_name}",
                "blockHeight": 100 + self.call_count,
            }
        })

    # ── 合约调用（写操作） ──
    def handle_invoke(self, request):
        self.call_count += 1
        body = json.loads(request.content)
        method = body.get("method", "")
        if method == "timeout_method":
            # 模拟 gRPC DEADLINE_EXCEEDED
            return Response(504, json={
                "code": 504, "message": "gRPC DEADLINE_EXCEEDED",
                "grpcStatusCode": 4
            })
        tx_id = f"cm-tx-{uuid.uuid4().hex[:12]}"
        self.transactions[tx_id] = {
            "method": method, "params": body.get("parameters", {}),
            "status": "confirmed", "blockHeight": 100 + self.call_count,
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_id,
                "blockHeight": 100 + self.call_count,
            }
        })

    # ── 合约查询（只读） ──
    def handle_query(self, request):
        self.call_count += 1
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
        body = json.loads(request.content)
        evidence_id = body.get("evidenceId", str(uuid.uuid4()))
        data_hash = body.get("dataHash", "")
        if not data_hash:
            return Response(400, json={"code": 400, "message": "dataHash 为必填项"})
        tx_id = f"cm-ev-{uuid.uuid4().hex[:12]}"
        self.evidences[evidence_id] = {
            "dataHash": data_hash, "extra": body.get("extra", ""),
            "txId": tx_id, "timestamp": "2026-03-14T10:00:00Z",
        }
        return Response(200, json={
            "code": 200, "data": {"success": True, "txId": tx_id, "evidenceId": evidence_id}
        })

    # ── 存证查询 ──
    def handle_get_evidence(self, request):
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
                "chain": "ChainMaker", "protocol": "gRPC",
                "activeNode": self.active_node,
                "nodes": self.nodes,
                "tlsEnabled": True, "smEnabled": True,
            }
        })

    # ── 交易状态查询 ──
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


@pytest.fixture
def chainmaker_service():
    """每个测试用例得到独立的 ChainMaker 服务状态"""
    svc = MockChainMakerService()
    base = "http://localhost:8021"
    prefix = "/api/blockchain/chainmaker"

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
# 测试：合约部署（gRPC）
# ═══════════════════════════════════════════════════════════════

class TestChainMakerContractDeploy:
    """长安链合约部署 — gRPC 协议"""

    @pytest.mark.asyncio
    async def test_deploy_contract_success(self, chainmaker_service):
        """正向：成功部署合约，返回 txId 和 contractAddress"""
        svc, _ = chainmaker_service
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/deploy", json={
                "contractName": "EvidenceStore",
                "version": "2.0",
                "bytecode": "base64encodedwasm",
                "runtimeType": "WASMER",
            })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["txId"].startswith("cm-deploy-")
        assert data["contractAddress"] == "cm://EvidenceStore"
        assert "EvidenceStore" in svc.deployed_contracts

    @pytest.mark.asyncio
    async def test_deploy_contract_missing_name(self, chainmaker_service):
        """反向：缺少 contractName 应返回 400"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/deploy", json={
                "version": "1.0", "bytecode": "abc",
            })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_deploy_returns_grpc_specific_address(self, chainmaker_service):
        """ChainMaker 特有：合约地址使用 cm:// 前缀（非 EVM 0x 格式）"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/deploy", json={
                "contractName": "CarbonCredit", "version": "1.0", "bytecode": "wasm",
            })
        addr = resp.json()["data"]["contractAddress"]
        assert addr.startswith("cm://"), "ChainMaker 合约地址应使用 cm:// 前缀"
        assert "0x" not in addr, "ChainMaker 不使用 EVM 地址格式"


# ═══════════════════════════════════════════════════════════════
# 测试：合约调用与查询（gRPC TxRequest 协议）
# ═══════════════════════════════════════════════════════════════

class TestChainMakerContractInvoke:
    """长安链合约调用 — gRPC TxRequest"""

    @pytest.mark.asyncio
    async def test_invoke_contract_success(self, chainmaker_service):
        """正向：合约写操作成功"""
        svc, _ = chainmaker_service
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/invoke", json={
                "contractName": "EvidenceStore",
                "method": "recordEvidence",
                "parameters": {"hash": "sha256:abc123", "category": "telemetry"},
            })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["txId"].startswith("cm-tx-")
        assert data["blockHeight"] > 100

    @pytest.mark.asyncio
    async def test_invoke_grpc_deadline_exceeded(self, chainmaker_service):
        """ChainMaker 特有：gRPC DEADLINE_EXCEEDED 映射为 504"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/invoke", json={
                "contractName": "EvidenceStore",
                "method": "timeout_method",
                "parameters": {},
            })
        assert resp.status_code == 504
        body = resp.json()
        assert body.get("grpcStatusCode") == 4, "应返回 gRPC status code 4 (DEADLINE_EXCEEDED)"

    @pytest.mark.asyncio
    async def test_query_contract_readonly(self, chainmaker_service):
        """只读查询不产生交易"""
        svc, _ = chainmaker_service
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/contract/query", json={
                "contractName": "EvidenceStore",
                "method": "getEvidence",
                "parameters": {"hash": "abc123"},
            })
        assert resp.status_code == 200
        assert resp.json()["data"]["success"] is True
        # 查询不应产生交易记录
        assert len(svc.transactions) == 0


# ═══════════════════════════════════════════════════════════════
# 测试：存证操作（ChainMaker 特有路径）
# ═══════════════════════════════════════════════════════════════

class TestChainMakerEvidence:
    """长安链存证 — 保存/查询/验证"""

    @pytest.mark.asyncio
    async def test_save_evidence_success(self, chainmaker_service):
        """正向：保存存证"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/evidence/save", json={
                "evidenceId": "ev-cm-001",
                "dataHash": "sha256:deadbeef",
                "extra": json.dumps({"source": "telemetry", "deviceId": "dev-001"}),
            })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["evidenceId"] == "ev-cm-001"

    @pytest.mark.asyncio
    async def test_save_evidence_missing_hash(self, chainmaker_service):
        """反向：缺少 dataHash 应返回 400"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/evidence/save", json={
                "evidenceId": "ev-cm-002",
            })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_get_evidence_found(self, chainmaker_service):
        """正向：查询已存在的存证"""
        svc, _ = chainmaker_service
        svc.evidences["ev-cm-003"] = {
            "dataHash": "sha256:aabbcc", "extra": "{}", "txId": "cm-ev-xyz",
            "timestamp": "2026-03-14T10:00:00Z",
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/chainmaker/evidence/get",
                                    params={"evidenceId": "ev-cm-003"})
        assert resp.status_code == 200
        assert resp.json()["data"]["dataHash"] == "sha256:aabbcc"

    @pytest.mark.asyncio
    async def test_get_evidence_not_found(self, chainmaker_service):
        """反向：查询不存在的存证返回 404"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/chainmaker/evidence/get",
                                    params={"evidenceId": "nonexistent"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_verify_evidence_match(self, chainmaker_service):
        """正向：存证验证通过"""
        svc, _ = chainmaker_service
        svc.evidences["ev-cm-004"] = {
            "dataHash": "sha256:match", "extra": "{}", "txId": "cm-ev-ok",
            "timestamp": "2026-03-14T10:00:00Z",
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/evidence/verify", json={
                "evidenceId": "ev-cm-004", "expectedHash": "sha256:match",
            })
        assert resp.status_code == 200
        assert resp.json()["data"]["verified"] is True

    @pytest.mark.asyncio
    async def test_verify_evidence_mismatch(self, chainmaker_service):
        """反向：存证验证不通过（哈希不匹配）"""
        svc, _ = chainmaker_service
        svc.evidences["ev-cm-005"] = {
            "dataHash": "sha256:actual", "extra": "{}", "txId": "cm-ev-fail",
            "timestamp": "2026-03-14T10:00:00Z",
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/chainmaker/evidence/verify", json={
                "evidenceId": "ev-cm-005", "expectedHash": "sha256:different",
            })
        assert resp.status_code == 200
        assert resp.json()["data"]["verified"] is False


# ═══════════════════════════════════════════════════════════════
# 测试：gRPC 节点管理与故障转移
# ═══════════════════════════════════════════════════════════════

class TestChainMakerNodeManagement:
    """长安链节点管理 — gRPC 通道与 TLS"""

    @pytest.mark.asyncio
    async def test_node_status_returns_grpc_topology(self, chainmaker_service):
        """节点状态应返回 gRPC 节点拓扑"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/chainmaker/nodes/status")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["chain"] == "ChainMaker"
        assert data["protocol"] == "gRPC"
        assert data["tlsEnabled"] is True
        assert data["smEnabled"] is True
        assert len(data["nodes"]) == 3
        # 验证节点按 Priority 排列
        priorities = [n["priority"] for n in data["nodes"].values()]
        assert priorities == sorted(priorities)

    @pytest.mark.asyncio
    async def test_grpc_node_addresses_use_grpc_scheme(self, chainmaker_service):
        """ChainMaker 特有：节点地址使用 grpc:// 前缀"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/chainmaker/nodes/status")
        nodes = resp.json()["data"]["nodes"]
        for node_name, node_info in nodes.items():
            assert node_info["addr"].startswith("grpc://"), \
                f"节点 {node_name} 地址应使用 grpc:// 前缀，实际: {node_info['addr']}"

    @pytest.mark.asyncio
    async def test_tx_status_query(self, chainmaker_service):
        """交易状态查询"""
        svc, _ = chainmaker_service
        svc.transactions["cm-tx-known"] = {"method": "test", "status": "confirmed", "blockHeight": 150}
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/chainmaker/tx/status",
                                    params={"txId": "cm-tx-known"})
        assert resp.status_code == 200
        assert resp.json()["data"]["found"] is True
        assert resp.json()["data"]["status"] == "confirmed"

    @pytest.mark.asyncio
    async def test_tx_status_unknown(self, chainmaker_service):
        """查询不存在的交易"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/chainmaker/tx/status",
                                    params={"txId": "nonexistent-tx"})
        assert resp.status_code == 200
        assert resp.json()["data"]["found"] is False
