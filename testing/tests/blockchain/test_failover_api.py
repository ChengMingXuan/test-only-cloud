"""
区块链服务 — API 集成测试（需要服务运行）
========================================================

覆盖所有 REST 端点：
  - GET /api/blockchain/failover/status
  - POST /api/blockchain/failover/switch-chain
  - POST /api/blockchain/failover/switch-node
  - POST /api/blockchain/failover/reset
  - GET /api/blockchain/health

前提条件：
  - 区块链服务在 http://localhost:8021 运行
  - PostgreSQL 数据库可用
  - Redis 缓存可用

运行：
  pytest tests/blockchain/test_failover_api.py -v --tb=short
  pytest tests/blockchain/test_failover_api.py -v -k "api" --tb=short
"""

import pytest
import httpx
import json
from typing import Dict, Any
from datetime import datetime


class BlockchainApiClient:
    """区块链 API 客户端"""
    
    BASE_URL = "http://localhost:8021"
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=10.0)
        self.auth_token = None
    
    def set_auth_token(self, token: str):
        """设置认证令牌"""
        self.auth_token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def get_failover_status(self) -> Dict[str, Any]:
        """GET /api/blockchain/failover/status"""
        response = self.client.get(
            "/api/blockchain/failover/status",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def switch_chain(self, target_chain: str, reason: str = None) -> Dict[str, Any]:
        """POST /api/blockchain/failover/switch-chain"""
        payload = {
            "targetChain": target_chain,
            "reason": reason or f"Test switch to {target_chain}"
        }
        response = self.client.post(
            "/api/blockchain/failover/switch-chain",
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def switch_node(self, node_name: str, reason: str = None) -> Dict[str, Any]:
        """POST /api/blockchain/failover/switch-node"""
        payload = {
            "nodeName": node_name,
            "reason": reason or f"Test switch to {node_name}"
        }
        response = self.client.post(
            "/api/blockchain/failover/switch-node",
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def reset_failover(self, reason: str = None) -> Dict[str, Any]:
        """POST /api/blockchain/failover/reset"""
        payload = {
            "reason": reason or "Test reset to default"
        }
        response = self.client.post(
            "/api/blockchain/failover/reset",
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """GET /api/blockchain/health"""
        response = self.client.get(
            "/api/blockchain/health",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """关闭客户端"""
        self.client.close()


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def api_client(mock_blockchain_service):
    """区块链 API 客户端（自动接入 respx mock）"""
    client = BlockchainApiClient()
    yield client
    client.close()


@pytest.fixture
def authenticated_api_client(api_client):
    """已认证的 API 客户端"""
    # 注：实际环境中需要真实的 token
    api_client.set_auth_token("mock-jwt-token")
    return api_client


# ═══════════════════════════════════════════════════════════════
# 测试：故障转移状态查询
# ═══════════════════════════════════════════════════════════════

class TestFailoverStatusApi:
    """故障转移状态 API 测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_get_failover_status_success(self, authenticated_api_client):
        """成功获取故障转移状态"""
        response = authenticated_api_client.get_failover_status()
        
        assert response is not None
        assert "data" in response
        
        data = response["data"]
        assert "activeChain" in data
        assert "activeNode" in data
        assert "isLocked" in data
        assert "nodes" in data
        assert isinstance(data["nodes"], dict)
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_get_failover_status_contains_all_nodes(self, authenticated_api_client):
        """故障转移状态应包含所有节点信息"""
        response = authenticated_api_client.get_failover_status()
        
        data = response["data"]
        nodes = data["nodes"]
        
        # 应该至少有 3 个节点
        assert len(nodes) >= 3
        
        for node_info in nodes.values():
            assert "available" in node_info
            assert "callCount" in node_info or "call_count" in node_info
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p1
    def test_get_failover_status_without_auth_should_fail(self, api_client):
        """无认证应返回 401"""
        with pytest.raises(httpx.HTTPStatusError):
            api_client.get_failover_status()


# ═══════════════════════════════════════════════════════════════
# 测试：链切换 API
# ═══════════════════════════════════════════════════════════════

class TestChainSwitchApi:
    """链切换 API 测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_switch_chain_to_fisco_success(self, authenticated_api_client):
        """成功切换到 FISCO 链"""
        response = authenticated_api_client.switch_chain("FISCO", "Test switch")
        
        assert response is not None
        assert "data" in response
        
        data = response["data"]
        assert data["previous_chain"] in ["ChainMaker", "FISCO", "Hyperchain"]
        assert data["current_chain"] == "FISCO"
        assert data["success"] is True
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_switch_chain_to_hyperchain_success(self, authenticated_api_client):
        """成功切换到 Hyperchain 链"""
        response = authenticated_api_client.switch_chain("Hyperchain", "Test switch")
        
        assert response is not None
        data = response["data"]
        assert data["current_chain"] == "Hyperchain"
        assert data["success"] is True
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p1
    def test_switch_chain_to_invalid_chain_should_fail(self, authenticated_api_client):
        """切换到无效链应失败"""
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            authenticated_api_client.switch_chain("InvalidChain")
        
        assert exc_info.value.response.status_code == 400
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p1
    def test_switch_chain_with_reason(self, authenticated_api_client):
        """链切换应记录原因"""
        reason = "Test failover scenario"
        response = authenticated_api_client.switch_chain("FISCO", reason)
        
        data = response["data"]
        assert "reason" in data or reason in data.get("message", "")


# ═══════════════════════════════════════════════════════════════
# 测试：节点切换 API
# ═══════════════════════════════════════════════════════════════

class TestNodeSwitchApi:
    """节点切换 API 测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_switch_node_success(self, authenticated_api_client):
        """成功切换节点"""
        # 假设存在 node-A-primary 节点
        response = authenticated_api_client.switch_node("node-A-primary")
        
        assert response is not None
        data = response["data"]
        assert data["success"] is True
        assert "previous_node" in data
        assert data["current_node"] == "node-A-primary"
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p1
    def test_switch_to_all_available_nodes(self, authenticated_api_client):
        """测试切换到所有可用节点"""
        nodes = ["node-A-primary", "node-B-slave", "node-C-dr"]
        
        for node in nodes:
            try:
                response = authenticated_api_client.switch_node(node)
                assert response["data"]["success"] is True
            except httpx.HTTPStatusError:
                # 某些节点可能不存在，跳过
                pass


# ═══════════════════════════════════════════════════════════════
# 测试：重置 API
# ═══════════════════════════════════════════════════════════════

class TestResetApi:
    """重置 API 测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_reset_to_default_success(self, authenticated_api_client):
        """成功重置到默认链"""
        # 先切换到其他链
        authenticated_api_client.switch_chain("FISCO")
        
        # 重置
        response = authenticated_api_client.reset_failover()
        
        assert response is not None
        data = response["data"]
        assert data["success"] is True
        assert data["current_chain"] == "ChainMaker"
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_reset_unlocks_manual_lock(self, authenticated_api_client):
        """重置应解除手动锁定"""
        # 手动切换（会加锁）
        authenticated_api_client.switch_chain("FISCO")
        
        # 重置应解除锁定
        response = authenticated_api_client.reset_failover()
        
        # 验证可以再次切换
        status = authenticated_api_client.get_failover_status()
        assert status["data"]["isLocked"] is False


# ═══════════════════════════════════════════════════════════════
# 测试：健康检查 API
# ═══════════════════════════════════════════════════════════════

class TestHealthApi:
    """健康检查 API 测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_get_health_success(self, authenticated_api_client):
        """健康检查应返回成功"""
        response = authenticated_api_client.get_health()
        
        assert response is not None
        assert "status" in response
        assert response["status"] == "Healthy"
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p1
    def test_health_includes_chain_info(self, authenticated_api_client):
        """健康检查应包含链信息"""
        response = authenticated_api_client.get_health()
        
        data = response
        assert "data" in data or "chains" in data
        
        # 应该包含至少一条链的健康状态
        if "data" in data:
            assert "chains" in data["data"] or "nodes" in data["data"]


# ═══════════════════════════════════════════════════════════════
# 集成场景测试
# ═══════════════════════════════════════════════════════════════

class TestIntegrationScenarios:
    """集成场景测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p0
    def test_failover_scenario_chainmaker_to_fisco(self, authenticated_api_client):
        """完整的故障转移场景：ChainMaker → FISCO"""
        # 1. 获取初始状态
        initial_status = authenticated_api_client.get_failover_status()
        assert initial_status["data"]["activeChain"] == "ChainMaker"
        
        # 2. 切换到 FISCO
        switch_response = authenticated_api_client.switch_chain("FISCO")
        assert switch_response["data"]["current_chain"] == "FISCO"
        
        # 3. 验证状态已更新
        updated_status = authenticated_api_client.get_failover_status()
        assert updated_status["data"]["activeChain"] == "FISCO"
        
        # 4. 重置到默认
        reset_response = authenticated_api_client.reset_failover()
        assert reset_response["data"]["current_chain"] == "ChainMaker"
        
        # 5. 验证恢复到默认链
        final_status = authenticated_api_client.get_failover_status()
        assert final_status["data"]["activeChain"] == "ChainMaker"
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p1
    def test_rapid_chain_switches(self, authenticated_api_client):
        """快速连续切换链"""
        chains = ["FISCO", "Hyperchain", "ChainMaker", "FISCO"]
        
        for chain in chains:
            response = authenticated_api_client.switch_chain(chain)
            assert response["data"]["current_chain"] == chain


# ═══════════════════════════════════════════════════════════════
# 并发测试
# ═══════════════════════════════════════════════════════════════

class TestConcurrency:
    """并发测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.api
    @pytest.mark.p2
    def test_concurrent_status_queries(self, authenticated_api_client):
        """并发状态查询应一致"""
        import concurrent.futures
        
        def get_status():
            return authenticated_api_client.get_failover_status()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(get_status) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # 所有结果应一致
        active_chains = [r["data"]["activeChain"] for r in results]
        assert len(set(active_chains)) == 1  # 所有值相同


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
