"""
Testcontainers 数据库基础设施
============================
使用真实 PostgreSQL 容器，保证测试效果 100% 与生产一致。

核心原则：
- 禁止连接生产/开发真实库
- 使用独立测试容器
- 每条用例自动清理
- 测试数据通过代码构造

使用方式：
```python
@pytest.fixture(scope="session")
def postgres():
    with PostgresTestContainer() as pg:
        yield pg

@pytest.fixture
def db_conn(postgres):
    conn = postgres.get_connection()
    yield conn
    conn.rollback()  # 自动回滚
    conn.close()
```
"""
import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# 尝试导入 testcontainers，如果没有则提供 fallback
try:
    from testcontainers.postgres import PostgresContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False
    logger.warning("testcontainers 未安装，将使用 Mock 模式")

# 尝试导入 psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 未安装")


class PostgresTestContainer:
    """
    PostgreSQL 测试容器封装
    
    特点：
    - 使用真实 PostgreSQL（与生产 100% 兼容）
    - 自动启动/停止容器
    - 支持 Schema 初始化
    - 每个测试用例可独立回滚
    """
    
    DEFAULT_IMAGE = "postgres:15-alpine"
    DEFAULT_DB = "test_db"
    DEFAULT_USER = "test"
    DEFAULT_PASSWORD = "test"
    
    def __init__(
        self,
        image: str = None,
        database: str = None,
        user: str = None,
        password: str = None,
        init_scripts: List[str] = None
    ):
        """
        初始化测试容器配置
        
        Args:
            image: PostgreSQL 镜像（默认 postgres:15-alpine）
            database: 数据库名（默认 test_db）
            user: 用户名（默认 test）
            password: 密码（默认 test）
            init_scripts: 初始化 SQL 脚本路径列表
        """
        self.image = image or self.DEFAULT_IMAGE
        self.database = database or self.DEFAULT_DB
        self.user = user or self.DEFAULT_USER
        self.password = password or self.DEFAULT_PASSWORD
        self.init_scripts = init_scripts or []
        
        self._container = None
        self._connection_url = None
    
    def start(self):
        """启动容器"""
        if not TESTCONTAINERS_AVAILABLE:
            raise RuntimeError(
                "testcontainers 未安装。请运行: pip install testcontainers testcontainers-postgres"
            )
        
        logger.info(f"🐳 启动 PostgreSQL 测试容器: {self.image}")
        
        self._container = PostgresContainer(
            image=self.image,
            username=self.user,
            password=self.password,
            dbname=self.database
        )
        self._container.start()
        
        self._connection_url = self._container.get_connection_url()
        logger.info(f"✅ 容器启动成功: {self._connection_url}")
        
        # 执行初始化脚本
        self._run_init_scripts()
        
        return self
    
    def stop(self):
        """停止容器"""
        if self._container:
            logger.info("🛑 停止 PostgreSQL 测试容器")
            self._container.stop()
            self._container = None
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    @property
    def connection_url(self) -> str:
        """获取连接 URL（SQLAlchemy 格式）"""
        if not self._connection_url:
            raise RuntimeError("容器未启动")
        return self._connection_url
    
    def get_connection(self):
        """获取 psycopg2 连接"""
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 未安装")
        
        if not self._container:
            raise RuntimeError("容器未启动")
        
        return psycopg2.connect(
            host=self._container.get_container_host_ip(),
            port=self._container.get_exposed_port(5432),
            database=self.database,
            user=self.user,
            password=self.password
        )
    
    def get_connection_params(self) -> Dict[str, Any]:
        """获取连接参数字典"""
        if not self._container:
            raise RuntimeError("容器未启动")
        
        return {
            "host": self._container.get_container_host_ip(),
            "port": self._container.get_exposed_port(5432),
            "database": self.database,
            "user": self.user,
            "password": self.password
        }
    
    def _run_init_scripts(self):
        """执行初始化脚本"""
        if not self.init_scripts:
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for script_path in self.init_scripts:
                if os.path.exists(script_path):
                    logger.info(f"📜 执行初始化脚本: {script_path}")
                    with open(script_path, 'r', encoding='utf-8') as f:
                        sql = f.read()
                    cursor.execute(sql)
                else:
                    logger.warning(f"⚠️ 脚本不存在: {script_path}")
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def execute_sql(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行 SQL 并返回结果"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute(sql, params or ())
            if cursor.description:
                return [dict(row) for row in cursor.fetchall()]
            conn.commit()
            return []
        finally:
            cursor.close()
            conn.close()
    
    def reset_database(self):
        """重置数据库（清空所有表数据）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 获取所有用户表
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' AND tablename NOT LIKE 'pg_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                # 禁用外键检查并清空
                cursor.execute("SET session_replication_role = 'replica';")
                for table in tables:
                    cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
                cursor.execute("SET session_replication_role = 'origin';")
                
            conn.commit()
            logger.info(f"🧹 已清空 {len(tables)} 张表")
        finally:
            cursor.close()
            conn.close()


class MockDbClient:
    """
    Mock 数据库客户端（无容器时使用）
    
    用于纯业务逻辑测试，不涉及真实数据库操作。
    """
    
    def __init__(self):
        self._data = {}  # 内存存储
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """模拟查询（返回空结果）"""
        return []
    
    def execute_scalar(self, sql: str, params: tuple = None) -> Any:
        """模拟标量查询"""
        return None
    
    def execute_update(self, sql: str, params: tuple = None) -> int:
        """模拟更新"""
        return 0
    
    def close(self):
        """关闭连接（无操作）"""
        pass
    
    def connect(self):
        """建立连接（无操作）"""
        pass


@contextmanager
def transactional_test(connection):
    """
    事务测试上下文管理器
    
    确保每个测试用例在事务中执行，结束后自动回滚。
    
    使用方式：
    ```python
    def test_something(db_conn):
        with transactional_test(db_conn) as cursor:
            cursor.execute("INSERT INTO ...")
            # 测试断言
        # 自动回滚，不影响其他测试
    ```
    """
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    try:
        yield cursor
    finally:
        connection.rollback()
        cursor.close()


# ═══════════════════════════════════════════════════
# pytest Fixtures
# ═══════════════════════════════════════════════════

def create_postgres_fixture(scope: str = "session", init_scripts: List[str] = None):
    """
    工厂函数：创建 PostgreSQL 测试容器 fixture
    
    使用方式：
    ```python
    # conftest.py
    postgres = create_postgres_fixture(
        scope="session",
        init_scripts=["schema.sql", "seed.sql"]
    )
    ```
    """
    import pytest
    
    @pytest.fixture(scope=scope)
    def _postgres_fixture():
        if not TESTCONTAINERS_AVAILABLE:
            logger.warning("⚠️ Testcontainers 不可用，使用 Mock 模式")
            yield MockDbClient()
            return
        
        container = PostgresTestContainer(init_scripts=init_scripts)
        container.start()
        yield container
        container.stop()
    
    return _postgres_fixture


def create_db_connection_fixture(postgres_fixture_name: str = "postgres"):
    """
    工厂函数：创建数据库连接 fixture（每个测试用例独立）
    
    使用方式：
    ```python
    # conftest.py
    db_conn = create_db_connection_fixture("postgres")
    ```
    """
    import pytest
    
    @pytest.fixture
    def _db_conn_fixture(request):
        postgres = request.getfixturevalue(postgres_fixture_name)
        
        if isinstance(postgres, MockDbClient):
            yield postgres
            return
        
        conn = postgres.get_connection()
        yield conn
        conn.rollback()  # 自动回滚
        conn.close()
    
    return _db_conn_fixture
