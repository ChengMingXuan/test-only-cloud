import pytest
import json
import os
from pathlib import Path

# 读取配置文件
CONFIG_FILE = Path(__file__).parent / 'config.json'

def load_config():
    """加载 config.json"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"配置文件不存在: {CONFIG_FILE}")

# 全局配置
CONFIG = load_config()

# 导入测试工具
from helpers.api_client import ApiClient

# 检测测试模式
TEST_MODE = os.getenv("JGSY_TEST_MODE", "mock").lower()  # mock | container | real
USE_TESTCONTAINERS = TEST_MODE == "container"
USE_REAL_DB = TEST_MODE == "real"  # 仅冒烟检查可用
USE_MOCK = TEST_MODE == "mock" or (not USE_TESTCONTAINERS and not USE_REAL_DB)

# ==================== pytest hooks ====================

def pytest_configure(config):
    """pytest 启动时的初始化"""
    print("\n" + "="*70)
    print("  🚀 AIOPS 平台自动化测试框架 v2.0")
    print("="*70)
    print(f"  API 地址：{CONFIG['test_environment']['api_base_url']}")
    print(f"  测试模式：{TEST_MODE.upper()}")
    if USE_MOCK:
        print("  数据库：Mock 模式（不连接真实数据库）")
    elif USE_TESTCONTAINERS:
        print("  数据库：Testcontainers（真实 PostgreSQL 容器）")
    elif USE_REAL_DB:
        print("  数据库：真实库（仅限冒烟检查）")
    print("="*70 + "\n")

def pytest_collection_modifyitems(config, items):
    """在收集测试用例后修改（如添加标签）"""
    for item in items:
        # 根据文件名自动标记
        if 'test_auth' in item.nodeid:
            item.add_marker(pytest.mark.auth)
        elif 'test_charging' in item.nodeid:
            item.add_marker(pytest.mark.charging)
        elif 'test_tenant' in item.nodeid:
            item.add_marker(pytest.mark.tenant)

# ==================== Session 级别 Fixture ====================

@pytest.fixture(scope="session")
def test_config():
    """提供全局配置"""
    return CONFIG

@pytest.fixture(scope="session")
def api_client(test_config):
    """
    创建 API 客户端（会话级别）
    所有测试共用一个实例
    """
    client = ApiClient(
        base_url=test_config['test_environment']['api_base_url'],
        timeout=test_config['test_environment']['timeout_seconds']
    )
    yield client
    # 说实话，HTTP Client 没什么需要清理的

@pytest.fixture(scope="session")
def db_client(test_config):
    """
    数据库客户端（会话级别）
    
    根据 JGSY_TEST_MODE 环境变量选择模式：
    - mock：使用 Mock 客户端（默认，不连接数据库）
    - container：使用 Testcontainers（真实 PostgreSQL 容器）
    - real：使用真实数据库（仅限冒烟检查）
    """
    if USE_MOCK:
        # Mock 模式：不连接任何数据库
        from helpers.db_container import MockDbClient
        print("📦 使用 Mock 数据库客户端")
        yield MockDbClient()
        return
    
    if USE_TESTCONTAINERS:
        # Testcontainers 模式：启动真实 PostgreSQL 容器
        try:
            from helpers.db_container import PostgresTestContainer
            print("🐳 启动 Testcontainers PostgreSQL...")
            container = PostgresTestContainer()
            container.start()
            
            # 返回容器包装的客户端
            class ContainerDbClient:
                def __init__(self, pg_container):
                    self._container = pg_container
                    self._conn = None
                
                def connect(self):
                    self._conn = self._container.get_connection()
                
                def execute_query(self, sql, params=None):
                    from psycopg2.extras import RealDictCursor
                    if not self._conn:
                        self.connect()
                    cursor = self._conn.cursor(cursor_factory=RealDictCursor)
                    try:
                        cursor.execute(sql, params or ())
                        return [dict(row) for row in cursor.fetchall()]
                    finally:
                        cursor.close()
                
                def execute_scalar(self, sql, params=None):
                    results = self.execute_query(sql, params)
                    if results:
                        return list(results[0].values())[0]
                    return None
                
                def execute_update(self, sql, params=None):
                    if not self._conn:
                        self.connect()
                    cursor = self._conn.cursor()
                    try:
                        cursor.execute(sql, params or ())
                        self._conn.commit()
                        return cursor.rowcount
                    except Exception as e:
                        self._conn.rollback()
                        raise
                    finally:
                        cursor.close()
                
                def close(self):
                    if self._conn:
                        self._conn.close()
            
            client = ContainerDbClient(container)
            yield client
            client.close()
            container.stop()
            return
        except ImportError as e:
            pytest.fail(f"Testcontainers 不可用: {e}")
    
    if USE_REAL_DB:
        # 真实数据库模式：仅限冒烟检查
        print("⚠️ 警告：使用真实数据库，仅限冒烟检查")
        from helpers.db_client import DbClient
        db_config = test_config['database']['account']
        db = DbClient(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        try:
            db.connect()
        except Exception as e:
            pytest.fail(f"无法连接数据库: {str(e)}")
        
        yield db
        db.close()

# ==================== 函数级别 Fixture ====================

@pytest.fixture
def auth_token(api_client, test_config):
    """
    获取测试 Token（函数级别）
    每个测试都会获取一个新的 Token
    """
    test_account = test_config['test_accounts']['superadmin']
    
    resp = api_client.post('account/auth/login', json_data={
        'username': test_account['username'],
        'password': test_account['password']
    })
    
    if resp.status_code != 200:
        pytest.fail(f"登陆失败: {resp.body}")
    
    data = resp.body.get('data', {})
    token = data.get('accessToken')
    
    if not token:
        pytest.fail(f"未返回 Token: {resp.body}")
    
    # 自动设置到 API 客户端
    api_client.set_auth(token)
    
    return token

@pytest.fixture
def tenant_admin_token(api_client, test_config):
    """
    获取租户管理员 Token
    """
    test_account = test_config['test_accounts']['tenant_admin']
    
    resp = api_client.post('account/auth/login', json_data={
        'username': test_account['username'],
        'password': test_account['password']
    })
    
    if resp.status_code != 200:
        pytest.fail(f"租户管理员登陆失败: {resp.body}")
    
    token = resp.body.get('data', {}).get('accessToken')
    api_client.set_auth(token)
    
    return token

# ==================== 命令行选项 ====================

def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--api-url",
        action="store",
        default=None,
        help="覆盖 config.json 中的 API 地址"
    )
    parser.addoption(
        "--db-host",
        action="store",
        default=None,
        help="覆盖 config.json 中的数据库主机"
    )
    parser.addoption(
        "--skip-db",
        action="store_true",
        help="跳过数据库相关的测试"
    )
    parser.addoption(
        "--test-mode",
        action="store",
        default="mock",
        choices=["mock", "container", "real"],
        help="测试模式: mock(默认/不连库) | container(Testcontainers) | real(真实库/仅冒烟)"
    )

def pytest_configure(config):
    """在配置阶段读取命令行选项并更新 CONFIG"""
    # 使用 known_args_namespace 避免 getoption 在 configure 阶段报错
    try:
        if config.getoption("--api-url", default=None):
            CONFIG['test_environment']['api_base_url'] = config.getoption("--api-url")
        if config.getoption("--db-host", default=None):
            CONFIG['database']['account']['host'] = config.getoption("--db-host")
    except (ValueError, AttributeError):
        pass

# ==================== 标记定义 ====================

def _configure_markers_reference(config):
    """定义自定义标记（已在 pytest.ini 中统一定义，此函数保留备份）"""
    config.addinivalue_line(
        "markers", 
        "auth: 用户认证模块"
    )
    config.addinivalue_line(
        "markers", 
        "tenant: 租户管理模块"
    )
    config.addinivalue_line(
        "markers", 
        "charging: 充电管理模块"
    )
    config.addinivalue_line(
        "markers", 
        "performance: 性能测试"
    )
    config.addinivalue_line(
        "markers", 
        "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", 
        "slow: 执行时间长的测试"
    )

# ==================== 报告钩子 ====================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """为每个测试用例生成报告"""
    outcome = yield
    rep = outcome.get_result()
    
    # 在测试失败时打印更多信息
    if rep.failed and hasattr(item, 'funcargs'):
        # 可以在这里添加自定义的失败信息
        pass

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """在测试运行结束后打印总结"""
    terminalreporter.write_sep("=", "✅ 测试运行完毕", green=True)

# ==================== 初始化 helper 模块 ====================

# pytest_plugins 必须是列表，不能是函数
pytest_plugins = []  # helpers 模块按需在各测试文件中导入

# ==================== pytest.ini 配置替代 ====================

# 如果没有 pytest.ini，这里的设置会生效
pytest.ini_content = """
[pytest]
# 测试文件模式
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 标记定义
markers =
    auth: 用户认证模块
    tenant: 租户管理模块
    charging: 充电管理模块
    performance: 性能测试
    integration: 集成测试
    slow: 执行时间长的测试

# 超时
timeout = 60

# 输出
addopts = 
    --strict-markers
    --tb=short
    -ra

# 日志
log_cli = false
log_cli_level = INFO
log_file = test-execution.log
log_file_level = DEBUG

# 覆盖率
testpaths = tests
"""

# ==================== 辅助函数 ====================

def get_db_client_for_database(database_name: str):
    """
    获取指定数据库的 DB 客户端
    
    根据 TEST_MODE 返回不同类型的客户端：
    - mock：返回 MockDbClient
    - container/real：返回真实 DbClient
    
    用例：
        db = get_db_client_for_database('charging')
        results = db.execute_query('SELECT * FROM charging_order LIMIT 5')
    """
    if USE_MOCK:
        from helpers.db_container import MockDbClient
        return MockDbClient()
    
    if database_name not in CONFIG['database']:
        raise ValueError(f"未知的数据库: {database_name}")
    
    from helpers.db_client import DbClient
    db_config = CONFIG['database'][database_name]
    db = DbClient(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['user'],
        password=db_config['password']
    )
    
    db.connect()
    return db

# ==================== 调试 ====================

if __name__ == '__main__':
    print("conftest.py 已加载")
    print(f"配置文件: {CONFIG_FILE}")
    print(f"API 地址: {CONFIG['test_environment']['api_base_url']}")
