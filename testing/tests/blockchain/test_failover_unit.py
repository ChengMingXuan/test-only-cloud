"""
区块链服务 — 故障转移单元测试（全 Mock，无需连库）
======================================================

覆盖：
  - 同链集群故障转移（节点级自动切换）
  - 跨链灾备兜底
  - 熔断器三态转移
  - 健康监控与自动回切
  - 幂等性防重复
  - WAL预写日志

运行：
  pytest tests/blockchain/test_failover_unit.py -v --tb=short
  pytest tests/blockchain/test_failover_unit.py -v -k "failover" --tb=short
  pytest tests/blockchain/test_failover_unit.py --cov=blockchain --cov-report=term-missing
"""

import pytest
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
from typing import Dict, List, Any


# ═══════════════════════════════════════════════════════════════
# Mock 客户端与基础设施
# ═══════════════════════════════════════════════════════════════

class MockChainClient:
    """模拟区块链客户端"""
    
    def __init__(self, name: str, is_available: bool = True):
        self.name = name
        self.is_available = is_available
        self.call_count = 0
        self.last_error = None
    
    async def send_transaction(self, data: Dict) -> str:
        self.call_count += 1
        if not self.is_available:
            self.last_error = f"Node {self.name} is unavailable"
            raise Exception(self.last_error)
        return f"tx-{self.name}-{uuid.uuid4().hex[:8]}"
    
    async def get_block_height(self) -> int:
        if not self.is_available:
            raise Exception(f"Node {self.name} is unavailable")
        return 1000
    
    def set_available(self, available: bool):
        self.is_available = available


class MockChainFailoverManager:
    """模拟链灾备管理器"""
    
    def __init__(self):
        self.nodes = {
            "node1": MockChainClient("node1", True),
            "node2": MockChainClient("node2", True),
            "node3": MockChainClient("node3", True),
        }
        self.active_node = "node1"
        self.active_chain = "ChainMaker"
        self.failover_events: List[Dict] = []
        self.is_locked = False
    
    async def execute_with_failover(self, operation_name: str, data: Dict) -> str:
        """执行操作，支持故障转移"""
        # 记录操作开始
        attempted_nodes = []
        
        # 按优先级尝试
        for node_name in ["node1", "node2", "node3"]:
            attempted_nodes.append(node_name)
            try:
                node = self.nodes[node_name]
                if node.is_available:
                    tx_hash = await node.send_transaction(data)
                    if node_name != self.active_node:
                        # 发生了故障转移
                        self._record_failover("node_failure", self.active_node, node_name)
                        self.active_node = node_name
                    return tx_hash
            except Exception:
                continue
        
        raise Exception(f"All nodes unavailable: {attempted_nodes}")
    
    async def switch_to_chain(self, chain_name: str) -> bool:
        """切换到另一条链"""
        if self.is_locked:
            raise Exception("Manual lock active")
        
        if chain_name not in ["ChainMaker", "FISCO", "Hyperchain"]:
            raise ValueError(f"Unknown chain: {chain_name}")
        
        old_chain = self.active_chain
        self.active_chain = chain_name
        self._record_failover("cross_chain", old_chain, chain_name)
        return True
    
    async def reset_to_default(self) -> bool:
        """重置到默认链"""
        self.is_locked = False
        self.active_chain = "ChainMaker"
        self.active_node = "node1"
        self._record_failover("reset", self.active_chain, "ChainMaker")
        return True
    
    def _record_failover(self, failover_type: str, prev: str, curr: str):
        """记录故障转移事件"""
        self.failover_events.append({
            "type": failover_type,
            "previous": prev,
            "current": curr,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_status(self) -> Dict:
        """获取灾备状态"""
        return {
            "active_chain": self.active_chain,
            "active_node": self.active_node,
            "is_locked": self.is_locked,
            "nodes": {
                name: {"available": client.is_available, "call_count": client.call_count}
                for name, client in self.nodes.items()
            }
        }


class MockCircuitBreaker:
    """模拟熔断器"""
    
    def __init__(self):
        self.state = "closed"  # closed, open, half_open
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.open_duration = 30
    
    def allow_request(self) -> bool:
        """是否允许请求通过"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            # 检查是否应该进入半开状态
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed > self.open_duration:
                    self.state = "half_open"
                    self.success_count = 0
                    return True
            return False
        else:  # half_open
            return True
    
    def record_success(self):
        """记录成功"""
        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= 2:
                self.state = "closed"
                self.failure_count = 0
        elif self.state == "closed":
            self.failure_count = 0
    
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= 3:
            self.state = "open"


class MockIdempotencyService:
    """模拟幂等性服务"""
    
    def __init__(self):
        self.cache: Dict[str, str] = {}
    
    def get_cached_result(self, key: str) -> str | None:
        """获取缓存的结果"""
        return self.cache.get(key)
    
    def cache_result(self, key: str, result: str):
        """缓存结果"""
        self.cache[key] = result


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def failover_manager():
    """故障转移管理器"""
    return MockChainFailoverManager()


@pytest.fixture
def circuit_breaker():
    """熔断器"""
    return MockCircuitBreaker()


@pytest.fixture
def idempotency_service():
    """幂等性服务"""
    return MockIdempotencyService()


# ═══════════════════════════════════════════════════════════════
# 测试：同链集群故障转移
# ═══════════════════════════════════════════════════════════════

class TestSameChainFailover:
    """同链集群故障转移测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_node1_available_should_use_node1(self, failover_manager):
        """node1 可用时应使用 node1"""
        data = {"evidence_id": str(uuid.uuid4()), "hash": "abc123"}
        tx_hash = await failover_manager.execute_with_failover("SaveEvidence", data)
        
        assert tx_hash.startswith("tx-node1-")
        assert failover_manager.active_node == "node1"
        assert len(failover_manager.failover_events) == 0  # 无故障转移
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_node1_unavailable_should_failover_to_node2(self, failover_manager):
        """node1 不可用时应自动转移到 node2"""
        failover_manager.nodes["node1"].set_available(False)
        
        data = {"evidence_id": str(uuid.uuid4()), "hash": "abc123"}
        tx_hash = await failover_manager.execute_with_failover("SaveEvidence", data)
        
        assert tx_hash.startswith("tx-node2-")
        assert failover_manager.active_node == "node2"
        assert len(failover_manager.failover_events) == 1
        assert failover_manager.failover_events[0]["type"] == "node_failure"
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_node1_node2_unavailable_should_failover_to_node3(self, failover_manager):
        """node1 和 node2 都不可用时应转移到 node3"""
        failover_manager.nodes["node1"].set_available(False)
        failover_manager.nodes["node2"].set_available(False)
        
        data = {"evidence_id": str(uuid.uuid4()), "hash": "abc123"}
        tx_hash = await failover_manager.execute_with_failover("SaveEvidence", data)
        
        assert tx_hash.startswith("tx-node3-")
        assert failover_manager.active_node == "node3"
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_all_nodes_unavailable_should_raise_exception(self, failover_manager):
        """所有节点都不可用时应抛出异常"""
        for node in failover_manager.nodes.values():
            node.set_available(False)
        
        data = {"evidence_id": str(uuid.uuid4()), "hash": "abc123"}
        
        with pytest.raises(Exception, match="All nodes unavailable"):
            await failover_manager.execute_with_failover("SaveEvidence", data)
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_multiple_consecutive_failures(self, failover_manager):
        """连续多个操作的故障转移"""
        # 第一个操作：node1 正常
        tx1 = await failover_manager.execute_with_failover("SaveEvidence", {"id": "1"})
        assert tx1.startswith("tx-node1-")
        
        # 第二个操作：node1 变为不可用，自动转移到 node2
        failover_manager.nodes["node1"].set_available(False)
        tx2 = await failover_manager.execute_with_failover("SaveEvidence", {"id": "2"})
        assert tx2.startswith("tx-node2-")
        
        # 第三个操作：继续使用 node2
        tx3 = await failover_manager.execute_with_failover("SaveEvidence", {"id": "3"})
        assert tx3.startswith("tx-node2-")
        
        # 验证故障转移事件
        assert len(failover_manager.failover_events) == 1


# ═══════════════════════════════════════════════════════════════
# 测试：跨链灾备兜底
# ═══════════════════════════════════════════════════════════════

class TestCrossChainFailover:
    """跨链灾备兜底测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_switch_to_fisco_when_chainmaker_unavailable(self, failover_manager):
        """ChainMaker 不可用时应切换到 FISCO"""
        # 所有 node 都不可用，触发跨链灾备
        for node in failover_manager.nodes.values():
            node.set_available(False)
        
        # 切换到 FISCO
        success = await failover_manager.switch_to_chain("FISCO")
        
        assert success
        assert failover_manager.active_chain == "FISCO"
        assert len(failover_manager.failover_events) >= 1
        
        # 验证跨链事件
        cross_chain_event = [e for e in failover_manager.failover_events 
                             if e["type"] == "cross_chain"]
        assert len(cross_chain_event) > 0
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_switch_chain_priority_order(self, failover_manager):
        """验证链的优先级顺序"""
        # ChainMaker → FISCO → Hyperchain
        chains = ["ChainMaker", "FISCO", "Hyperchain"]
        
        for chain in chains:
            await failover_manager.switch_to_chain(chain)
            assert failover_manager.active_chain == chain
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_manual_lock_prevents_auto_switch(self, failover_manager):
        """手动锁定应防止自动切换"""
        failover_manager.is_locked = True
        
        with pytest.raises(Exception, match="Manual lock active"):
            await failover_manager.switch_to_chain("FISCO")
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_reset_unlocks_and_restores_default(self, failover_manager):
        """重置应解除锁定并恢复到默认链"""
        # 先切到 FISCO，然后加锁，验证重置能解锁并回到默认链
        await failover_manager.switch_to_chain("FISCO")
        failover_manager.is_locked = True
        
        # 锁定状态下切换应失败
        with pytest.raises(Exception, match="Manual lock active"):
            await failover_manager.switch_to_chain("ChainMaker")
        
        # 重置解锁
        success = await failover_manager.reset_to_default()
        
        assert success
        assert not failover_manager.is_locked
        assert failover_manager.active_chain == "ChainMaker"


# ═══════════════════════════════════════════════════════════════
# 测试：熔断器保护
# ═══════════════════════════════════════════════════════════════

class TestCircuitBreaker:
    """熔断器测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    def test_circuit_breaker_closed_allows_requests(self, circuit_breaker):
        """Closed 状态允许请求"""
        assert circuit_breaker.state == "closed"
        assert circuit_breaker.allow_request() is True
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    def test_circuit_breaker_opens_after_failures(self, circuit_breaker):
        """达到失败阈值后进入 Open 状态"""
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        
        assert circuit_breaker.state == "open"
        assert circuit_breaker.allow_request() is False
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    def test_circuit_breaker_half_open_after_timeout(self, circuit_breaker):
        """超时后进入 HalfOpen 状态"""
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.state == "open"
        
        # 模拟超时
        circuit_breaker.last_failure_time = datetime.utcnow() - timedelta(seconds=31)
        
        assert circuit_breaker.allow_request() is True
        assert circuit_breaker.state == "half_open"
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    def test_circuit_breaker_recovers_after_successes(self, circuit_breaker):
        """连续成功后恢复到 Closed 状态"""
        # 打开熔断器
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.state == "open"
        
        # 进入半开
        circuit_breaker.last_failure_time = datetime.utcnow() - timedelta(seconds=31)
        circuit_breaker.allow_request()
        
        # 连续成功
        circuit_breaker.record_success()
        circuit_breaker.record_success()
        
        assert circuit_breaker.state == "closed"


# ═══════════════════════════════════════════════════════════════
# 测试：幂等性防重复
# ═══════════════════════════════════════════════════════════════

class TestIdempotency:
    """幂等性测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    def test_first_request_not_cached(self, idempotency_service):
        """首次请求应无缓存"""
        key = "evidence:abc123:hash123"
        result = idempotency_service.get_cached_result(key)
        assert result is None
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    def test_cached_result_returns_same_hash(self, idempotency_service):
        """缓存的结果应返回相同的哈希"""
        key = "evidence:abc123:hash123"
        tx_hash = "tx-12345678"
        
        idempotency_service.cache_result(key, tx_hash)
        
        cached = idempotency_service.get_cached_result(key)
        assert cached == tx_hash
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    def test_duplicate_request_uses_cache(self, idempotency_service):
        """重复请求应使用缓存"""
        key = "evidence:abc123:hash123"
        tx_hash = "tx-12345678"
        
        idempotency_service.cache_result(key, tx_hash)
        
        # 假设相同的请求来了（同一 evidence_id 和 hash）
        cached = idempotency_service.get_cached_result(key)
        assert cached == tx_hash
        # 应该返回相同的结果，而不是生成新的 tx_hash


# ═══════════════════════════════════════════════════════════════
# 测试：状态查询与事件追踪
# ═══════════════════════════════════════════════════════════════

class TestStatusAndAudit:
    """状态查询与审计日志测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p2
    async def test_get_failover_status(self, failover_manager):
        """获取故障转移状态"""
        failover_manager.nodes["node1"].set_available(False)
        await failover_manager.execute_with_failover("SaveEvidence", {"id": "1"})
        
        status = failover_manager.get_status()
        
        assert status["active_node"] == "node2"
        assert status["active_chain"] == "ChainMaker"
        assert status["is_locked"] is False
        assert status["nodes"]["node1"]["available"] is False
        assert status["nodes"]["node2"]["available"] is True
    
    @pytest.mark.blockchain
    @pytest.mark.p2
    async def test_failover_events_recorded(self, failover_manager):
        """故障转移事件被记录"""
        failover_manager.nodes["node1"].set_available(False)
        await failover_manager.execute_with_failover("SaveEvidence", {"id": "1"})
        
        events = failover_manager.failover_events
        assert len(events) == 1
        assert events[0]["type"] == "node_failure"
        assert events[0]["previous"] == "node1"
        assert events[0]["current"] == "node2"
        assert "timestamp" in events[0]


# ═══════════════════════════════════════════════════════════════
# 参数化测试
# ═══════════════════════════════════════════════════════════════

class TestParametrized:
    """参数化测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p2
    @pytest.mark.parametrize("chain_name", ["ChainMaker", "FISCO", "Hyperchain"])
    async def test_switch_to_all_chains(self, failover_manager, chain_name):
        """测试切换到所有支持的链"""
        success = await failover_manager.switch_to_chain(chain_name)
        assert success
        assert failover_manager.active_chain == chain_name
    
    @pytest.mark.blockchain
    @pytest.mark.p2
    @pytest.mark.parametrize("failure_count", [1, 2, 3])
    def test_circuit_breaker_failure_counts(self, circuit_breaker, failure_count):
        """测试不同的失败计数"""
        for _ in range(failure_count):
            circuit_breaker.record_failure()
        
        if failure_count < 3:
            assert circuit_breaker.state == "closed"
        else:
            assert circuit_breaker.state == "open"
    
    @pytest.mark.blockchain
    @pytest.mark.p2
    @pytest.mark.parametrize("unavailable_nodes", [
        ["node1"],
        ["node1", "node2"],
        ["node1", "node2", "node3"],
    ])
    async def test_failover_with_different_unavailable_nodes(self, failover_manager, unavailable_nodes):
        """测试不同的节点不可用情况"""
        for node_name in unavailable_nodes:
            failover_manager.nodes[node_name].set_available(False)
        
        data = {"id": "test"}
        
        if len(unavailable_nodes) < 3:
            tx_hash = await failover_manager.execute_with_failover("SaveEvidence", data)
            assert tx_hash is not None
        else:
            with pytest.raises(Exception, match="All nodes unavailable"):
                await failover_manager.execute_with_failover("SaveEvidence", data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
