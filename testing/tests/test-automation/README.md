# 🚀 AIOPS 平台全自动化测试框架

> **最后更新**：2026-03-05
> **框架版本**：v1.0.0
> **覆盖范围**：API 测试 + 数据库验证 + 性能测试 + 多租户隔离测试

---

## 📋 框架概述

本自动化框架用于验证 AIOPS 平台的功能完整性、数据一致性、性能达成、安全合规等指标。

### 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **API 测试** | pytest + requests | 接口请求、响应验证、权限校验 |
| **数据库** | psycopg2 + SQL | 数据库查询、多租户隔离验证、软删除验证 |
| **性能测试** | k6 (JavaScript) | 压力测试、并发模拟、性能基线采集 |
| **报告** | pytest-html + allure | HTML 测试报告、CI/CD 集成 |

### 目录结构

```
test-automation/
├── README.md                      ← 本文件
├── requirements.txt               ← Python 依赖
├── config.json                    ← 环境配置
├── conftest.py                    ← pytest 全局配置
│
├── tests/                         ← 测试用例（Python）
│   ├── __init__.py
│   ├── test_auth.py               ← 认证模块测试
│   ├── test_tenant.py             ← 租户管理测试
│   ├── test_permission.py         ← 权限系统测试
│   ├── test_charging.py           ← 充电管理测试
│   ├── test_station.py            ← 场站管理测试
│   ├── test_device.py             ← 设备管理测试
│   ├── test_workorder.py          ← 工单管理测试
│   ├── test_settlement.py         ← 结算管理测试
│   └── test_ruleengine.py         ← 规则引擎测试
│
├── db_validators/                 ← 数据库验证脚本
│   ├── __init__.py
│   ├── tenant_isolation.py        ← 多租户隔离验证
│   ├── soft_delete.py             ← 软删除验证
│   ├── data_consistency.py        ← 数据一致性验证
│   └── audit_fields.py            ← 审计字段验证
│
├── helpers/                       ← 通用工具库
│   ├── __init__.py
│   ├── api_client.py              ← HTTP 客户端
│   ├── db_client.py               ← 数据库客户端
│   ├── data_factory.py            ← 测试数据生成
│   └── assertions.py              ← 断言库（备留，功能已合并）
│
├── k6-scripts/                    ← 性能测试脚本（JavaScript）
│   ├── charging-load-test.js      ← 充电 API 压测
│   ├── multi-tenant-load-test.js  ← 多租户并发压测
│   └── e2e-scenario-test.js       ← E2E 场景压测
│
└── docs/                          ← 文档
    ├── setup.md                   ← 环境搭建指南
    ├── run-tests.md               ← 执行命令参考
    └── best-practices.md          ← 最佳实践
```

---

## 🔧 快速开始（5 分钟）

### 1️⃣ 环境准备

```bash
# 1. 进入项目目录
cd d:\2026\aiops.v2

# 2. 启动基础设施（Docker）
docker-compose -f docker/docker-compose.infrastructure.yml up -d

# 3. 执行数据库迁移
pwsh scripts/init-databases.ps1

# 4. 启动后端服务（全量部署）
pwsh scripts/deploy-all.ps1

# 5. 编译前端
cd JGSY.AGI.Frontend && npm install && npm start

# 验证：访问 http://localhost:8080，能看见登陆页
```

### 2️⃣ 安装测试依赖

```bash
cd tests/test-automation

# 创建虚拟环境（可选，推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 3️⃣ 修改配置

编辑 `config.json`，确保数据库连接信息正确：

```json
{
  "test_environment": {
    "api_base_url": "http://localhost:8000/api"
  },
  "database": {
    "account": {
      "host": "localhost",
      "port": 5432,
      "database": "jgsy_account",
      "user": "postgres",
      "password": "postgres"
    }
  }
}
```

### 4️⃣ 运行测试

```bash
# 运行所有认证模块测试
pytest tests/test_auth.py -v

# 运行特定测试用例
pytest tests/test_auth.py::TestAuthLogin::test_AUTH_LOGIN_001_正常账号密码登陆 -v

# 显示打印输出
pytest tests/test_auth.py -v -s

# 生成 HTML 报告
pytest tests/test_auth.py -v --html=../test-results/report.html

# 显示最慢的 10 个测试
pytest tests/test_auth.py --durations=10
```

### 5️⃣ 查看报告

打开 `tests/test-results/report.html`，查看测试结果详情。

---

## 📖 详细使用指南

### API 测试

#### 示例 1：简单的 API 测试

```python
# tests/test_charging.py

from helpers.api_client import ApiClient
from helpers.data_factory import TestDataFactory, AssertionHelper

def test_get_charging_orders(api_client, auth_token):
    """获取充电订单列表"""
    # 执行请求
    resp = api_client.get('charging/orders?page=1&pageSize=20')
    
    # 断言
    assert resp.status_code == 200
    AssertionHelper.assert_api_success(resp.body)
    
    data = resp.body.get('data', {})
    orders = data.get('items', [])
    
    # 断言多租户隔离
    tenant_id = 'xxx'  # 当前用户的租户 ID
    AssertionHelper.assert_tenant_isolation(orders, tenant_id)
    
    # 断言软删除
    AssertionHelper.assert_soft_delete_compliance(orders)
```

#### 示例 2：CRUD 操作测试

```python
def test_crud_station(api_client, auth_token, db_client):
    """场站 CRUD 测试"""
    # 1. CREATE - 新增
    station_data = TestDataFactory.generate_station_data()
    resp = api_client.post('station/lists', json_data=station_data)
    assert resp.status_code == 201
    station_id = resp.body['data']['id']
    
    # 2. READ - 查询
    resp = api_client.get(f'station/lists/{station_id}')
    assert resp.status_code == 200
    assert resp.body['data']['id'] == station_id
    
    # 3. UPDATE - 修改
    update_data = {'name': '修改后的场站名'}
    resp = api_client.put(f'station/lists/{station_id}', json_data=update_data)
    assert resp.status_code == 200
    
    # 4. DELETE - 删除（软删除）
    resp = api_client.delete(f'station/lists/{station_id}')
    assert resp.status_code == 204
    
    # 5. 验证数据库软删除
    results = db_client.execute_query(
        "SELECT delete_at FROM station.station_list WHERE id = %s",
        (station_id,)
    )
    assert len(results) == 1
    assert results[0]['delete_at'] is not None
```

### 数据库验证

#### 示例 3：多租户隔离验证

```python
# db_validators/tenant_isolation.py

from helpers.db_client import DbClient, MultiTenantValidator

def test_multi_tenant_isolation():
    """验证数据库层面的多租户隔离"""
    db = DbClient(
        host='localhost', port=5432,
        database='jgsy_account',
        user='postgres', password='postgres'
    )
    db.connect()
    
    validator = MultiTenantValidator(db)
    
    # 检查是否有表缺少 tenant_id
    missing = validator.find_missing_tenant_id_columns()
    for item in missing:
        print(f"⚠️ {item['schema']}.{item['table']}: {item['reason']}")
    
    assert len(missing) == 0, f"发现 {len(missing)} 个缺少 tenant_id 的表"
    
    db.close()
```

#### 示例 4：软删除验证

```python
from db_validators.soft_delete import SoftDeleteValidator

def test_soft_delete_compliance():
    """验证软删除规范"""
    db = DbClient(...)
    db.connect()
    
    validator = SoftDeleteValidator(db)
    
    # 检查是否有表缺少 delete_at
    missing = validator.find_missing_delete_at_columns()
    assert len(missing) == 0
    
    # 验证已删除的记录被排除
    assert validator.verify_deleted_records_excluded('account', 'account_user')
    
    db.close()
```

### 性能测试（k6）

#### 示例 5：压力测试

```javascript
// k6-scripts/charging-load-test.js

import http from 'k6/http';
import { check, group, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up - 2分钟内到达100用户
    { duration: '5m', target: 100 },  // Stay at 100 users for 5 minutes
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 for 5 minutes
    { duration: '2m', target: 0 },    // Ramp down - 降低到0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% 请求 < 500ms，99% < 1000ms
    http_req_failed: ['rate<0.001'],                 // 错误率 < 0.1%
  },
};

export default function () {
  group('Charging Orders API', () => {
    let res = http.get('http://localhost:8000/api/charging/orders?page=1&pageSize=20', {
      headers: {
        'Authorization': `Bearer ${__ENV.TOKEN}`,
        'Content-Type': 'application/json',
      },
    });

    check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 500ms': (r) => r.timings.duration < 500,
      'has data': (r) => JSON.parse(r.body).data !== undefined,
    });
  });

  sleep(1);
}
```

执行：

```bash
# 先获取 Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/account/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' \
  | jq -r '.data.accessToken')

# 运行 k6 压测
k6 run k6-scripts/charging-load-test.js --env TOKEN=$TOKEN
```

---

## 🎯 测试场景覆盖

### Level 1：页面级功能（L1）

| 模块 | 测试文件 | 用例数 | 优先级 |
|------|---------|--------|-------|
| 用户认证 | `test_auth.py` | 12 | P0 |
| 租户管理 | `test_tenant.py` | 10 | P0 |
| 权限系统 | `test_permission.py` | 15 | P0 |
| 充电管理 | `test_charging.py` | 11 | P0 |
| 场站管理 | `test_station.py` | 9 | P0 |
| 设备管理 | `test_device.py` | 8 | P0 |
| 工单管理 | `test_workorder.py` | 10 | P0 |
| 结算管理 | `test_settlement.py` | 7 | P0 |
| 规则引擎 | `test_ruleengine.py` | 8 | P0 |

### Level 2：子系统集成（L2）

跨服务协联测试，如：站点创建 → 设备注册 → 费率配置 → 充电开始 → 结算生成

### Level 3：平台综合（L3）

E2E 场景、性能、安全、多租户压力测试

### 数据库验证（DB）

- 多租户隔离（tenant_id 覆盖 100%）
- 软删除合规（delete_at 覆盖 100%）
- 数据一致性（无孤儿数据）
- 审计字段完整

---

## 📊 测试报告

### 自动生成的报告

```
tests/test-results/
├── report.html              ← pytest HTML 报告（含详细失败信息）
├── coverage/                ← 代码覆盖率报告
│   └── index.html
├── performance.json         ← k6 性能指标（JSON）
└── test-execution.log       ← 完整运行日志
```

### 样本报告内容

```
=============== 测试执行摘要 ===============
平台用户认证模块 - 2026-03-05 14:32

用例总数：12
✅ 通过：11
❌ 失败：1
⏭️  跳过：0
⏰ 耗时：45.23 秒

失败用例：
  ❌ test_AUTH_LOGIN_006_连续失败锁定
     文件：tests/test_auth.py:256
     错误：AssertionError: 预期锁定时间戳不为 NULL
     
性能：
  平均响应：142ms ✅
  P99 响应：654ms ✅
```

---

## 🔍 常见问题与故障排除

### Q1：运行测试时 API 返回 401 Unauthorized

**原因**：Token 无效或过期

**解决**：
```python
# 确保 auth_token fixture 被正确使用
def test_something(api_client, auth_token):
    # auth_token 会自动设置到 api_client
    resp = api_client.get('some/endpoint')
```

### Q2：数据库连接超时

**原因**：PostgreSQL 未启动或网络问题

**解决**：
```bash
# 验证 PostgreSQL 是否运行
docker ps | grep postgres

# 验证连接
psql -h localhost -U postgres -d postgres -c "SELECT 1;"

# 修改 config.json 中的数据库地址
```

### Q3：某个测试总是失败，怀疑是环境问题

**解决**：
1. 查看详细日志：`pytest test_file.py -v -s`
2. 查看 API 响应：`pytest test_file.py -v --tb=long`
3. 查看数据库状态：`SELECT * FROM table_name LIMIT 5;`

### Q4：性能测试 (k6) 报错：无法获取 Token

**原因**：登陆接口变更或密码不对

**解决**：
```bash
# 手动测试登陆
curl -X POST http://localhost:8000/api/account/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' | jq .

# 复制 accessToken，手动设置到 k6 脚本
```

---

## 🏃 完整执行流程

### 日常开发（开发者）

```bash
# 在提交 PR 前运行一下快速检查
pytest tests/test_auth.py -v -k "P0" --tb=short
```

### 功能测试（测试人员）

```bash
# 日常运行完整的测试套件
pytest tests/ -v --html=../test-results/report-$(date +%Y%m%d-%H%M%S).html

# 专项验证（如多租户隔离）
pytest tests/ -v -k "multi_tenant"
```

### 发布前（QA Lead）

```bash
# 运行完整的 L1 + L2 + L3 + 数据库验证
pytest tests/ -v --cov=helpers --cov-report=html
k6 run k6-scripts/charging-load-test.js --env TOKEN=$TOKEN

# 生成最终报告
python scripts/generate-final-report.py
```

---

## 📚 扩展与最佳实践

### 如何添加新的测试用例

1. **在对应的 `test_*.py` 文件中添加**

```python
class TestNewFeature:
    def test_新功能_场景描述(self, api_client, auth_token):
        """
        用例编号：NEW-001
        描述：...
        """
        # 测试代码
```

2. **使用 TestDataFactory 生成测试数据**

```python
data = TestDataFactory.generate_charging_order_data(
    charged_energy_kwh=10.5,
    total_amount_yuan=50.0
)
```

3. **使用 AssertionHelper 进行断言**

```python
AssertionHelper.assert_tenant_isolation(results, tenant_id)
AssertionHelper.assert_soft_delete_compliance(results)
AssertionHelper.assert_response_time(resp.elapsed_ms, max_ms=500)
```

### 最佳实践

1. **用例名称格式**：`test_{模块}_{操作}_{场景}`
2. **每个测试要独立**：不依赖其他测试的执行结果
3. **使用 fixture 管理资源**：数据库连接、Token、测试数据
4. **断言要清晰**：失败时能快速定位问题
5. **性能测试要隔离**：不与功能测试混在一起
6. **数据要自动清理**：用完即删，不留污染数据

---

## 🔗 相关文档

- [环境搭建详细指南](docs/setup.md)
- [所有执行命令参考](docs/run-tests.md)
- [测试最佳实践](docs/best-practices.md)
- [性能测试详解](docs/performance-testing.md)

---

## 👥 支持与反馈

如有问题，请：
1. 查看本 README 的"常见问题"部分
2. 查看测试日志（`test-execution.log`）
3. 提交 Issue 或联系测试团队

---

**最后更新**：2026-03-05 | **下一版本**：v1.1.0（计划增加 GraphQL 测试、WebSocket 测试）
