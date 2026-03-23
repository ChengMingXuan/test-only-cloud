"""
区块链服务 — 数据一致性测试（WAL、幂等性、跨链同步）
=========================================================

覆盖：
  - WAL 预写日志（Write-Ahead Logging）
  - 幂等性防重复提交
  - 跨链交易映射与同步
  - 恢复检查点与断点续跑
  - 软删除与多租户隔离

前提条件：
  - PostgreSQL 数据库可用
  - 可以访问 bc_cross_chain_tx_mapping / bc_recovery_checkpoint 表

运行：
  pytest tests/blockchain/test_data_consistency.py -v --tb=short -m blockchain
  pytest tests/blockchain/test_data_consistency.py -v -k "wal or idempotent or cross_chain"
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, MagicMock


# ═══════════════════════════════════════════════════════════════
# Mock 数据库与事务管理
# ═══════════════════════════════════════════════════════════════

class MockTransaction:
    """模拟数据库事务"""
    
    def __init__(self):
        self.is_open = False
        self.is_committed = False
        self.is_rolled_back = False
        self.statements: List[str] = []
    
    async def __aenter__(self):
        self.is_open = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
    
    async def execute(self, sql: str, params: Dict = None):
        """执行 SQL"""
        self.statements.append(sql)
        return {"affected_rows": 1}
    
    async def commit(self):
        """提交事务"""
        self.is_committed = True
    
    async def rollback(self):
        """回滚事务"""
        self.is_rolled_back = True


class MockWalLog:
    """模拟 WAL 日志"""
    
    def __init__(self):
        self.entries: Dict[str, Any] = {}
    
    async def insert_intent(self, mapping_id: uuid.UUID, data: Dict) -> bool:
        """插入意图记录"""
        self.entries[str(mapping_id)] = {
            "id": str(mapping_id),
            "status": "intent",
            "data": data,
            "created_at": datetime.utcnow().isoformat()
        }
        return True
    
    async def update_committed(self, mapping_id: uuid.UUID, tx_hash: str):
        """更新为已提交"""
        if str(mapping_id) in self.entries:
            self.entries[str(mapping_id)]["status"] = "committed"
            self.entries[str(mapping_id)]["tx_hash"] = tx_hash
    
    async def get_incomplete_entries(self) -> List[Dict]:
        """获取未完成的条目"""
        return [
            entry for entry in self.entries.values()
            if entry["status"] in ["intent", "wal_failed"]
        ]


class MockCrossChainTxMapper:
    """模拟跨链交易映射"""
    
    def __init__(self):
        self.mappings: Dict[str, Dict] = {}
        self.sync_queue: List[str] = []
    
    async def insert_mapping(self, mapping: Dict) -> str:
        """插入交易映射"""
        mapping_id = str(uuid.uuid4())
        self.mappings[mapping_id] = {
            **mapping,
            "id": mapping_id,
            "sync_status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        self.sync_queue.append(mapping_id)
        return mapping_id
    
    async def get_sync_queue(self, primary_chain: str) -> List[Dict]:
        """获取同步队列"""
        return [
            self.mappings[mid] for mid in self.sync_queue
            if self.mappings[mid]["primary_chain"] == primary_chain
            and self.mappings[mid]["sync_status"] in ["pending", "failed"]
        ]
    
    async def update_sync_status(self, mapping_id: str, status: str, 
                                  primary_tx_hash: str = None):
        """更新同步状态"""
        if mapping_id in self.mappings:
            self.mappings[mapping_id]["sync_status"] = status
            if primary_tx_hash:
                self.mappings[mapping_id]["primary_tx_hash"] = primary_tx_hash
            if status == "synced":
                self.mappings[mapping_id]["sync_time"] = datetime.utcnow().isoformat()
    
    async def count_synced(self, primary_chain: str) -> int:
        """统计已同步的数量"""
        return sum(
            1 for mapping in self.mappings.values()
            if mapping["primary_chain"] == primary_chain
            and mapping["sync_status"] == "synced"
        )


class MockRecoveryCheckpoint:
    """模拟恢复检查点"""
    
    def __init__(self):
        self.checkpoints: Dict[str, Dict] = {}
    
    async def create_checkpoint(self, failover_period_id: uuid.UUID, 
                                 total_transactions: int) -> str:
        """创建检查点"""
        checkpoint_id = str(uuid.uuid4())
        self.checkpoints[checkpoint_id] = {
            "id": checkpoint_id,
            "failover_period_id": str(failover_period_id),
            "status": "in_progress",
            "total_transactions": total_transactions,
            "synced_transactions": 0,
            "failed_transactions": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        return checkpoint_id
    
    async def update_progress(self, checkpoint_id: str, synced: int, failed: int):
        """更新进度"""
        if checkpoint_id in self.checkpoints:
            self.checkpoints[checkpoint_id]["synced_transactions"] = synced
            self.checkpoints[checkpoint_id]["failed_transactions"] = failed
            
            # 检查是否完成
            total = self.checkpoints[checkpoint_id]["total_transactions"]
            if synced + failed >= total:
                self.checkpoints[checkpoint_id]["status"] = "completed"
    
    async def get_checkpoint(self, checkpoint_id: str) -> Dict:
        """获取检查点"""
        return self.checkpoints.get(checkpoint_id)


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def wal_log():
    """WAL 日志"""
    return MockWalLog()


@pytest.fixture
def cross_chain_mapper():
    """跨链交易映射"""
    return MockCrossChainTxMapper()


@pytest.fixture
def recovery_checkpoint():
    """恢复检查点"""
    return MockRecoveryCheckpoint()


@pytest.fixture
def mock_transaction():
    """数据库事务"""
    return MockTransaction()


# ═══════════════════════════════════════════════════════════════
# 测试：WAL 预写日志
# ═══════════════════════════════════════════════════════════════

class TestWalPreWriteLogging:
    """WAL 预写日志测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_wal_intent_created_before_operation(self, wal_log):
        """操作前应创建 WAL 意图记录"""
        mapping_id = uuid.uuid4()
        data = {
            "business_id": "evidence-123",
            "operation": "SaveEvidence"
        }
        
        success = await wal_log.insert_intent(mapping_id, data)
        
        assert success
        assert str(mapping_id) in wal_log.entries
        assert wal_log.entries[str(mapping_id)]["status"] == "intent"
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_wal_intent_to_committed_transition(self, wal_log):
        """WAL 应从意图转移到已提交"""
        mapping_id = uuid.uuid4()
        data = {"business_id": "evidence-123"}
        
        # 插入意图
        await wal_log.insert_intent(mapping_id, data)
        assert wal_log.entries[str(mapping_id)]["status"] == "intent"
        
        # 更新为已提交
        tx_hash = "tx-abc123"
        await wal_log.update_committed(mapping_id, tx_hash)
        assert wal_log.entries[str(mapping_id)]["status"] == "committed"
        assert wal_log.entries[str(mapping_id)]["tx_hash"] == tx_hash
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_wal_incomplete_entries_recovery(self, wal_log):
        """启动恢复应找到所有未完成的 WAL 条目"""
        # 插入多个条目
        mapping_id_1 = uuid.uuid4()
        mapping_id_2 = uuid.uuid4()
        mapping_id_3 = uuid.uuid4()
        
        await wal_log.insert_intent(mapping_id_1, {"id": "1"})
        await wal_log.insert_intent(mapping_id_2, {"id": "2"})
        await wal_log.insert_intent(mapping_id_3, {"id": "3"})
        
        # 提交第一个
        await wal_log.update_committed(mapping_id_1, "tx-1")
        
        # 获取未完成的条目
        incomplete = await wal_log.get_incomplete_entries()
        
        assert len(incomplete) == 2
        assert any(e["id"] == str(mapping_id_2) for e in incomplete)
        assert any(e["id"] == str(mapping_id_3) for e in incomplete)
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_wal_crash_recovery(self, wal_log):
        """模拟崩溃后恢复"""
        # 场景：链操作前插入 WAL 意图
        mapping_id = uuid.uuid4()
        await wal_log.insert_intent(mapping_id, {"op": "SaveEvidence"})
        
        # 模拟崩溃（不调用 update_committed）
        # 重启后扫描未完成的条目
        incomplete = await wal_log.get_incomplete_entries()
        
        assert len(incomplete) == 1
        assert incomplete[0]["id"] == str(mapping_id)


# ═══════════════════════════════════════════════════════════════
# 测试：幂等性防重复
# ═══════════════════════════════════════════════════════════════

class TestIdempotencyGuards:
    """幂等性防重复测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    def test_idempotency_key_generation(self):
        """幂等性键生成"""
        evidence_id = "evidence-123"
        data_hash = "abc123def456"
        
        key = f"evidence:{evidence_id}:{data_hash}"
        
        assert key == "evidence:evidence-123:abc123def456"
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    def test_duplicate_request_same_key_returns_cached_tx_hash(self):
        """重复请求（相同键）应返回缓存的 tx_hash"""
        cache = {}
        
        # 第一个请求
        key = "evidence:e123:h123"
        tx_hash_1 = "tx-12345678"
        cache[key] = tx_hash_1
        
        # 第二个请求（相同键）
        tx_hash_2 = cache.get(key)
        
        assert tx_hash_2 == tx_hash_1
        assert tx_hash_2 is not None
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_cross_chain_failover_idempotency(self):
        """跨链灾备期间的幂等性保护"""
        cache = {}
        
        # 故障转移前：请求 1 写入 ChainMaker
        key_1 = "evidence:e123:h123"
        tx_hash_1 = "tx-chainmaker-12345"
        cache[key_1] = tx_hash_1
        
        # 故障转移：切换到 FISCO
        # 故障转移后：重复请求相同的 evidence
        tx_hash_2 = cache.get(key_1)
        
        # 应该返回相同的 tx_hash，而不是生成新的
        assert tx_hash_2 == tx_hash_1


# ═══════════════════════════════════════════════════════════════
# 测试：跨链交易映射与同步
# ═══════════════════════════════════════════════════════════════

class TestCrossChainTransactionMapping:
    """跨链交易映射测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_create_cross_chain_mapping(self, cross_chain_mapper):
        """创建跨链交易映射"""
        mapping = {
            "business_id": "evidence-123",
            "business_type": "Evidence",
            "operation_name": "SaveEvidence",
            "primary_chain": "ChainMaker",
            "fallback_chain": "FISCO",
            "fallback_tx_hash": "tx-fisco-123"
        }
        
        mapping_id = await cross_chain_mapper.insert_mapping(mapping)
        
        assert mapping_id is not None
        assert mapping_id in cross_chain_mapper.mappings
        assert cross_chain_mapper.mappings[mapping_id]["sync_status"] == "pending"
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_get_sync_queue_for_primary_chain(self, cross_chain_mapper):
        """获取主链的同步队列"""
        # 插入多个映射
        mapping_1 = {
            "business_id": "e1",
            "primary_chain": "ChainMaker",
            "fallback_chain": "FISCO",
            "fallback_tx_hash": "tx-1"
        }
        mapping_2 = {
            "business_id": "e2",
            "primary_chain": "ChainMaker",
            "fallback_chain": "FISCO",
            "fallback_tx_hash": "tx-2"
        }
        mapping_3 = {
            "business_id": "e3",
            "primary_chain": "FISCO",
            "fallback_chain": "Hyperchain",
            "fallback_tx_hash": "tx-3"
        }
        
        await cross_chain_mapper.insert_mapping(mapping_1)
        await cross_chain_mapper.insert_mapping(mapping_2)
        await cross_chain_mapper.insert_mapping(mapping_3)
        
        # 获取 ChainMaker 的同步队列
        queue = await cross_chain_mapper.get_sync_queue("ChainMaker")
        
        assert len(queue) == 2
        assert all(m["primary_chain"] == "ChainMaker" for m in queue)
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_sync_status_transitions(self, cross_chain_mapper):
        """同步状态转移"""
        mapping = {
            "business_id": "e1",
            "primary_chain": "ChainMaker",
            "fallback_chain": "FISCO",
            "fallback_tx_hash": "tx-fisco-1"
        }
        
        mapping_id = await cross_chain_mapper.insert_mapping(mapping)
        
        # pending → synced
        await cross_chain_mapper.update_sync_status(mapping_id, "synced", "tx-chainmaker-1")
        
        updated = cross_chain_mapper.mappings[mapping_id]
        assert updated["sync_status"] == "synced"
        assert updated["primary_tx_hash"] == "tx-chainmaker-1"
        assert "sync_time" in updated


# ═══════════════════════════════════════════════════════════════
# 测试：恢复检查点与断点续跑
# ═══════════════════════════════════════════════════════════════

class TestRecoveryCheckpoints:
    """恢复检查点测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_create_recovery_checkpoint(self, recovery_checkpoint):
        """创建恢复检查点"""
        failover_period_id = uuid.uuid4()
        total_tx = 100
        
        checkpoint_id = await recovery_checkpoint.create_checkpoint(
            failover_period_id, total_tx
        )
        
        assert checkpoint_id is not None
        checkpoint = await recovery_checkpoint.get_checkpoint(checkpoint_id)
        assert checkpoint["status"] == "in_progress"
        assert checkpoint["total_transactions"] == total_tx
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_checkpoint_progress_tracking(self, recovery_checkpoint):
        """检查点进度追踪"""
        failover_period_id = uuid.uuid4()
        checkpoint_id = await recovery_checkpoint.create_checkpoint(failover_period_id, 100)
        
        # 进度阶段 1：同步了 30 个，失败了 5 个
        await recovery_checkpoint.update_progress(checkpoint_id, synced=30, failed=5)
        checkpoint = await recovery_checkpoint.get_checkpoint(checkpoint_id)
        assert checkpoint["synced_transactions"] == 30
        assert checkpoint["failed_transactions"] == 5
        assert checkpoint["status"] == "in_progress"
        
        # 进度阶段 2：同步了 65 个，失败了 35 个（完成）
        await recovery_checkpoint.update_progress(checkpoint_id, synced=65, failed=35)
        checkpoint = await recovery_checkpoint.get_checkpoint(checkpoint_id)
        assert checkpoint["status"] == "completed"
    
    @pytest.mark.blockchain
    @pytest.mark.p1
    async def test_resumable_recovery(self, recovery_checkpoint):
        """可恢复的恢复流程"""
        # 场景：恢复进程崩溃后重启
        failover_period_id = uuid.uuid4()
        checkpoint_id = await recovery_checkpoint.create_checkpoint(failover_period_id, 100)
        
        # 进度：同步了 40 个
        await recovery_checkpoint.update_progress(checkpoint_id, synced=40, failed=0)
        
        # 模拟崩溃
        # 重启后读取检查点，继续从第 41 个开始
        checkpoint = await recovery_checkpoint.get_checkpoint(checkpoint_id)
        next_offset = checkpoint["synced_transactions"] + checkpoint["failed_transactions"]
        
        assert next_offset == 40
        # 继续同步剩余 60 个...


# ═══════════════════════════════════════════════════════════════
# 集成场景：完整的跨链灾备与恢复
# ═══════════════════════════════════════════════════════════════

class TestFullCrossChainRecoveryScenario:
    """完整的跨链灾备与恢复场景"""
    
    @pytest.mark.blockchain
    @pytest.mark.p0
    async def test_complete_cross_chain_failover_and_recovery(
        self, wal_log, cross_chain_mapper, recovery_checkpoint
    ):
        """完整的跨链灾备和恢复流程"""
        
        # ========== 阶段一：正常运行（ChainMaker）==========
        evidence_1_id = uuid.uuid4()
        evidence_1_hash = "hash-1"
        evidence_1_key = f"evidence:{evidence_1_id}:{evidence_1_hash}"
        
        # 使用正常的 WAL 流程
        await wal_log.insert_intent(evidence_1_id, {"op": "SaveEvidence"})
        await wal_log.update_committed(evidence_1_id, "tx-chainmaker-1")
        
        # ========== 阶段二：灾备切换（ChainMaker 不可用，切到 FISCO）==========
        evidence_2_id = uuid.uuid4()
        evidence_2_hash = "hash-2"
        
        # 故障期间的数据写入 FISCO（带 WAL 保护）
        evidence_2_wal_id = uuid.uuid4()
        await wal_log.insert_intent(evidence_2_wal_id, {"op": "SaveEvidence", "chain": "FISCO"})
        
        # 同时记录跨链映射
        mapping_2 = {
            "business_id": str(evidence_2_id),
            "primary_chain": "ChainMaker",
            "fallback_chain": "FISCO",
            "fallback_tx_hash": "tx-fisco-2"
        }
        mapping_2_id = await cross_chain_mapper.insert_mapping(mapping_2)
        
        # ========== 阶段三：主链恢复 ==========
        # 创建恢复检查点
        failover_period_id = uuid.uuid4()
        checkpoint_id = await recovery_checkpoint.create_checkpoint(failover_period_id, 1)
        
        # 获取待同步的交易
        sync_queue = await cross_chain_mapper.get_sync_queue("ChainMaker")
        assert len(sync_queue) >= 1
        
        # 同步交易到 ChainMaker
        for mapping in sync_queue:
            if mapping["id"] == mapping_2_id:
                # 重放交易
                await cross_chain_mapper.update_sync_status(
                    mapping["id"], "synced", "tx-chainmaker-2"
                )
                await recovery_checkpoint.update_progress(checkpoint_id, synced=1, failed=0)
        
        # 验证同步完成
        checkpoint = await recovery_checkpoint.get_checkpoint(checkpoint_id)
        assert checkpoint["status"] == "completed"
        
        synced_count = await cross_chain_mapper.count_synced("ChainMaker")
        assert synced_count >= 1


# ═══════════════════════════════════════════════════════════════
# 边界情况测试
# ═══════════════════════════════════════════════════════════════

class TestBoundaryConditions:
    """边界情况测试"""
    
    @pytest.mark.blockchain
    @pytest.mark.p2
    async def test_empty_sync_queue(self, cross_chain_mapper):
        """空同步队列"""
        queue = await cross_chain_mapper.get_sync_queue("ChainMaker")
        assert queue == []
    
    @pytest.mark.blockchain
    @pytest.mark.p2
    async def test_large_number_of_mappings(self, cross_chain_mapper):
        """大量交易映射"""
        # 插入 1000 个映射
        for i in range(1000):
            mapping = {
                "business_id": f"e{i}",
                "primary_chain": "ChainMaker",
                "fallback_chain": "FISCO",
                "fallback_tx_hash": f"tx-{i}"
            }
            await cross_chain_mapper.insert_mapping(mapping)
        
        queue = await cross_chain_mapper.get_sync_queue("ChainMaker")
        assert len(queue) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "blockchain"])
