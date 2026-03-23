"""
blockchain 测试目录的 pytest 配置
- 自动启用 asyncio 模式（所有 async def 测试无需手动标注 @pytest.mark.asyncio）
- 配置测试数据库基础连接（Mock 模式，不连真实库）
- 使用 respx 拦截 httpx 调用，实现无需真实服务的 API 集成测试
"""
import json
import pytest
import respx
from httpx import Response


# ==================================================================================
# asyncio 自动配置
# ==================================================================================

def pytest_collection_modifyitems(items):
    """为所有 async 测试自动添加 asyncio 标记"""
    import asyncio
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


# ==================================================================================
# 有状态区块链服务 Mock（用于 API 集成测试）
# ==================================================================================

class _MockBlockchainState:
    """在同一测试内跨请求共享的服务状态"""

    VALID_CHAINS = {"ChainMaker", "FISCO", "Hyperchain"}

    def __init__(self):
        self.active_chain = "ChainMaker"
        self.active_node = "node-A-primary"
        self.is_locked = False
        self.nodes = {
            "node-A-primary": {"available": True, "callCount": 0},
            "node-B-slave":   {"available": True, "callCount": 0},
            "node-C-dr":      {"available": True, "callCount": 0},
        }

    # ----- 路由处理器 -----

    def handle_get_status(self, request):
        if not self._has_auth(request):
            return Response(401, json={"code": 401, "message": "Unauthorized"})
        return Response(200, json={
            "code": 200, "message": "success",
            "data": {
                "activeChain": self.active_chain,
                "activeNode":  self.active_node,
                "isLocked":    self.is_locked,
                "nodes":       self.nodes,
            },
        })

    def handle_no_auth_status(self, request):
        """供"无认证应返回 401"用例专属路由（api_client 不带 token）"""
        return Response(401, json={"code": 401, "message": "Unauthorized"})

    def handle_switch_chain(self, request):
        if not self._has_auth(request):
            return Response(401, json={"code": 401, "message": "Unauthorized"})
        body = json.loads(request.content)
        target = body.get("targetChain", "")
        if target not in self.VALID_CHAINS:
            return Response(400, json={"code": 400, "message": f"Invalid chain: {target}"})
        prev = self.active_chain
        self.active_chain = target
        self.is_locked = True
        return Response(200, json={
            "code": 200,
            "data": {
                "success": True,
                "previous_chain": prev,
                "current_chain":  target,
                "reason": body.get("reason", ""),
                "message": f"Switched to {target}",
            },
        })

    def handle_switch_node(self, request):
        if not self._has_auth(request):
            return Response(401, json={"code": 401, "message": "Unauthorized"})
        body = json.loads(request.content)
        node = body.get("nodeName", "")
        if node not in self.nodes:
            return Response(400, json={"code": 400, "message": f"Node not found: {node}"})
        prev = self.active_node
        self.active_node = node
        return Response(200, json={
            "code": 200,
            "data": {
                "success": True,
                "previous_node": prev,
                "current_node":  node,
            },
        })

    def handle_reset(self, request):
        if not self._has_auth(request):
            return Response(401, json={"code": 401, "message": "Unauthorized"})
        prev = self.active_chain
        self.active_chain = "ChainMaker"
        self.active_node  = "node-A-primary"
        self.is_locked    = False
        return Response(200, json={
            "code": 200,
            "data": {
                "success": True,
                "previous_chain": prev,
                "current_chain":  "ChainMaker",
                "message":        "Reset to default",
            },
        })

    def handle_health(self, request):
        return Response(200, json={
            "status": "Healthy",
            "data": {
                "chains": {
                    "ChainMaker": "Healthy",
                    "FISCO":      "Healthy",
                    "Hyperchain": "Healthy",
                },
                "nodes": self.nodes,
            },
        })

    @staticmethod
    def _has_auth(request) -> bool:
        # httpx.Headers 是大小写不敏感的，直接用 `in` 检查
        return "authorization" in request.headers


@pytest.fixture
def mock_blockchain_service():
    """每个测试用例得到独立的服务状态 + respx 拦截层"""
    state = _MockBlockchainState()
    base = "http://localhost:8021"

    with respx.mock(base_url=base, assert_all_called=False) as mock:
        mock.get("/api/blockchain/failover/status").mock(side_effect=state.handle_get_status)
        mock.post("/api/blockchain/failover/switch-chain").mock(side_effect=state.handle_switch_chain)
        mock.post("/api/blockchain/failover/switch-node").mock(side_effect=state.handle_switch_node)
        mock.post("/api/blockchain/failover/reset").mock(side_effect=state.handle_reset)
        mock.get("/api/blockchain/health").mock(side_effect=state.handle_health)
        yield state
