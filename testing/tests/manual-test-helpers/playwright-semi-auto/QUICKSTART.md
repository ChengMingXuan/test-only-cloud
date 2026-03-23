# 🚀 Playwright 半自动脚本 - 快速启动指南

> 不到 5 分钟，开始您的第一个半自动化测试场景！


## 📦 一键安装

```bash
cd tests/manual-test-helpers/playwright-semi-auto
npm install && npx playwright install
```

## ⚡ 快速运行

### 运行单个场景（推荐新手）

```bash
# 用户管理 - 最简单的场景（4 个步骤）
npm run scenario:user

# 其他热门场景
npm run scenario:tenant      # 租户管理
npm run scenario:charging    # 充电工作流
npm run scenario:device      # 设备管理
npm run scenario:permission  # 权限管理
npm run scenario:workorder   # 工单管理
```

### 运行所有场景

```bash
# 完整测试套件（13 个场景）
npm run test

# 可视化模式（推荐）
npm run test:ui
```

## 🎯 使用步骤

### 第 1 步：启动系统
确保 AIOPS 系统正常运行（前端 + 后端 + 数据库）

### 第 2 步：打开场景
```bash
npm run scenario:user
```

### 第 3 步：跟随引导
1. 浏览器自动打开并显示提示
2. 页面高亮要操作的元素（红色边框）
3. 按照提示完成操作
4. 按 **Enter 键**或点击**✅ 确认**按钮继续

### 第 4 步：查看报告
```bash
npm run report
```

## 📸 截图与报告

### 自动保存位置

```
test-results/
├── screenshots/      # 场景截图
│   └── 2024-03-05T10-30-45-123Z-user-created.png
├── reports/          # JSON 报告
│   └── user-management-2024-03-05T10-30-45-123Z.json
└── html-report/      # HTML 格式报告
```

### 查看报告

```bash
# 自动打开 HTML 报告
npm run report

# 或手动查看
ls test-results/screenshots/    # 查看截图
cat test-results/reports/*      # 查看 JSON 报告
```

## 🎓 13 个完整场景速览

| 快捷命令 | 场景 | 用时 | 难度 |
|---------|------|------|------|
| `npm run scenario:user` | 👤 用户管理 | 10 分钟 | ⭐ 最简单 |
| `npm run scenario:tenant` | 🏢 租户管理 | 12 分钟 | ⭐ |
| `npm run scenario:permission` | 🔐 权限管理 | 15 分钟 | ⭐⭐ |
| `npm run scenario:charging` | ⚡ 充电工作流 | 15 分钟 | ⭐⭐ |
| `npm run scenario:device` | 🔧 设备管理 | 15 分钟 | ⭐⭐ |
| `npm run scenario:workorder` | 📝 工单管理 | 15 分钟 | ⭐⭐ |
| `npm run scenario:station` | 🏬 站点管理 | 18 分钟 | ⭐⭐ |
| `npm run scenario:settlement` | 💰 结算工作流 | 18 分钟 | ⭐⭐⭐ |
| `npm run scenario:rule` | ⚙️ 规则引擎 | 12 分钟 | ⭐⭐ |
| `npm run scenario:multitenant` | 🔒 多租户隔离 | 15 分钟 | ⭐⭐⭐ |
| `npm run scenario:performance` | 📈 性能基线 | 10 分钟 | ⭐⭐ |
| `npm run scenario:e2e` | 🔗 端到端流程 | 20 分钟 | ⭐⭐⭐ |
| `npm run scenario:error` | ⚠️ 异常场景 | 25 分钟 | ⭐⭐⭐⭐ |

## 💡 常见问题

### Q: 浏览器没打开？
```bash
# 检查配置
cat playwright.config.js | grep headless
# 应该显示: headless: false

# 如果是 true，修改为 false 并重新运行
```

### Q: 元素找不到（超时）？
```bash
# 增加等待时间
npm run test:headed        # 可视化模式更容易看到问题
npm run test:debug         # 调试模式，支持暂停
```

### Q: 如何跳过某个场景的某个步骤？
编辑 `scenarios/XX-scenario.spec.js`，找到对应步骤，使用 `.skip`：
```javascript
test.skip('步骤2：配置参数', async () => {
  // 此步骤会被跳过
});
```

### Q: 生成的数据在哪里？
每次运行时，系统使用 Faker.js 生成随机测试数据（用户名、邮箱、电话等）。数据详情在 JSON 报告中。

### Q: 能并行运行多个场景吗？
不建议。半自动测试需要人工交互。如需并行，编辑 `playwright.config.js`：
```javascript
fullyParallel: true,
workers: 2,
```

## 🔧 高级用法

### 自定义场景

```javascript
// 在 scenarios/ 创建新文件：custom-scenario.spec.js

import { test } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';

let helper;

test.describe('您的自定义场景', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    await helper.login('admin');
  });

  test('步骤1：操作', async () => {
    await helper.navigate('/your/path');
    await helper.showPrompt('标题', '说明');
    await helper.highlightElement('button');
    await helper.waitForUserConfirm('确认？');
    await helper.takeScreenshot('step-name');
  });

  test.afterEach(async () => {
    await helper.generateReport('custom-scenario', {});
  });
});
```

然后在 `package.json` 添加：
```json
"scenario:custom": "playwright test scenarios/custom-scenario.spec.js --headed"
```

### 修改配置

编辑 `playwright.config.js`：
```javascript
// 调整浏览器速度（毫秒）
slowMo: 1000,  // 默认 500

// 调整等待时间
timeout: 60 * 60 * 1000,  // 60 分钟

// 调整截图策略
screenshot: 'only-on-failure',  // 仅失败时截图
```

## 📚 完整文档

- [详细使用指南](README.md)
- [完成报告](COMPLETION_REPORT.md)
- [原始 USAGE 文档](USAGE.md)

## 🎯 典型工作流

### 场景 1：一次完整的测试（约 25 分钟）

```bash
# 1. 启动一个场景
npm run scenario:user

# 2. （跟随系统引导完成 4 个测试步骤）

# 3. 查看报告
npm run report

# 4. 检查截图和 JSON 报告
```

### 场景 2：完整测试套件（约 3 小时）

```bash
# 运行全部 13 个场景
npm run test

# 最后生成综合报告
npm run report
```

## ✅ 检查清单

启动前，请确认：

- [ ] AIOPS 系统已启动
- [ ] Node.js >= 18 已安装
- [ ] `npm install` 已执行
- [ ] `npx playwright install` 已执行
- [ ] 浏览器已关闭旧实例

## 🎉 开始吧！

```bash
# 一行命令启动您的第一个测试
npm run scenario:user
```

**提示**：如果是首次使用，建议从 `scenario:user` 开始，这是最简单的场景！

---

**需要帮助？** 查看 [README.md](README.md) 或 [COMPLETION_REPORT.md](COMPLETION_REPORT.md)

**Happy Testing! 🚀**
