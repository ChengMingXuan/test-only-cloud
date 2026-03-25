# VSCode 测试任务快速指南

> **版本**: v1.0  
> **日期**: 2026年3月5日  
> **位置**: `.vscode/tasks.json` 第⑭章节

---

## 🎯 快速使用

### 方式一：VSCode 命令面板
1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 `Tasks: Run Task`
3. 选择测试任务（带 🧪 🎨 ⚡ 🌐 🎭 🎯 🏆 图标）

### 方式二：VSCode 终端菜单
1. 菜单栏 -> **终端** -> **运行任务...**
2. 选择测试任务

### 方式三：快捷键（推荐配置）
在 `.vscode/keybindings.json` 中添加：
```json
[
  { "key": "ctrl+shift+t", "command": "workbench.action.tasks.runTask", "args": "🏆 一键全量测试（五工具组合）" },
  { "key": "ctrl+alt+t", "command": "workbench.action.tasks.runTask", "args": "⚡ 快速验证测试（pytest + Cypress）" }
]
```

---

## 📊 测试任务清单（9个）

### 🔹 独立工具任务（按测试金字塔层级）

| 序号 | 任务名称 | Label | 时长 | 说明 |
|------|---------|-------|------|------|
| 1️⃣ | **pytest API测试** | 🧪 pytest API测试（金字塔底层） | 10-15分钟 | API/数据库验证（80%+ 覆盖率，93个用例） |
| 2️⃣ | **Cypress 组件测试** | 🎨 Cypress 组件测试 | 5-10分钟 | 组件交互测试（40-50% 组件，快速反馈） |
| 3️⃣ | **Puppeteer 性能测试** | ⚡ Puppeteer 性能测试 | 10-15分钟 | Chrome深度性能分析（10-15% 页面，Core Web Vitals） |
| 4️⃣ | **Selenium 兼容性测试** | 🌐 Selenium 兼容性测试 | 30-60分钟 | 多浏览器矩阵测试（20-30% 页面，Chrome/Firefox/Edge） |
| 5️⃣ | **Playwright E2E测试** | 🎭 Playwright E2E测试 | 20-40分钟 | 跨浏览器E2E流程（60-70% 关键流程，Chromium/Firefox/WebKit） |
| 6️⃣ | **K6 负载压测** | 🎯 K6 负载压测（金字塔顶层） | 20-25分钟 | API端点负载测试（100% API，100-500并发） |

### 🔹 组合任务（一键执行）

| 序号 | 任务名称 | Label | 时长 | 说明 |
|------|---------|-------|------|------|
| 7️⃣ | **一键全量测试** | 🏆 一键全量测试（五工具组合） | 4-5小时 | 顺序执行全部6个工具 + 报告聚合 + 发布门禁 |
| 8️⃣ | **快速验证测试** | ⚡ 快速验证测试（pytest + Cypress） | ~20分钟 | 仅执行pytest + Cypress，本地开发快速反馈 |
| 9️⃣ | **并行全量测试** | 🔥 并行全量测试（快速模式） | 2-3小时 | 并行执行全部工具（需机器性能足够） |

---

## 🏆 测试金字塔层级说明

```
┌─────────────────────────────────────────────────────────┐
│                   测试金字塔（从底到顶）                   │
├─────────────────────────────────────────────────────────┤
│  ⑥ K6 负载压测 (100% API端点, 找性能瓶颈)                │ ← 顶层
├─────────────────────────────────────────────────────────┤
│  ⑤ Playwright E2E (60-70%关键流程, 跨浏览器)             │
├─────────────────────────────────────────────────────────┤
│  ④ Selenium兼容性 (20-30%页面, 多浏览器矩阵)             │
├─────────────────────────────────────────────────────────┤
│  ③ Puppeteer性能 (10-15%页面, Chrome深度分析)            │
├─────────────────────────────────────────────────────────┤
│  ② Cypress组件 (40-50%组件, 快速反馈)                    │
├─────────────────────────────────────────────────────────┤
│  ① pytest API (80%+ API, 数据库验证)                     │ ← 底层
└─────────────────────────────────────────────────────────┘
```

**原则**：
- **底层**（pytest）：执行最快、覆盖最广、反馈最早
- **中层**（Cypress/Puppeteer/Selenium）：针对性测试、补充覆盖
- **顶层**（Playwright E2E/K6）：端到端验证、性能压测

---

## 🚀 使用场景推荐

### 场景1：本地开发后快速验证（20分钟）
```
任务: ⚡ 快速验证测试（pytest + Cypress）
```
- **适用**：完成一个模块功能，需要快速验证API和关键组件
- **覆盖**：API测试 + 组件交互测试
- **优势**：快速反馈，早发现问题

### 场景2：功能分支合并前检查（1-2小时）
```
按顺序执行:
1. 🧪 pytest API测试
2. 🎨 Cypress 组件测试
3. 🎭 Playwright E2E测试
```
- **适用**：Pull Request 前验证
- **覆盖**：API + 组件 + E2E 关键流程
- **优势**：覆盖核心功能路径

### 场景3：发版前全量回归（4-5小时）
```
任务: 🏆 一键全量测试（五工具组合）
```
- **适用**：版本发布前的完整验证
- **覆盖**：全部6个工具 + 报告聚合
- **优势**：全面覆盖，生成发布门禁报告

### 场景4：夜间自动化回归（2-3小时）
```
任务: 🔥 并行全量测试（快速模式）
```
- **适用**：CI/CD 夜间自动任务
- **覆盖**：全部工具并行执行
- **优势**：节省时间，次日查看报告

### 场景5：性能基准测试（20-25分钟）
```
任务: 🎯 K6 负载压测（金字塔顶层）
```
- **适用**：验证系统性能指标
- **覆盖**：API负载测试（100-500并发）
- **优势**：找到性能瓶颈

### 场景6：浏览器兼容性验证（30-60分钟）
```
任务: 🌐 Selenium 兼容性测试
```
- **适用**：发版前验证多浏览器兼容性
- **覆盖**：Chrome/Firefox/Edge 矩阵测试
- **优势**：确保各浏览器正常运行

---

## 📋 首次使用检查清单

### ✅ 环境准备

- [ ] **Python 3.11+** 已安装（pytest/Selenium需要）
  ```powershell
  python --version
  ```

- [ ] **Node.js 18+** 已安装（Playwright/Cypress/Puppeteer需要）
  ```powershell
  node --version
  npm --version
  ```

- [ ] **K6** 已安装
  ```powershell
  # 方式1: Chocolatey
  choco install k6
  
  # 方式2: 手动下载
  # https://k6.io/docs/getting-started/installation/
  
  # 验证
  k6 version
  ```

- [ ] **Docker Desktop** 已运行（Selenium Grid需要）
  ```powershell
  docker ps
  ```

- [ ] **基础设施已启动**
  ```powershell
  # 执行VSCode任务: 🏗️ 启动基础设施
  ```

### ✅ 依赖安装

运行第一个测试任务时会自动安装依赖，或手动执行：

```powershell
# pytest
cd tests/test-automation
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Cypress
cd tests/cypress-tests
npm install

# Puppeteer
cd tests/puppeteer-tests
npm install

# Playwright
cd tests/playwright-tests
npm install
npx playwright install --with-deps

# Selenium
cd tests/selenium-tests
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 统一编排器
cd tests/test-orchestrator
npm install
```

---

## 🎯 任务执行顺序建议

### 金字塔顺序（推荐，早失败早反馈）

```
1️⃣ 🧪 pytest API测试         ← 最先执行（最快，最底层）
2️⃣ 🎨 Cypress 组件测试        ← 组件级验证
3️⃣ ⚡ Puppeteer 性能测试      ← 性能监控
4️⃣ 🌐 Selenium 兼容性测试     ← 浏览器兼容性
5️⃣ 🎭 Playwright E2E测试      ← 端到端流程
6️⃣ 🎯 K6 负载压测             ← 最后执行（压力测试）
```

**优势**：
- 底层测试失败 → 立即停止，节省时间
- 逐层验证 → 逻辑清晰
- API/组件通过 → 才测E2E，避免无效测试

### 优先级顺序（快速验证）

```
1️⃣ 🧪 pytest API测试         ← 最重要（80%+覆盖率）
2️⃣ 🎨 Cypress 组件测试        ← 快速反馈
3️⃣ 🎭 Playwright E2E测试      ← 关键流程
其他可选...
```

---

## 📊 报告查看

### 独立工具报告

| 工具 | 报告位置 |
|------|---------|
| pytest | `tests/test-automation/report.html` |
| Cypress | `tests/cypress-tests/cypress/reports/` |
| Playwright | `tests/playwright-tests/playwright-report/` |
| Selenium | `tests/selenium-tests/report.html` |
| Puppeteer | `tests/puppeteer-tests/reports/` |
| K6 | `tests/test-reports/k6-report/summary.json` |

### 统一聚合报告

```
tests/test-reports/aggregated-report.json
```

**内容**：
- 所有工具的测试结果汇总
- 总用例数、通过数、失败数、通过率
- 发布门禁状态（PASSED/FAILED）

**查看方式**：
```powershell
# 打开JSON文件
code tests/test-reports/aggregated-report.json

# 或使用jq格式化输出
Get-Content tests/test-reports/aggregated-report.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 🐛 常见问题

### Q1: 任务执行报错"找不到命令"

**解决方案**：
```powershell
# pytest/Selenium -> 检查Python虚拟环境
cd tests/test-automation
.\venv\Scripts\Activate.ps1

# Playwright/Cypress/Puppeteer -> 检查Node依赖
npm install

# K6 -> 安装K6
choco install k6
```

### Q2: Selenium Grid启动失败

**解决方案**：
```powershell
cd tests/selenium-tests
docker-compose -f selenium-grid-config.yml down
docker-compose -f selenium-grid-config.yml up -d

# 验证
docker ps --filter 'name=selenium'
```

### Q3: Playwright浏览器下载失败

**解决方案**：
```powershell
cd tests/playwright-tests
npx playwright install --with-deps

# 如果网络问题，设置镜像
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
npx playwright install --with-deps
```

### Q4: 一键全量测试中断如何恢复

**解决方案**：
```powershell
cd tests/test-orchestrator

# 查看已完成的工具报告
ls ../test-reports/

# 手动执行剩余工具
npm run test:quick  # 或单独运行某个工具
```

### Q5: 报告聚合失败

**解决方案**：
```powershell
cd tests/test-orchestrator

# 检查各工具报告是否生成
ls ../test-reports/*/summary.json

# 手动触发聚合
node run-all-tests.js sequential
```

---

## 🔗 相关文档

- [五工具互补测试架构方案](./00-五工具互补测试架构方案.md) - 完整架构设计
- [五工具互补测试体系-交付文档](./五工具互补测试体系-交付文档.md) - 交付清单
- [test-orchestrator/README.md](./test-orchestrator/README.md) - 统一编排器使用指南
- [playwright-tests/README.md](./playwright-tests/README.md) - Playwright详细文档
- [selenium-tests/README.md](./selenium-tests/README.md) - Selenium详细文档

---

## ✨ 最佳实践

### 1. 本地开发流程

```
开发代码 → 🧪 pytest API测试 → 🎨 Cypress 组件测试 → 提交PR
```

### 2. PR合并前流程

```
PR创建 → CI执行 ⚡ 快速验证测试 → Code Review → 合并
```

### 3. 发版前流程

```
合并到main → CI执行 🏆 一键全量测试 → 生成报告 → 发布门禁 → 发版
```

### 4. 夜间回归流程

```
定时任务 → 🔥 并行全量测试 → 生成报告 → 邮件通知团队
```

---

**快速启动**：按 `Ctrl+Shift+P` → `Tasks: Run Task` → 选择 `⚡ 快速验证测试（pytest + Cypress）`

**问题反馈**：[GitHub Issues](https://github.com/your-repo/issues) 或联系测试团队
