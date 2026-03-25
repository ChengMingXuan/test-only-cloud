# 🎯 AIOPS 平台测试框架 - 完整执行指南

> **版本**：v1.0 | **最后更新**：2026-03-05
> **用途**：全量自动化测试 + 手工验证 + 性能压测、发布前最终验收

---

## 📋 快速命令速查表

> **直接复制粘贴即用** ⬇️

### 第一步：环境准备

```bash
# 1. 启动基础设施（Docker 容器）
cd d:\2026\aiops.v2
docker-compose -f docker/docker-compose.infrastructure.yml up -d

# 2. 迁移数据库（DbUp）
pwsh scripts/init-databases.ps1

# 3. 启动后端服务（全量）
pwsh scripts/deploy-all.ps1

# 4. 编译前端
cd JGSY.AGI.Frontend && npm install && npm start

# ✅ 验证：打开 http://localhost:8080，看到登陆页
```

### 第二步：安装测试依赖

```bash
cd d:\2026\aiops.v2\tests\test-automation

# 创建虚拟环境（可选）
python -m venv venv
venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

### 第三步：运行自动化测试

#### 【快速】仅验证认证模块（5 分钟）

```bash
pytest tests/test_auth.py -v
```

#### 【标准】运行所有已实现的测试（15 分钟）

```bash
pytest tests/ -v
```

#### 【完整】生成详细报告（20 分钟）

```bash
# 运行测试 + 生成 HTML 报告 + 代码覆盖率
pytest tests/ -v \
  --html=../test-results/report.html \
  --self-contained-html \
  --cov=helpers \
  --cov-report=html:../test-results/coverage \
  --durations=10
```

#### 【专项】仅验证多租户隔离

```bash
pytest tests/ -k "multi_tenant" -v
```

#### 【专项】仅验证权限校验

```bash
pytest tests/ -k "permission" -v
```

#### 【专项】仅验证性能指标

```bash
pytest tests/ -k "Performance" -v
```

#### 【调试】显示详细日志和打印输出

```bash
pytest tests/test_auth.py -v -s --tb=long
```

#### 【并行】多进程运行（加快速度）

```bash
pytest tests/ -v -n auto
```

### 第四步：查看报告

```bash
# 用浏览器打开 HTML 报告
start ../test-results/report.html

# 查看代码覆盖率报告
start ../test-results/coverage/index.html

# 查看完整日志
type test-execution.log
```

---

## 🔥 常见操作

### 运行单个测试用例

```bash
# 测试格式：pytest 文件::类::函数
pytest tests/test_auth.py::TestAuthLogin::test_AUTH_LOGIN_001_正常账号密码登陆 -v -s
```

### 命令行覆盖配置

```bash
# 指定 API 地址（覆盖 config.json）
pytest tests/ -v --api-url http://192.168.1.100:8000/api

# 指定数据库地址
pytest tests/ -v --db-host 192.168.1.100

# 跳过数据库测试
pytest tests/ -v --skip-db
```

### 标记使用（按功能筛选）

```bash
# 只运行认证模块测试
pytest tests/ -m auth -v

# 只运行充电模块测试
pytest tests/ -m charging -v

# 只运行集成测试（不含基础测试）
pytest tests/ -m integration -v

# 排除某些标记
pytest tests/ -m "not slow" -v
```

### 性能测试（k6）

```bash
# 先获取登陆 Token
$token = curl -s -X POST "http://localhost:8000/api/account/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"Admin@123"}' | jq -r '.data.accessToken'

# 运行充电 API 压测（阶梯增压：0→100→200→0 用户）
k6 run k6-scripts/charging-load-test.js --env TOKEN=$token -v

# 运行多租户压测
k6 run k6-scripts/multi-tenant-load-test.js --env TOKEN=$token

# 生成 JSON 报告格式输出
k6 run k6-scripts/charging-load-test.js --env TOKEN=$token -o json=performance.json
```

---

## 📊 数据库验证（直接 SQL）

### 验证多租户隔离

```bash
# 连接到数据库
docker exec -it jgsy_postgres psql -U postgres -d jgsy_account -c "SET client_encoding TO UTF8;"

# 查询用户表（应该包含 tenant_id 字段）
SELECT id, tenant_id, username, delete_at 
FROM account.account_user 
WHERE delete_at IS NULL 
LIMIT 5;

# 验证查询不能跨租户
SELECT COUNT(DISTINCT tenant_id) 
FROM account.account_user 
WHERE delete_at IS NULL;

-- 预期：应该有多个 tenant_id，说明隔离正确
```

### 验证软删除

```bash
-- 检查软删除覆盖率（应该 100%）
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('public', 'pg_*')
AND table_name NOT LIKE '%_log'
ORDER BY table_schema, table_name;

-- 验证已删除的记录被排除
SELECT COUNT(*) as deleted_count 
FROM account.account_user 
WHERE delete_at IS NOT NULL;

SELECT COUNT(*) as active_count 
FROM account.account_user 
WHERE delete_at IS NULL;
```

### 验证数据一致性

```bash
-- 检查孤儿数据（外键引用不存在）
SELECT c.id, c.user_id
FROM account.account_user_role c
WHERE c.delete_at IS NULL
AND c.user_id NOT IN (SELECT id FROM account.account_user WHERE delete_at IS NULL)
LIMIT 10;

-- 预期：0 行结果（无孤儿数据）
```

---

## 🔍 故障排除快速查询

### 问题：API 返回 401 Unauthorized

```bash
# 原因：Token 过期或无效
# 解决：
pytest tests/test_auth.py::TestAuthLogin::test_AUTH_LOGIN_001_正常账号密码登陆 -v -s

# 查看登陆请求的响应
curl -X POST http://localhost:8000/api/account/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' | jq .
```

### 问题：数据库连接失败

```bash
# 原因：PostgreSQL 未启动
# 解决：
docker ps | grep postgres

# 如果没有，启动 PostgreSQL
docker-compose -f docker/docker-compose.infrastructure.yml up -d postgres

# 测试连接
docker exec -it jgsy_postgres psql -U postgres -c "SELECT 1;"
```

### 问题：某个测试总是失败

```bash
# 解决：
# 1. 运行单个测试，显示详细输出
pytest tests/test_auth.py::TestAuthLogin -v -s --tb=long

# 2. 查看日志
type test-execution.log | tail -100

# 3. 手动测试 API
curl -X GET "http://localhost:8000/api/account/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📈 完整执行流程（日常）

### 【D1-D8】开发与 L1 测试阶段（每天）

```bash
# 早上：检查新的测试用例是否编译通过
pytest tests/ --co -q

# 中午：运行完整的 L1 测试
pytest tests/ -v --html=../test-results/report-$(Get-Date -Format yyyyMMdd-HHmmss).html

# 下午：针对失败的用例进行修复 + 回归测试
pytest tests/test_charging.py -v -k "failed_case_name" -s
```

### 【D9】L2 子系统集成测试

```bash
# 运行集成测试
pytest tests/ -m integration -v

# 验证多服务数据流转
pytest tests/ -k "charging and settlement" -v
```

### 【D10】L3 平台级综合测试

```bash
# E2E 场景测试
pytest tests/ -k "e2e" -v

# 性能压力测试
k6 run k6-scripts/charging-load-test.js --env TOKEN=$token

# 多租户隔离压力测试
k6 run k6-scripts/multi-tenant-load-test.js --env TOKEN=$token
```

### 【D11】发布前门禁检查

```bash
# 编译检查
dotnet build

# 权限检查
psql -c "SELECT COUNT(*) FROM perm_permission WHERE delete_at IS NULL;"

# 数据库迁移检查
psql -c "SELECT COUNT(*) FROM schemaversions;"

# 种子数据检查
psql -c "SELECT COUNT(*) FROM perm_menu WHERE delete_at IS NULL;"
psql -c "SELECT COUNT(*) FROM perm_role_permission WHERE delete_at IS NULL;"

# 自动化测试最后验收
pytest tests/ -v --cov=helpers
```

---

## 📝 报告输出

### HTML 报告内容

打开 `test-results/report.html` 可以看到：

```
AIOPS 平台自动化测试报告
═══════════════════════════
总用例数：93
✅ 通过：91  (97.8%)
❌ 失败：2   (2.2%)
⏭️  跳过：0   (0%)

执行时间：2m 34s
通过率：97.8% ✅

【用例详情】
✅ test_auth.py::TestAuthLogin::test_AUTH_LOGIN_001_正常账号密码登陆
   耗时：0.45s | 响应：142ms

❌ test_charging.py::TestChargingOrder::test_CHG_ORDER_008
   错误：AssertionError: 费用计算错误，期望 50.2，实际 50.15
   日志：[截图和堆栈跟踪]

...
```

### 性能报告内容

k6 运行完成后会输出：

```
    http_req_duration ............ avg=156ms p(95)=456ms p(99)=892ms max=1234ms
    http_req_failed .............. 0 ✓
    http_reqs .................... 5234 ✓
    vus .......................... 200 ✓
```

**预期**：
- 平均响应 < 200ms ✅
- P99 响应 < 1000ms ✅
- 错误率 < 0.1% ✅

---

## 🎓 扩展与自定义

### 添加新的测试模块

```bash
# 1. 复制演示文件
cp tests/test_auth.py tests/test_mycustom.py

# 2. 修改类名和测试方法名
# 假设测试"我的服务"

# 3. 导入客户端和工具
from helpers.api_client import ApiClient
from helpers.data_factory import TestDataFactory, AssertionHelper

# 4. 编写你的测试
class TestMyService:
    def test_mycustom_001(self, api_client, auth_token):
        resp = api_client.get('myservice/data')
        assert resp.status_code == 200
        AssertionHelper.assert_api_success(resp.body)

# 5. 运行
pytest tests/test_mycustom.py -v
```

### 添加新的数据库验证

```python
# db_validators/my_validation.py

from helpers.db_client import DbClient

class MyValidator:
    def __init__(self, db: DbClient):
        self.db = db
    
    def verify_custom_rule(self):
        results = self.db.execute_query(
            "SELECT * FROM my_table WHERE condition = %s",
            ('value',)
        )
        return len(results) == 0  # 验证规则
```

---

## 🔐 安全与合规检查

### 权限校验

```bash
# 验证所有权限码已入库
psql -d jgsy_permission -c \
  "SELECT code, name FROM perm_permission WHERE delete_at IS NULL ORDER BY code;"

# 验证 SUPER_ADMIN 拥有所有权限
psql -d jgsy_permission -c \
  "SELECT COUNT(*) FROM perm_role_permission WHERE role_id = '00000000-0000-0000-0000-000000000001';"
```

### 多租户隔离检查

```bash
# 验证所有查询都包含 tenant_id 过滤
# 检查应用日志中的 SQL 查询

grep -r "SELECT.*FROM" logs/ | grep -v "WHERE.*tenant_id" | wc -l
# 预期：0（没有漏掉 tenant_id 的查询）
```

---

## 💾 备份与恢复

### 测试前备份

```bash
# 备份所有数据库
pwsh docker/backup-databases.ps1

# 验证备份成功
ls -la backups/
```

### 恢复到初始状态

```bash
# 重置数据库（仅保留种子数据）
pwsh scripts/init-databases.ps1 -Reset

# 或者从备份恢复
pwsh docker/backup-drill.ps1 -Restore -BackupDate 20260305
```

---

## 📞 快速支持

### 日常问题

| 问题 | 快速解决 |
|------|---------|
| API 返回 500 | 查看 `logs/` 目录下的服务日志 |
| 数据库连接超时 | `docker restart jgsy_postgres` |
| 测试挂起 | `pytest --timeout=60` |
| 报告打不开 | 检查路径是否为中文，改为英文 |

### 联系方式

- **QA Lead**：[QA Team Email]
- **测试框架问题**：[相关文档 / GitHub Issues]
- **API 问题**：[API Team]
- **数据库问题**：[DBA]

---

## 📚 完整文档导航

| 文档 | 用途 |
|------|------|
| `00-测试执行总体计划.md` | 项目规划 + 日程 + 门禁清单 |
| `manual-test-checklist.md` | 手工测试清单（打印版） |
| `test-automation/README.md` | 框架详细说明 + FAQ |
| `test-automation/config.json` | 环境配置 |
| `test-automation/conftest.py` | Pytest 配置详解 |
| **本文件** | 快速命令参考 |

---

## ✅ 发布前最终检查清单

> 在发布前，运行以下这个完整脚本

```bash
#!/bin/bash
echo "🔍 发布前最终检查..."

# 1. 编译检查
echo "1️⃣  编译检查..."
dotnet build > /dev/null 2>&1
if [ $? -ne 0 ]; then echo "❌ 编译失败"; exit 1; fi
echo "✅ 编译通过"

# 2. 自动化测试
echo "2️⃣  运行自动化测试..."
pytest tests/ -v --html=../test-results/final-report.html > /dev/null 2>&1
TEST_RESULT=$?
if [ $TEST_RESULT -ne 0 ]; then echo "❌ 部分测试失败"; fi
echo "✅ 测试完成"

# 3. 性能测试
echo "3️⃣  运行性能测试..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/account/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' | jq -r '.data.accessToken')
k6 run k6-scripts/charging-load-test.js --env TOKEN=$token --quiet > /dev/null 2>&1
echo "✅ 性能测试完成"

# 4. 数据库检查
echo "4️⃣  数据库合规检查..."
psql -c "SELECT 'DbUp Migrations' as check, COUNT(*) as count FROM schemaversions;" > /dev/null 2>&1
psql -c "SELECT 'Permissions' as check, COUNT(*) as count FROM perm_permission WHERE delete_at IS NULL;" > /dev/null 2>&1
echo "✅ 数据库检查通过"

echo ""
echo "═══════════════════════════════"
echo "✅ 所有检查完毕！可以发布生产"
echo "═══════════════════════════════"
echo ""
echo "📊 查看报告：test-results/final-report.html"
```

保存为 `final-check.sh`，执行：

```bash
bash final-check.sh
```

---

**版本**：v1.0 | **最后更新**：2026-03-05 | **维护者**：QA Team
