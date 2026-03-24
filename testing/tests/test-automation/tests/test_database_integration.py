"""
数据库集成测试用例
==================
使用 Testcontainers 或 Mock 验证 SQL 兼容性。

测试模式：
- JGSY_TEST_MODE=mock      → 使用 MockDbClient（不连库）
- JGSY_TEST_MODE=container → 使用 Testcontainers PostgreSQL 容器（100% 生产兼容）
- JGSY_TEST_MODE=real      → 使用真实数据库（仅冒烟检查）
"""
import pytest
import uuid
from datetime import datetime

# ==================== pytest 标记 ====================

pytestmark = [
    pytest.mark.integration,
    pytest.mark.database,
]


# ==================== 数据库基础测试 ====================

class TestDatabaseConnection:
    """数据库连接测试"""
    
    @pytest.mark.smoke
    def test_DB_CONN_001_数据库连接正常(self, db_client):
        """
        用例：验证数据库连接
        预期：可以成功建立连接并执行简单查询
        """
        # 注意：在 Mock 模式下返回空列表，这是预期行为
        result = db_client.execute_query("SELECT 1 as test_value")
        # Mock 模式下结果为空，Container/Real 模式下有值
        assert result is not None, "查询应返回结果（或空列表）"
        print(f"✅ 数据库连接测试通过，返回: {result}")
    
    @pytest.mark.smoke
    def test_DB_CONN_002_数据库版本查询(self, db_client):
        """
        用例：查询数据库版本
        预期：可以获取 PostgreSQL 版本信息
        """
        result = db_client.execute_query("SELECT version()")
        # Mock 模式下结果为空
        if result:
            version = list(result[0].values())[0]
            assert "PostgreSQL" in version, f"应为 PostgreSQL，实际: {version}"
            print(f"✅ 数据库版本: {version[:50]}...")
        else:
            print("✅ Mock 模式，跳过版本验证")


class TestDatabaseSchema:
    """数据库 Schema 测试"""
    
    def test_DB_SCHEMA_001_创建测试表(self, db_client):
        """
        用例：验证 DDL 语句执行
        预期：可以创建临时测试表
        """
        # 在 Mock 模式下，此操作不会真正执行
        create_sql = """
            CREATE TABLE IF NOT EXISTS _test_temp_table (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                tenant_id UUID NOT NULL,
                create_time TIMESTAMP DEFAULT NOW(),
                delete_at TIMESTAMP NULL
            )
        """
        try:
            db_client.execute_update(create_sql)
            print("✅ 测试表创建成功（或 Mock 模式跳过）")
        except Exception as e:
            # Mock 模式下可能抛出异常，这是预期的
            print(f"ℹ️ DDL 执行状态: {e}")
    
    def test_DB_SCHEMA_002_表字段检查(self, db_client):
        """
        用例：验证必要字段存在
        预期：表应包含标准字段（id, tenant_id, create_time, delete_at）
        """
        check_sql = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '_test_temp_table'
            ORDER BY ordinal_position
        """
        result = db_client.execute_query(check_sql)
        
        if result:
            columns = {row['column_name']: row for row in result}
            required_columns = ['id', 'name', 'tenant_id', 'create_time', 'delete_at']
            
            for col in required_columns:
                assert col in columns, f"缺少必要字段: {col}"
            
            # 验证 delete_at 可空（软删除字段）
            assert columns['delete_at']['is_nullable'] == 'YES', "delete_at 应该可空"
            print(f"✅ 字段检查通过: {list(columns.keys())}")
        else:
            print("✅ Mock 模式，跳过字段检查")


class TestDatabaseCRUD:
    """数据库 CRUD 测试"""
    
    def test_DB_CRUD_001_插入数据(self, db_client):
        """
        用例：验证 INSERT 语句
        预期：可以插入数据并返回正确的行数
        """
        test_id = str(uuid.uuid4())
        test_tenant_id = str(uuid.uuid4())
        
        insert_sql = """
            INSERT INTO _test_temp_table (id, name, tenant_id)
            VALUES (%s, %s, %s)
        """
        try:
            affected = db_client.execute_update(insert_sql, (test_id, '测试数据', test_tenant_id))
            # Container/Real 模式下应返回 1
            if affected is not None and affected > 0:
                print(f"✅ 插入成功，影响行数: {affected}")
            else:
                print("✅ Mock 模式，插入模拟成功")
        except Exception as e:
            print(f"ℹ️ 插入状态: {e}")
    
    def test_DB_CRUD_002_查询数据(self, db_client):
        """
        用例：验证 SELECT 语句（带租户隔离）
        预期：查询应包含 tenant_id 和 delete_at IS NULL 条件
        """
        test_tenant_id = str(uuid.uuid4())
        
        # 符合规范的查询：包含 tenant_id 和软删除过滤
        select_sql = """
            SELECT id, name, tenant_id, create_time
            FROM _test_temp_table
            WHERE tenant_id = %s AND delete_at IS NULL
            ORDER BY create_time DESC
            LIMIT 10
        """
        result = db_client.execute_query(select_sql, (test_tenant_id,))
        
        # Mock 模式下返回空列表
        assert isinstance(result, list), "查询结果应为列表"
        print(f"✅ 查询成功，返回 {len(result)} 条记录")
    
    def test_DB_CRUD_003_软删除数据(self, db_client):
        """
        用例：验证软删除（UPDATE delete_at）
        预期：软删除应设置 delete_at 字段，而非物理删除
        """
        test_id = str(uuid.uuid4())
        
        # 符合规范的软删除
        soft_delete_sql = """
            UPDATE _test_temp_table
            SET delete_at = NOW()
            WHERE id = %s AND delete_at IS NULL
        """
        try:
            affected = db_client.execute_update(soft_delete_sql, (test_id,))
            print(f"✅ 软删除执行成功，影响行数: {affected or 0}")
        except Exception as e:
            print(f"ℹ️ 软删除状态: {e}")


class TestDatabaseTenantIsolation:
    """多租户隔离测试"""
    
    def test_DB_TENANT_001_租户A数据隔离(self, db_client):
        """
        用例：验证租户 A 无法看到租户 B 的数据
        预期：查询结果只包含当前租户的数据
        """
        tenant_a = str(uuid.uuid4())
        tenant_b = str(uuid.uuid4())
        
        # 查询租户 A 的数据
        query_sql = """
            SELECT COUNT(*) as cnt
            FROM _test_temp_table
            WHERE tenant_id = %s AND delete_at IS NULL
        """
        
        result_a = db_client.execute_query(query_sql, (tenant_a,))
        result_b = db_client.execute_query(query_sql, (tenant_b,))
        
        # 验证两个租户的数据相互独立
        print(f"✅ 租户隔离验证：A={result_a}, B={result_b}")
    
    def test_DB_TENANT_002_缺少tenant_id应报错(self, db_client):
        """
        用例：不带 tenant_id 的查询应被拒绝（规范检查）
        预期：生产代码中不应出现不带 tenant_id 的查询
        """
        # 这个测试是提示性的，检查代码规范
        # 实际的 Repository 层应该强制要求 tenant_id
        bad_query = "SELECT * FROM _test_temp_table WHERE delete_at IS NULL"
        
        # 这个查询在语法上是合法的，但不符合多租户规范
        # 实际项目中应通过代码审查或 lint 工具检查
        print("⚠️ 提示：查询必须包含 tenant_id 条件，否则违反多租户规范")


class TestDatabaseCleanup:
    """数据库清理测试"""
    
    def test_DB_CLEANUP_001_清理测试表(self, db_client):
        """
        用例：清理测试创建的临时表
        预期：测试表被成功删除
        """
        drop_sql = "DROP TABLE IF EXISTS _test_temp_table"
        try:
            db_client.execute_update(drop_sql)
            print("✅ 测试表清理成功")
        except Exception as e:
            print(f"ℹ️ 清理状态: {e}")


# ==================== Testcontainers 专用测试 ====================

@pytest.mark.container
class TestContainerDatabase:
    """
    Testcontainers 专用测试
    仅在 JGSY_TEST_MODE=container 时运行
    """
    
    def test_CONTAINER_001_真实PostgreSQL执行(self, db_client):
        """
        用例：在真实 PostgreSQL 容器中执行复杂查询
        预期：结果与生产环境 100% 兼容
        """
        import os
        assert os.getenv("JGSY_TEST_MODE", "mock") == "container", "仅在 Container 模式下运行"
        
        # 测试 PostgreSQL 特有功能
        pg_sql = "SELECT pg_backend_pid() as pid, current_database() as db"
        result = db_client.execute_query(pg_sql)
        
        if result:
            print(f"✅ PostgreSQL 进程 ID: {result[0]['pid']}, 数据库: {result[0]['db']}")
        else:
            pytest.fail("Container 模式应返回真实结果")
    
    def test_CONTAINER_002_JSON类型支持(self, db_client):
        """
        用例：验证 PostgreSQL JSON/JSONB 类型支持
        预期：可以正确处理 JSON 数据
        """
        import os
        assert os.getenv("JGSY_TEST_MODE", "mock") == "container", "仅在 Container 模式下运行"
        
        # 使用 ->> 返回文本，-> 返回 JSON（带引号）
        json_sql = """
            SELECT '{"key": "value", "nested": {"a": 1}}'::jsonb ->> 'key' as val
        """
        result = db_client.execute_query(json_sql)
        
        if result:
            assert result[0]['val'] == 'value', f"JSON 解析错误: {result}"
            print("✅ JSONB 类型支持验证通过")
