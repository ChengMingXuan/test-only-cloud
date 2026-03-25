# Playwright E2E 测试套件

> **AIOPS 平台端到端自动化测试**  
> 基于 Playwright 的跨浏览器测试框架

---

## 📋 目录

- [快速开始](#快速开始)
- [测试架构](#测试架构)
- [测试用例](#测试用例)
- [执行测试](#执行测试)
- [调试技巧](#调试技巧)
- [最佳实践](#最佳实践)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd tests/playwright-tests
npm install
```

### 2. 安装浏览器

```bash
npm run install:browsers
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
TEST_BASE_URL=https://aiops.jgsy.com
ADMIN_USERNAME=admin@jgsy.com
ADMIN_PASSWORD=P@ssw0rd
USER_USERNAME=user@jgsy.com
USER_PASSWORD=User@123456
TEST_ENV=staging
```

### 4. 运行第一个测试

```bash
# 运行所有测试（headless模式）
npm test

# 运行单个测试文件
npm run test:auth

# 使用UI模式（推荐）
npm run test:ui
```

---

## 🏗️ 测试架构

### 目录结构

```
playwright-tests/
├── tests/                      # 测试用例
│   ├── auth.spec.ts           # 认证模块测试
│   ├── charging.spec.ts       # 充电模块测试
│   ├── station.spec.ts        # 充电站模块测试
│   ├── tenant.spec.ts         # 租户模块测试
│   └── ...
├── page-objects/              # 页面对象模型（POM）
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   └── ...
├── fixtures/                  # 测试夹具和数据
│   ├── test-data.json
│   └── mock-responses.ts
├── .auth/                     # 认证状态存储
│   ├── admin-auth.json
│   └── user-auth.json
├── playwright.config.ts       # Playwright配置
├── global-setup.ts            # 全局设置
├── global-teardown.ts         # 全局清理
└── package.json
```

### 浏览器配置

支持7种浏览器/设备配置：

| 项目名 | 说明 | 使用场景 |
|--------|------|----------|
| `chromium` | Chrome/Edge 桌面版 | 主力测试 |
| `firefox` | Firefox 桌面版 | 跨浏览器兼容 |
| `webkit` | Safari 桌面版 | Mac/iOS 兼容 |
| `mobile-chrome` | Android Chrome | 移动端测试 |
| `mobile-safari` | iPhone Safari | iOS测试 |
| `desktop-hd` | 高分辨率桌面 | 1920x1080 |
| `tablet` | iPad | 平板测试 |

---

## 📝 测试用例

### 已实现测试（30+ 用例）

#### 1. 认证模块 (`auth.spec.ts`)

- ✅ 正确用户名密码登录成功
- ✅ 错误密码登录失败
- ✅ 用户名不存在登录失败
- ✅ 空用户名密码提交失败
- ✅ 登录后成功登出
- ✅ Token过期后自动跳转
- ✅ Refresh Token续期
- ✅ 忘记密码流程
- ✅ 密码重置链接验证
- ✅ 多设备同时登录
- ✅ 多次失败后显示验证码

#### 2. 充电模块 (`charging.spec.ts`)

- ✅ 创建充电订单成功
- ✅ 充电站无可用桩提示
- ✅ 充电功率超限提示
- ✅ 微信支付订单
- ✅ 支付宝支付订单
- ✅ 支付超时自动取消
- ✅ 实时充电进度显示
- ✅ 充电异常告警
- ✅ 手动停止充电
- ✅ 历史订单分页
- ✅ 按状态筛选订单
- ✅ 按时间范围筛选
- ✅ 导出订单数据
- ✅ 未支付订单取消
- ✅ 已支付订单退款
- ✅ 充电中订单不可取消

### 待实现测试（60+ 用例）

- 充电站管理（创建/编辑/删除/启用/禁用）
- 充电桩管理（添加/配置/状态监控）
- 租户管理（创建/配置/多租户隔离）
- 用户管理（邀请/权限/角色分配）
- 工单管理（创建/分配/处理/关闭）
- 结算管理（对账/开票/报表）
- 规则引擎（创建规则/调试/告警）
- 数据看板（图表加载/数据准确性）

---

## ▶️ 执行测试

### 基础命令

```bash
# 运行所有测试
npm test

# 使用UI模式（可视化调试）
npm run test:ui

# Headed模式（显示浏览器窗口）
npm run test:headed

# Debug模式（逐步调试）
npm run test:debug
```

### 按浏览器执行

```bash
# 仅Chromium
npm run test:chromium

# 仅Firefox
npm run test:firefox

# 仅Safari
npm run test:webkit

# 移动端浏览器
npm run test:mobile
```

### 按标签执行

```bash
# 仅P0冒烟测试
npm run test:smoke

# 仅关键路径
npm run test:critical

# 特定模块
npm run test:auth
npm run test:charging
npm run test:station
```

### 并行执行

```bash
# 4个worker并行（本地默认）
npm test

# 指定worker数量
npm test -- --workers=2

# 完全并行（最快）
npm test -- --fully-parallel
```

### 失败重试

```bash
# 失败时重试2次
npm test -- --retries=2

# CI环境自动开启重试
CI=true npm test
```

---

## 🐛 调试技巧

### 1. 使用 UI 模式（推荐）

```bash
npm run test:ui
```

功能：
- ✅ 可视化测试执行
- ✅ 时间旅行调试
- ✅ 实时查看DOM
- ✅ 网络请求监控
- ✅ 截图和视频回放

### 2. 使用 Debug 模式

```bash
npm run test:debug
```

功能：
- ✅ 逐步执行
- ✅ 在浏览器开发者工具中调试
- ✅ 设置断点

### 3. 使用 Trace Viewer

```bash
# 测试失败后，打开trace
npx playwright show-trace trace.zip
```

### 4. 使用 Codegen（录制测试）

```bash
# 录制新测试用例
npm run codegen

# 指定起始URL
npx playwright codegen https://aiops.jgsy.com/charging/orders
```

### 5. 选择性运行

```bash
# 仅运行包含"登录"的测试
npm test -- -g "登录"

# 跳过Firefox
npm test -- --project=chromium --project=webkit
```

---

## 📊 测试报告

### HTML报告

测试完成后自动生成：

```bash
# 查看报告
npm run report
```

报告位置：`../test-reports/playwright-report/index.html`

包含内容：
- ✅ 测试通过/失败统计
- ✅ 执行时间分析
- ✅ 失败用例截图
- ✅ 视频录制
- ✅ 追踪文件

### JSON报告

```json
{
  "suites": [...],
  "stats": {
    "total": 30,
    "passed": 28,
    "failed": 2,
    "skipped": 0
  }
}
```

位置：`../test-reports/playwright-report/results.json`

### JUnit报告

位置：`../test-reports/playwright-report/junit.xml`  
用途：集成到CI/CD (Jenkins/GitLab CI)

---

## 🎯 最佳实践

### 1. 使用 Page Object Model (POM)

**Bad ❌**:
```typescript
test('登录', async ({ page }) => {
  await page.fill('#username', 'admin');
  await page.fill('#password', '123456');
  await page.click('#login-btn');
});
```

**Good ✅**:
```typescript
test('登录', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('admin', '123456');
});
```

### 2. 使用 data-testid 而非 CSS 选择器

**Bad ❌**:
```typescript
await page.click('.btn.btn-primary.login-button');
```

**Good ✅**:
```typescript
await page.click('[data-testid="login-button"]');
```

### 3. 合理设置超时

**Bad ❌**:
```typescript
await page.waitForTimeout(5000); // 硬编码等待
```

**Good ✅**:
```typescript
await page.waitForSelector('[data-testid="order-loaded"]', { timeout: 10000 });
```

### 4. 使用认证状态复用

**Bad ❌**:
```typescript
test('查看订单', async ({ page }) => {
  // 每个测试都重新登录
  await page.goto('/login');
  await page.fill('username', 'admin');
  await page.fill('password', '123456');
  await page.click('login');
  
  await page.goto('/orders');
  // ...
});
```

**Good ✅**:
```typescript
test.use({ storageState: '.auth/admin-auth.json' });

test('查看订单', async ({ page }) => {
  await page.goto('/orders'); // 已登录
  // ...
});
```

### 5. 独立且可重复执行

**Bad ❌**:
```typescript
test('测试1', async () => {
  // 创建数据
});

test('测试2', async () => {
  // 依赖测试1的数据 ❌
});
```

**Good ✅**:
```typescript
test('测试1', async () => {
  // 自己创建所需数据
});

test('测试2', async () => {
  // 自己创建所需数据
});
```

### 6. 使用标签分类

```typescript
test('[P0] 关键功能 @smoke @critical', async () => {
  // P0级测试，每次构建必跑
});

test('[P1] 常规功能', async () => {
  // P1级测试，每日回归
});

test('[P2] 边缘情况 @slow', async () => {
  // P2级测试，发版前跑
});
```

### 7. 清理测试数据

```typescript
test.afterEach(async ({ page }) => {
  // 在数据库中删除测试创建的数据
  await page.request.delete('/api/test-data/cleanup', {
    data: { testId: 'test-001' }
  });
});
```

---

## 🔧 配置详解

### playwright.config.ts 关键配置

```typescript
export default defineConfig({
  // 测试超时
  timeout: 60 * 1000,        // 单个测试60秒
  
  // 断言超时
  expect: {
    timeout: 10 * 1000,      // 断言10秒
  },
  
  // 失败重试
  retries: process.env.CI ? 2 : 1,
  
  // 并行worker
  workers: process.env.CI ? 2 : 4,
  
  // 视频录制
  use: {
    video: 'retain-on-failure',  // 仅失败保留
    screenshot: 'only-on-failure', // 仅失败截图
    trace: 'retain-on-failure',   // 仅失败追踪
  },
});
```

---

## 🚨 常见问题

### Q1: 测试不稳定，时快时慢？

**A**: 使用显式等待而非固定延迟：

```typescript
// ❌ 不稳定
await page.waitForTimeout(3000);

// ✅ 稳定
await page.waitForSelector('[data-testid="order-list"]');
await page.waitForLoadState('networkidle');
```

### Q2: 如何处理弹窗？

**A**: 使用 dialog 事件监听：

```typescript
page.on('dialog', async dialog => {
  console.log(dialog.message());
  await dialog.accept(); // 或 dialog.dismiss()
});

await page.click('[data-testid="delete-button"]');
```

### Q3: 如何拦截网络请求？

**A**: 使用 route：

```typescript
await page.route('**/api/orders', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ data: [] }),
  });
});
```

### Q4: 如何上传文件？

**A**: 使用 setInputFiles：

```typescript
await page.setInputFiles('[data-testid="file-upload"]', 'path/to/file.pdf');
```

### Q5: 如何在CI中运行？

**A**: 使用Docker或GitHub Actions：

```yaml
# .github/workflows/playwright.yml
- name: Run Playwright tests
  run: |
    cd tests/playwright-tests
    npm ci
    npx playwright install --with-deps
    npm test
```

---

## 📚 相关文档

- [Playwright 官方文档](https://playwright.dev/)
- [00-五工具互补测试架构方案.md](../00-五工具互补测试架构方案.md)
- [00-测试执行总体计划.md](../00-测试执行总体计划.md)
- [manual-test-checklist.md](../manual-test-checklist.md)

---

## 👥 联系我们

- 测试负责人: [测试负责人邮箱]
- Playwright 专家: [前端测试工程师]
- 技术支持: [技术支持群]

---

**最后更新**: 2026-03-05  
**维护者**: JGSY.AGI 测试团队
