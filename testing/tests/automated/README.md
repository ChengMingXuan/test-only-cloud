# AIOPS v2.0 全面自动化测试套件

> 覆盖 31 个微服务、280+ 控制器、1370+ API 端点

## 目录结构

```
tests/automated/
├── config.py                # 统一配置（自动读取 docker/services.json）
├── conftest.py              # 全局 Fixture（ApiClient / DbClient / 验证器）
├── pytest.ini               # pytest 配置与标记
├── requirements.txt         # Python 依赖
├── test_01_smoke.py         # 烟雾测试 — 服务可达性、网关代理、响应结构
├── test_02_auth.py          # 认证鉴权 — 登录、Token、权限
├── test_03_crud.py          # CRUD 全模块 — 13 个业务模块的增删改查
├── test_04_business.py      # 业务逻辑 — 14 个领域的状态机与流程
├── test_05_tenant.py        # 多租户隔离 — 数据隔离、跨租户阻断、DB 级验证
├── test_06_security.py      # 安全边界 — SQL 注入 / XSS / 路径遍历 / 边界值
└── test_07_integration.py   # 跨服务集成 — 端到端链路、数据一致性
```

## 快速开始

```powershell
# 1. 确保基础设施已启动
# （PostgreSQL / Redis / Consul / 所有微服务）

# 2. 安装依赖
pip install -r tests/automated/requirements.txt

# 3. 运行烟雾测试（快速验证）
.\tests\run-automated-tests.ps1 -Mode smoke

# 4. 运行全量测试
.\tests\run-automated-tests.ps1 -Mode full

# 5. 生成 HTML 报告
.\tests\run-automated-tests.ps1 -Mode full -Html
```

## 运行模式

| 模式 | 覆盖范围 | 预估用时 | 命令 |
|------|---------|---------|------|
| smoke | P0 烟雾测试 | ~2 分钟 | `-Mode smoke` |
| core | 烟雾 + 认证 + CRUD | ~5 分钟 | `-Mode core` |
| security | 安全 + 边界 | ~5 分钟 | `-Mode security` |
| tenant | 多租户隔离 | ~3 分钟 | `-Mode tenant` |
| integration | 跨服务集成 | ~5 分钟 | `-Mode integration` |
| full | 全量测试 | ~15 分钟 | `-Mode full` |

## 直接用 pytest

```bash
# 按标记运行
pytest tests/automated/ -m "smoke"
pytest tests/automated/ -m "p0 and not db_verify"
pytest tests/automated/ -m "security or boundary"

# 按文件运行
pytest tests/automated/test_01_smoke.py -v
pytest tests/automated/test_03_crud.py -v

# 并行运行
pytest tests/automated/ -n auto

# 生成报告
pytest tests/automated/ --junitxml=TestResults/report.xml --html=TestResults/report.html
```

## 测试标记 (Markers)

| 标记 | 说明 |
|------|------|
| `smoke` | 烟雾测试 |
| `auth` | 认证鉴权 |
| `crud` | CRUD 增删改查 |
| `business` | 业务逻辑 |
| `tenant` | 多租户 |
| `security` | 安全测试 |
| `boundary` | 边界值 |
| `query` | 查询组合 |
| `integration` | 跨服务集成 |
| `db_verify` | 需要数据库连接 |
| `p0` | 最高优先级（阻断性） |
| `p1` | 高优先级 |
| `p2` | 普通优先级 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `JGSY_GATEWAY_URL` | `http://localhost:5000` | 网关地址 |
| `JGSY_DB_HOST` | `localhost` | 数据库地址 |
| `JGSY_DB_PORT` | `5432` | 数据库端口 |
| `JGSY_DB_USER` | `postgres` | 数据库用户 |
| `JGSY_DB_PASSWORD` | `P@ssw0rd` | 数据库密码 |

## 测试用例统计

| 文件 | 测试类 | 用例数（含参数化） |
|------|--------|-------------------|
| test_01_smoke | 5 | 100+ |
| test_02_auth | 5 | 20+ |
| test_03_crud | 2 | 100+ |
| test_04_business | 14 | 70+ |
| test_05_tenant | 4 | 15+ |
| test_06_security | 7 | 60+ |
| test_07_integration | 8 | 30+ |
| **合计** | **45** | **400+** |

## 设计原则

1. **零硬编码** — 所有服务地址、端口从 `docker/services.json` 自动读取
2. **参数化覆盖** — 通过 `SERVICE_API_REGISTRY` 和 `CRUD_MODULES` 自动铺展测试用例
3. **CI/CD 就绪** — 支持 JUnit XML / HTML 报告，可直接集成到 Jenkins / GitHub Actions
4. **数据自清理** — `cleanup` fixture 自动清理测试创建的数据
5. **环境隔离** — 所有配置可通过环境变量覆盖
