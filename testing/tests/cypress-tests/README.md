# Cypress 组件交互测试 - UmiJS 管理后台（仅限）

## 📋 测试范围

| 项目 | 说明 |
|------|------|
| **测试对象** | ✅ JGSY.AGI.Frontend（管理后台） |
| **基础 URL** | `http://localhost:8000`（UmiJS 仅有地址） |
| **测试方式** | ✅ 真实前端应用 + 后端接口可 Mock |
| **运行时间** | 10-15 分钟 |



---

## ✅ 快速开始

### 前置条件

1. **启动前端开发服务器**：
```bash
cd JGSY.AGI.Frontend
npm install  # 首次需要
npm run dev

# 等待输出：Ready on http://localhost:8000
```

2. **后端模式二选一**：
```bash
# 方案 A：真实后端联调
cd docker
docker-compose up -d

# 方案 B：后端接口 Mock
# 无需启动完整后端，由 Cypress 内部 cy.intercept() 提供接口响应
```

### 运行 Cypress 测试

```bash
# 终端 2：运行完整测试
cd tests/cypress-tests
npm install  # 首次需要
npm run cy:run

# 或 UI 调试模式
npm run cy:open
```

---

## 📊 输出和报告

### 生成测试报告

```bash
# 运行测试 + 生成 JSON 报告
npm run cy:run
# → reports/mochawesome_*.json

# 转换为可视化 HTML 报告（可选）
npm run generate-report
# → reports/mochawesome.html
```

### 查看报告

```bash
# Windows
start reports/mochawesome.html

# macOS
open reports/mochawesome.html

# Linux
xdg-open reports/mochawesome.html
```

---

## 🔍 故障排查

### ❌ "Cannot connect to http://localhost:8000"

**原因**：UmiJS 开发服务器未启动  
**解决**：
```bash
# 检查端口 8000 是否有进程监听
netstat -ano | findstr ":8000"  # Windows
lsof -i :8000  # macOS/Linux

# 启动 UmiJS
cd JGSY.AGI.Frontend
npm run dev
```

### ❌ "Cannot find element"

**原因**：页面加载失败或 HTML 结构不同  
**解决**：
1. 用 UI 调试模式查看实际 DOM：`npm run cy:open`
2. 更新选择器以匹配真实应用的 HTML 结构
3. 检查后端API返回的数据是否影响页面渲染

### ❌ "前端服务未启动，请先在 JGSY.AGI.Frontend 执行 npm run dev"

**原因**：真实前端页面未启动  
**解决**：
```bash
cd JGSY.AGI.Frontend
npm run dev
```

### ❌ "Request timeout" / "API 返回 500 错误"

**原因**：如果当前用例未对该接口做 Mock，则后端服务或 API 未正确启动  
**解决**：
```bash
# 检查后端服务状态
docker logs jgsy-permission  # 查看各服务日志
docker ps | grep jgsy        # 查看运行中的服务

# 重启后端
docker-compose restart
```

### ❌ 某个测试持续超时

**原因**：等待页面元素时间过长（网络/渲染慢）  
**解决**：
1. 增加超时时间。编辑 `cypress.config.js`：
   ```javascript
   defaultCommandTimeout: 15000,  // 改为 15 秒
   pageLoadTimeout: 30000,        // 改为 30 秒
   ```
2. 或跳过该测试暂时调试。编辑测试文件：
   ```javascript
   it.skip('[P2] 某个测试...', () => {
     // 测试代码
   });
   ```

---

## 📋 NPM 脚本速查

```bash
npm run cy:open           # 打开 Cypress UI 调试工具
npm run cy:run            # 运行完整测试套件
npm run generate-report   # 生成 HTML 可视化报告
```

---

## 🎯 最佳实践

### 开发/调试阶段

```bash
# 终端 1：启动后端 + UmiJS
docker-compose up -d
cd JGSY.AGI.Frontend && npm run dev

# 终端 2：Cypress UI 调试
cd tests/cypress-tests
npm run cy:open
```

### 自动化测试（CI/发布前）

```bash
# 一键测试（需后端 + UmiJS 已启动）
cd tests/cypress-tests
npm run cy:run
```

### 生成最终报告

```bash
npm run cy:run && npm run generate-report
# 打开 reports/mochawesome.html 查看详细结果
```

---

## 📝 架构说明

### Cypress 在五工具体系中的角色

```
┌───────────────────────────────────────────────────────────┐
│  AIOPS 五工具互补测试体系                                  │
├───────────────────────────────────────────────────────────┤
│ Playwright (E2E)      → 关键业务流程端到端（主力 70%）     │
│ Selenium  (兼容性)    → 多浏览器兼容性验证（次要 20%）    │
│ Puppeteer (性能)      → 页面性能指标采集（支撑 10%）      │
│ 🟢 Cypress (组件交互)  → 前端组件交互、状态逻辑（本层）   │
│ K6       (性能压测)   → API 负载压力测试（100% API 覆盖） │
└───────────────────────────────────────────────────────────┘

Cypress 定位：
✅ 通过真实前端应用验证组件逻辑和交互
✅ 测试状态管理（Redux）、表单合法性、路由跳转
✅ 后端接口可按场景选择真实联调或 cy.intercept() Mock
✅ 快速反馈（10-15 分钟）

❌ 不做 API 单元测试（用 pytest）
❌ 不做远程网络依赖（用 Playwright 跨浏览器）
```

### 测试大小金字塔

```
     🔴 Playwright (少数关键E2E)            [1%]
    🟡 Selenium (浏览器兼容性)            [5%]
   🟠 K6 (性能压测)                       [10%]
  🟢 Cypress (组件交互 - 真实应用)        [40%] ← 本层
 🔵 pytest (API 单元+集成测试)             [44%]
────────────────────────────────────────
高速反馈 ←─────────→ 覆盖广度
```

---

## 🎯 支持的前端应用

| 应用 | URL | 框架 | 测试 | 说明 |
|------|-----|------|------|------|
| **UmiJS 管理后台** | `http://localhost:8000` | React 18 | ✅ Cypress | **核心测试对象** |

---

## 💡 当前约束

支持真实前端页面的原因：
- ✅ 完全还原用户真实操作
- ✅ 页面结构、路由、组件渲染都来自真实应用

允许后端接口 Mock 的原因：
- ✅ 可以稳定复现前端交互场景
- ✅ 降低后端依赖带来的不稳定性
- ✅ 适合组件交互、权限态、异常态验证

---

## 📞 FAQ

**Q: 现在还能 Mock 吗？**

A: 可以，但只允许 Mock 后端接口，不允许 Mock 页面壳。页面必须来自真实 UmiJS 前端服务。

**Q: 能否连接远程 UmiJS？**

A: 可以。修改 `cypress.config.js` 的 `baseUrl`：
```javascript
baseUrl: 'http://192.168.1.100:8000'  // 内网 IP
baseUrl: 'http://host.docker.internal:8000'  // Docker 主机
```

**Q: 如何在 CI 中自动运行？**

A: 确保 Docker 和 UmiJS 在运行，然后：
```yaml
- run: |
    cd tests/cypress-tests
    npm install
    npm run cy:run
```

---

## 🔗 相关文件

- `tests/cypress-tests/e2e/` - 所有 UmiJS 测试用例
- `tests/cypress-tests/cypress.config.js` - Cypress 配置
- `tests/cypress-tests/support/commands.js` - 自定义命令
- `JGSY.AGI.Frontend/.umirc.ts` - UmiJS 配置


---

## 🔍 故障排查

### ❌ "Cannot connect to http://localhost:8000"

**原因**：UmiJS 开发服务器未启动  
**解决**：
```bash
# 检查是否有进程监听 8000 端口
netstat -ano | findstr ":8000"  # Windows
lsof -i :8000  # macOS/Linux

# 启动 UmiJS
cd JGSY.AGI.Frontend
npm run dev
```

### ❌ "Cannot find element" 错误

**原因**：页面加载失败或选择器错误  
**解决**：
1. 增加超时时间。编辑 `cypress.config.js`：
   ```javascript
   defaultCommandTimeout: 10000,  // 改为 10 秒
   ```
2. 用 UI 调试模式查看页面：`npm run cy:open`

### ❌ "API 请求失败" 错误

**原因**：后端服务未启动或 Mock 缺失  
**解决**：
1. 启动后端（如有需要）
2. 或改用 Mock 模式：`npm run cy:run:mock`

---

## 📋 NPM 脚本速查表

```bash
npm run cy:open          # 打开 Cypress UI（本地 Dev 模式）
npm run cy:run           # 运行完整测试（本地 Dev 模式）
npm run cy:open:mock     # 打开 Cypress UI（Mock 模式）
npm run cy:run:mock      # 运行完整测试（Mock 模式）
```

---

## 🎯 最佳实践

1. **开发阶段**：
   - 用 Mock 模式 (`npm run cy:open:mock`) 快速调试
   - 或启动 UmiJS，用本地模式 (`npm run cy:open`)

2. **提交前**：
   - 运行 Mock 模式确保通过：`npm run cy:run:mock`

3. **发布前**：
   - 启动完整栈（UmiJS + 后端），运行完整测试：`npm run cy:run`

---

## 📝 架构说明

### Cypress 在五工具体系中的角色

```
┌─────────────────────────────────────────────────────────┐
│  AIOPS 五工具互补测试体系                                │
├─────────────────────────────────────────────────────────┤
│ Playwright (E2E)      → 关键业务流程端到端（主力）       │
│ Selenium  (兼容性)    → 多浏览器兼容性验证               │
│ Puppeteer (性能)      → 性能指标采集监控                 │
│ 🟢 Cypress (组件交互)  → 前端组件逻辑、状态交互（本层）  │
│ K6       (性能压测)   → API 负载压力测试                 │
└─────────────────────────────────────────────────────────┘

Cypress 职责：
✅ 通过 Mock API 快速测试前端组件逻辑
✅ 通过本地 Dev Server 测试真实前端应用
✅ 测试状态管理（Redux）、表单交互、路由跳转
✅ 快速反馈循环（2-10 分钟）

❌ 不做 API 层单元测试（用 pytest）
❌ 不做远程网络依赖（用 Playwright）
```

---

## 🎯 支持的前端应用

当前支持：
- ✅ **JGSY.AGI.Frontend**（UmiJS 4 + React 18）- 管理后台

---

## 📞 FAQ

**Q: 为什么用 Mock 而不是真实 API？**

A: Mock 模式提供**快速反馈**（2分钟），用于开发阶段快速迭代。完整测试时，用本地 Dev 模式（10分钟），连接真实 UmiJS 和 API。

**Q: 如何在 CI Pipeline 中使用？**

A: 推荐 Mock 模式，快速且不依赖外部服务：
```yaml
- run: cd tests/cypress-tests && npm run cy:run:mock
```

**Q: 支持远程服务器（如 Docker 容器）吗？**

A: 可以。修改 `cypress.config.js` 的 `baseUrl`：
```javascript
baseUrl: 'http://host.docker.internal:8000'  // Docker 中访问主机
baseUrl: 'http://192.168.1.100:8000'         // 指定内网 IP
```

---

## 🔗 相关文档

- `tests/cypress-tests/e2e/` - 所有测试用例
- `tests/cypress-tests/support/commands.js` - 自定义命令
- `tests/00-五工具互补测试架构方案.md` - 完整架构设计

---

## ✅ 快速开始

### 模式 1️⃣：Mock 本地快速测试（推荐 CI/快速反馈）

```bash
cd tests/cypress-tests

# 安装依赖（首次）
npm install

# 运行测试（2 分钟，100% 必过）
npm run cy:run:mock

# 生成报告
# → reports/mochawesome_*.json 等文件

# UI 调试模式
npm run cy:open:mock
```

**特点**：
- ✅ 依赖 Mock API，无网络延迟  
- ✅ 测试前端组件状态、交互逻辑
- ✅ 快速反馈（CI/CD 友好）
- ❌ 不测 API 集成（那是 Playwright 的职责）

**输出**：
```
✓ 登录页面正常加载
✓ 用户名密码输入框可交互
✓ 登录成功跳转到首页
... （共 50+ 用例）
```

---

### 模式 2️⃣：本地 Dev Server 完整测试（推荐集成验证）

**前置条件**：
- ✅ 后端服务已启动（如 `docker-compose up`）
- ✅ UmiJS 前端开发服务器可用

**第一步：启动前端 Dev Server**

```bash
# 终端 1：启动 UmiJS
cd JGSY.AGI.Frontend
npm install  # 首次需要
npm run dev

# 等待输出：Ready on http://localhost:8000
```

**第二步：运行 Cypress 测试**

```bash
# 终端 2：运行测试
cd tests/cypress-tests
npm run cy:run:local

# 或 UI 调试
npm run cy:open:local
```

**特点**：
- ✅ 连接真实前端应用（UmiJS）
- ✅ 使用真实后端 API（需后端启动）
- ✅ 测试完整的页面流程
- ⏱️ 较慢（10-15 分钟），但最接近真实

**故障排查**：
```bash
# 如果超时：
# 1. 检查后端服务是否启动
# 2. 检查 UmiJS 是否运行（http://localhost:8000）
# 3. 增加超时时间：修改 cypress.local.js
```

---

### 模式 3️⃣：远程测试（不推荐）

```bash
npm run cy:run  # 连接 https://aiops.jgsy.com（生产环境）
```

⚠️ **警告**：
- 网络延迟大（60-90 秒/页面）
- 容易超时（30 分钟+）
- 仅用于最终发布前验证

---

## 📊 报告生成

### 生成 HTML 报告

```bash
# 仅合并 JSON 报告（推荐快速）
npm run cy:run:mock
# 报告位置：reports/mochawesome_*.json

# 转换为可视 HTML（可选）
npx mochawesome-merge reports/*.json > reports/merged.json
npx marge reports/merged.json --reportDir reports --inline
# 打开：reports/mochawesome.html
```

### 查看报告

```bash
# Windows
start reports/mochawesome.html

# macOS
open reports/mochawesome.html

# Linux
firefox reports/mochawesome.html
```

---

## 🔍 故障排查

### ❌ "Cannot find element" 错误

**原因**：前端应用未加载或渲染困难  
**解决**：
1. 检查 `baseUrl` 是否正确
2. 增加 `defaultCommandTimeout`（如 10000ms）
3. 使用 `cy.log()` 调试

### ❌ "Request timeout" 错误

**原因**：API 响应慢或后端未启动  
**解决**：
1. 确认后端服务启动：`docker ps | grep jgsy`
2. 增加 `responseTimeout`（如 15000ms）
3. 切换到 Mock 模式排除后端问题

### ❌ 一直卡在某个 spec 不进下一个

**原因**：前置 Hook 未正确清理  
**解决**：
```javascript
afterEach(() => {
  cy.logout();  // 清理登录状态
});
```

---

## 📈 CI/CD 集成

### GitHub Actions 示例

```yaml
- name: Run Cypress Tests (Mock Mode)
  run: |
    cd tests/cypress-tests
    npm install
    npm run cy:run:mock
    
- name: Upload Report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: cypress-report
    path: tests/cypress-tests/reports/
```

### GitLab CI 示例

```yaml
cypress:test:mock:
  stage: test
  script:
    - cd tests/cypress-tests
    - npm install
    - npm run cy:run:mock
  artifacts:
    reports:
      junit: tests/cypress-tests/reports/junit.xml
    paths:
      - tests/cypress-tests/reports/
    expire_in: 30 days
```

---

## 🎯 最佳实践

1. **开发阶段**：用 Mock 模式 (`cy:open:mock`) 快速反馈
2. **集成测试**：启动完整栈（Dev Server + Backend），用本地模式
3. **CI Pipeline**：用 Mock 模式快速验证
4. **发布前**：用本地模式完整验证，再用远程模式最终确认

---

## 📝 笔记

### Cypress 在五工具体系中的角色

```
┌─────────────────────────────────────────────────────────┐
│  五工具互补测试体系                                      │
├─────────────────────────────────────────────────────────┤
│ Playwright (E2E)      → 关键业务流程端到端测试（主力）  │
│ Selenium  (兼容性)    → 多浏览器兼容性验证               │
│ Puppeteer (性能)      → 性能指标采集监控                 │
│ 🟢 Cypress (组件)     → 前端组件交互、状态逻辑（本层）   │
│ K6       (压测)       → API 负载压力测试                 │
└─────────────────────────────────────────────────────────┘

Cypress 职责：
✅ 测试组件生命周期、Redux/Vuex 状态管理
✅ 测试表单交互、模态框、路由跳转
✅ 快速反馈（2 分钟）
❌ 不测 API 层（那是 pytest/K6 的职责）
❌ 不做端到端业务验证（那是 Playwright 的职责）
```

---

## 🤔 FAQ

**Q: Mock 模式下的测试算真实吗？**

A: 你测的是 **前端组件层面的真实**，这是 Cypress 的正确定位。Mock API 避免了对后端的依赖，加快了反馈循环。如果要测 API 集成，用**本地 Dev 模式**或 **Playwright**。

**Q: 如何选择模式？**

A: 
- 开发中快速反馈 → Mock 模式（2分钟）
- 功能验证 → 本地 Dev 模式（10分钟）
- 最终发布验证 → 远程模式（30分钟，可选）

**Q: 能同时运行多个 spec 吗？**

A: 可以，Cypress 默认并行运行（取决于 CPU）。加参数 `--spec e2e/01-login.cy.js,e2e/02-dashboard.cy.js` 指定多个。

---

## 📞 支持

如有问题，请查看：
- `tests/cypress-tests/e2e/*.cy.js` - 测试用例
- `tests/cypress-tests/support/commands.js` - 自定义命令
- `tests/00-五工具互补测试架构方案.md` - 完整架构设计
