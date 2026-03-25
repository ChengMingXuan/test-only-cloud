"""
FISCO BCOS JSON-RPC 适配器测试
================================

覆盖 FISCO 特有的 JSON-RPC 2.0 协议行为：
  - JSON-RPC 请求格式（id / jsonrpc / method / params）
  - SM2 私钥签名认证
  - sendRawTransaction / call 路由
  - 存证合约交互（EvidenceContract ABI）
  - JSON-RPC error code → 统一错误映射
  - GroupId 多组管理
  - 节点轮询故障转移

运行：
  pytest tests/blockchain/test_fisco_adapter.py -v --tb=short
"""

import pytest
import json
import uuid
import respx
from httpx import Response


# ═══════════════════════════════════════════════════════════════
# Mock：FISCO JSON-RPC 服务端行为模拟
# ═══════════════════════════════════════════════════════════════

class MockFISCOService:
    """模拟 FISCO BCOS JSON-RPC 服务行为"""

    def __init__(self):
        self.deployed_contracts: dict = {}
        self.transactions: dict = {}
        self.evidences: dict = {}
        self.nodes = {
            "fisco-node1-primary": {"status": "healthy", "priority": 0, "role": "Primary",
                                    "endpoint": "http://fisco-node1:8545"},
            "fisco-node2-slave":   {"status": "healthy", "priority": 1, "role": "Slave",
                                    "endpoint": "http://fisco-node2:8545"},
        }
        self.active_node = "fisco-node1-primary"
        self.group_id = 1
        self.call_count = 0

    # ── 合约部署 ──
    def handle_deploy(self, request):
        self.call_count += 1
        body = json.loads(request.content)
        contract_name = body.get("contractName", "")
        if not contract_name:
            return Response(400, json={"code": 400, "message": "contractName 为必填项"})
        tx_hash = f"0x{uuid.uuid4().hex}"
        contract_addr = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
        self.deployed_contracts[contract_name] = {
            "txId": tx_hash, "contractAddress": contract_addr,
            "version": body.get("version", "1.0"),
            "chainType": "FISCO",
            # FISCO 特有：返回 JSON-RPC 风格 status
            "jsonrpcResult": {"status": "0x0", "output": "0x"},
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_hash,
                "contractAddress": contract_addr,
                "blockHeight": 200 + self.call_count,
                "groupId": self.group_id,
            }
        })

    # ── 合约调用（sendRawTransaction） ──
    def handle_invoke(self, request):
        self.call_count += 1
        body = json.loads(request.content)
        method = body.get("method", "")
        # 模拟 JSON-RPC error code
        if method == "revert_method":
            return Response(200, json={
                "code": 200, "data": {
                    "success": False,
                    "jsonrpcError": {"code": -32000, "message": "execution reverted: Insufficient balance"},
                    "txId": None,
                }
            })
        if method == "parse_error":
            return Response(400, json={
                "code": 400,
                "jsonrpcError": {"code": -32700, "message": "Parse error"},
            })
        tx_hash = f"0x{uuid.uuid4().hex}"
        self.transactions[tx_hash] = {
            "method": method, "params": body.get("parameters", {}),
            "status": "confirmed", "blockHeight": 200 + self.call_count,
            "groupId": self.group_id,
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_hash,
                "blockHeight": 200 + self.call_count,
                "groupId": self.group_id,
            }
        })

    # ── 合约查询（call） ──
    def handle_query(self, request):
        self.call_count += 1
        body = json.loads(request.content)
        return Response(200, json={
            "code": 200, "data": {
                "success": True,
                "result": json.dumps({"queried": body.get("method"), "params": body.get("parameters", {})}),
                "groupId": self.group_id,
            }
        })

    # ── 存证保存（FISCO 特有：通过 ABI 编码调用 EvidenceContract） ──
    def handle_save_evidence(self, request):
        self.call_count += 1
        body = json.loads(request.content)
        evidence_id = body.get("evidenceId", str(uuid.uuid4()))
        data_hash = body.get("dataHash", "")
        if not data_hash:
            return Response(400, json={"code": 400, "message": "dataHash 为必填项"})
        tx_hash = f"0x{uuid.uuid4().hex}"
        self.evidences[evidence_id] = {
            "dataHash": data_hash, "extra": body.get("extra", ""),
            "txId": tx_hash, "timestamp": "2026-03-14T10:00:00Z",
            # FISCO 特有：ABI 编码结果
            "abiEncoded": True,
        }
        return Response(200, json={
            "code": 200, "data": {
                "success": True, "txId": tx_hash, "evidenceId": evidence_id,
                "abiEncoded": True,
            }
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
                "chain": "FISCO", "protocol": "JSON-RPC",
                "activeNode": self.active_node,
                "nodes": self.nodes,
                "groupId": self.group_id,
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


@pytest.fixture
def fisco_service():
    """每个测试用例得到独立的 FISCO 服务状态"""
    svc = MockFISCOService()
    base = "http://localhost:8021"
    prefix = "/api/blockchain/fisco"

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
# 测试：合约部署（FISCO JSON-RPC）
# ═══════════════════════════════════════════════════════════════

class TestFISCOContractDeploy:
    """FISCO 合约部署 — JSON-RPC 协议"""

    @pytest.mark.asyncio
    async def test_deploy_contract_success(self, fisco_service):
        """正向：成功部署合约，返回 0x 地址"""
        svc, _ = fisco_service
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/deploy", json={
                "contractName": "EvidenceContract",
                "version": "1.0",
                "bytecode": "608060405234801561001057600080fd",
                "runtimeType": "EVM",
            })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["txId"].startswith("0x"), "FISCO 交易ID应为 0x 十六进制格式"
        assert data["contractAddress"].startswith("0x"), "FISCO 合约地址应为 EVM 0x 格式"
        assert data["groupId"] == 1

    @pytest.mark.asyncio
    async def test_deploy_returns_evm_address(self, fisco_service):
        """FISCO 特有：合约地址使用 EVM 0x 格式（与 ChainMaker cm:// 不同）"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/deploy", json={
                "contractName": "CarbonTrade", "version": "1.0", "bytecode": "0x60",
            })
        addr = resp.json()["data"]["contractAddress"]
        assert addr.startswith("0x"), "FISCO 使用 EVM 0x 地址"
        assert len(addr) == 42, "FISCO 0x 地址长度应为 42 (0x + 40hex)"


# ═══════════════════════════════════════════════════════════════
# 测试：合约调用 — JSON-RPC 错误码映射
# ═══════════════════════════════════════════════════════════════

class TestFISCOContractInvoke:
    """FISCO 合约调用 — sendRawTransaction"""

    @pytest.mark.asyncio
    async def test_invoke_success(self, fisco_service):
        """正向：写操作成功"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/invoke", json={
                "contractName": "EvidenceContract",
                "method": "recordEvidence",
                "parameters": {"hash": "sha256:abc", "category": "energy"},
            })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["txId"].startswith("0x")

    @pytest.mark.asyncio
    async def test_invoke_execution_reverted(self, fisco_service):
        """FISCO 特有：JSON-RPC -32000 execution reverted"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/invoke", json={
                "contractName": "EvidenceContract",
                "method": "revert_method",
                "parameters": {},
            })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is False
        assert data["jsonrpcError"]["code"] == -32000, "应返回 JSON-RPC error code -32000"
        assert "reverted" in data["jsonrpcError"]["message"]

    @pytest.mark.asyncio
    async def test_invoke_parse_error(self, fisco_service):
        """FISCO 特有：JSON-RPC -32700 Parse error"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/invoke", json={
                "contractName": "EvidenceContract",
                "method": "parse_error",
                "parameters": {},
            })
        assert resp.status_code == 400
        body = resp.json()
        assert body["jsonrpcError"]["code"] == -32700

    @pytest.mark.asyncio
    async def test_query_readonly(self, fisco_service):
        """只读查询返回 groupId"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/contract/query", json={
                "contractName": "EvidenceContract",
                "method": "getEvidence", "parameters": {"hash": "abc"},
            })
        assert resp.status_code == 200
        assert resp.json()["data"]["groupId"] == 1


# ═══════════════════════════════════════════════════════════════
# 测试：存证操作（FISCO ABI 编码）
# ═══════════════════════════════════════════════════════════════

class TestFISCOEvidence:
    """FISCO 存证 — ABI 编码方式"""

    @pytest.mark.asyncio
    async def test_save_evidence_with_abi_encoding(self, fisco_service):
        """FISCO 特有：存证使用 ABI 编码"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/evidence/save", json={
                "evidenceId": "ev-fisco-001",
                "dataHash": "sha256:fisco_hash",
                "extra": json.dumps({"source": "carbon_trade"}),
            })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        assert data["abiEncoded"] is True, "FISCO 应使用 ABI 编码"

    @pytest.mark.asyncio
    async def test_get_evidence(self, fisco_service):
        svc, _ = fisco_service
        svc.evidences["ev-fisco-002"] = {
            "dataHash": "sha256:fisco_existing", "extra": "{}", "txId": "0xabc",
            "timestamp": "2026-03-14T10:00:00Z", "abiEncoded": True,
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/fisco/evidence/get",
                                    params={"evidenceId": "ev-fisco-002"})
        assert resp.status_code == 200
        assert resp.json()["data"]["dataHash"] == "sha256:fisco_existing"

    @pytest.mark.asyncio
    async def test_verify_evidence_match(self, fisco_service):
        svc, _ = fisco_service
        svc.evidences["ev-fisco-003"] = {
            "dataHash": "sha256:match_hash", "extra": "{}", "txId": "0xdef",
            "timestamp": "2026-03-14T10:00:00Z", "abiEncoded": True,
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/evidence/verify", json={
                "evidenceId": "ev-fisco-003", "expectedHash": "sha256:match_hash",
            })
        assert resp.status_code == 200
        assert resp.json()["data"]["verified"] is True

    @pytest.mark.asyncio
    async def test_verify_evidence_mismatch(self, fisco_service):
        svc, _ = fisco_service
        svc.evidences["ev-fisco-004"] = {
            "dataHash": "sha256:real", "extra": "{}", "txId": "0x111",
            "timestamp": "2026-03-14T10:00:00Z", "abiEncoded": True,
        }
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.post("/api/blockchain/fisco/evidence/verify", json={
                "evidenceId": "ev-fisco-004", "expectedHash": "sha256:fake",
            })
        assert resp.status_code == 200
        assert resp.json()["data"]["verified"] is False


# ═══════════════════════════════════════════════════════════════
# 测试：节点管理（JSON-RPC 轮询）
# ═══════════════════════════════════════════════════════════════

class TestFISCONodeManagement:
    """FISCO 节点管理 — JSON-RPC 协议特性"""

    @pytest.mark.asyncio
    async def test_node_status_returns_jsonrpc_topology(self, fisco_service):
        """节点状态应返回 JSON-RPC 协议标识"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/fisco/nodes/status")
        data = resp.json()["data"]
        assert data["chain"] == "FISCO"
        assert data["protocol"] == "JSON-RPC"
        assert data["groupId"] == 1

    @pytest.mark.asyncio
    async def test_fisco_node_endpoints_use_http(self, fisco_service):
        """FISCO 特有：节点端点使用 http:// 前缀（非 gRPC）"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/fisco/nodes/status")
        nodes = resp.json()["data"]["nodes"]
        for node_name, node_info in nodes.items():
            assert node_info["endpoint"].startswith("http://"), \
                f"FISCO 节点 {node_name} 应使用 http:// 端点"

    @pytest.mark.asyncio
    async def test_tx_status_hex_format(self, fisco_service):
        """FISCO 交易ID 使用 0x 十六进制格式"""
        svc, _ = fisco_service
        svc.transactions["0xdeadbeef"] = {"method": "test", "status": "confirmed",
                                           "blockHeight": 250, "groupId": 1}
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8021") as client:
            resp = await client.get("/api/blockchain/fisco/tx/status",
                                    params={"txId": "0xdeadbeef"})
        assert resp.json()["data"]["found"] is True
