# Playwright 半自动测试脚本

## 📚 目录

- [简介](#简介)
- [快速开始](#快速开始)
- [场景列表](#场景列表)
- [使用指南](#使用指南)
- [架构说明](#架构说明)
- [常见问题](#常见问题)

---

## 简介

本项目提供 **Playwright 半自动测试脚本**，用于辅助手动测试 AIOPS 系统。与传统的全自动测试不同，半自动测试会：

✅ **引导操作** - 系统高亮需要操作的元素  
✅ **显示提示** - 在页面上显示清晰的操作指导  
✅ **等待确认** - 等待测试人员完成操作后按回车继续  
✅ **截图留证** - 自动在每个关键步骤截图保存  
✅ **生成报告** - 自动生成包含步骤、截图和元数据的 JSON 报告  

**核心理念**：让系统引导您完成复杂的测试工作流，同时保留人工判断和验证。

---

## 快速开始

### 1. 安装依赖

```bash
cd tests/manual-test-helpers/playwright-semi-auto
npm install
```

### 2. 安装 Playwright 浏览器

```bash
npx playwright install
```

### 3. 配置环境变量（可选）

创建 `.env` 文件：

```env
BASE_URL=http://localhost:3000
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin123!@#
```

### 4. 运行场景

```bash
# 运行用户管理场景
npm run scenario:user

# 运行租户管理场景
npm run scenario:tenant

# 运行权限管理场景
npm run scenario:permission

# 运行充电工作流场景
npm run scenario:charging

# 运行设备管理场景
npm run scenario:device

# 运行工单管理场景
npm run scenario:workorder
```

### 5. 查看测试报告

```bash
npm run report
```

---

## 场景列表

### 已完成场景（6 个）✅

| 序号 | 场景名称 | 文件名 | 描述 | 命令 |
|------|---------|--------|------|------|
| 01 | 用户管理 | `01-user-management.spec.js` | 创建→编辑→分配角色→删除用户 | `npm run scenario:user` |
| 02 | 租户管理 | `02-tenant-management.spec.js` | 创建租户→配置→数据隔离验证→删除 | `npm run scenario:tenant` |
| 03 | 权限管理 | `03-permission-management.spec.js` | 创建角色→分配权限→测试访问→撤销 | `npm run scenario:permission` |
| 04 | 充电工作流 | `04-charging-workflow.spec.js` | 创建充电桩→启动充电→监控→完成→结算 | `npm run scenario:charging` |
| 05 | 设备管理 | `05-device-management.spec.js` | 注册设备→配置→绑定站点→监控→退役 | `npm run scenario:device` |
| 06 | 工单管理 | `06-workorder-workflow.spec.js` | 创建工单→分配→更新状态→备注→关闭 | `npm run scenario:workorder` |

### 规划中场景（7+ 个）⏳

| 序号 | 场景名称 | 描述 |
|------|---------|------|
| 07 | 站点管理 | 创建站点→添加设备→配置→监控→维护 |
| 08 | 结算工作流 | 生成账单→审核→批准→导出→归档 |
| 09 | 规则引擎 | 创建规则→配置条件→触发测试→监控执行 |
| 10 | 多租户隔离 | 创建数据→切换租户→验证隔离→测试跨租户访问 |
| 11 | 性能基线 | 加载页面→测量指标→对比基线→生成报告 |
| 12 | 端到端完整流程 | 设备注册→充电→计费→结算→归档 |
| 13 | 异常场景 | 非法输入→边界条件→网络故障→恢复 |

---

## 使用指南

### 基本使用流程

1. **启动系统**  
   确保 AIOPS 系统已启动（前端 + 后端 + 数据库）

2. **运行场景脚本**  
   ```bash
   npm run scenario:user  # 示例：运行用户管理场景
   ```

3. **跟随系统引导**  
   - 浏览器会自动打开并导航到相应页面
   - 页面上会显示彩色的提示框，告诉您下一步要做什么
   - 需要操作的元素会被红色边框高亮
   - 按照提示完成操作，然后按 **Enter 键**继续

4. **查看结果**  
   - 测试完成后，在 `test-results/` 目录查看：
     - `screenshots/` - 全部截图
     - `reports/` - JSON 格式的详细报告
     - `html-report/` - HTML 格式的测试报告

### 半自动交互方式

#### 1. 提示框

系统会在页面顶部显示紫色渐变的提示框：

```
┌─────────────────────────────────┐
│  📝 准备创建用户                │
│  请点击"新建用户"按钮             │
└─────────────────────────────────┘
```

#### 2. 元素高亮

需要操作的按钮或输入框会被红色边框高亮，并自动滚动到视图中心。

#### 3. 确认按钮

完成操作后，页面右下角会显示绿色的确认按钮：

```
┌──────────────────────┐
│  ✅ 确认 (Enter)      │
└──────────────────────┘
```

点击按钮或按 **Enter 键**继续下一步。

#### 4. 等待用户操作

某些复杂操作（如填写表单）会给您充足的时间：

```
⏳ 等待您填写表单... (最多 60 秒)
```

完成后按 Enter 继续。

---

## 架构说明

### 目录结构

```
playwright-semi-auto/
├── scenarios/               # 场景脚本目录
│   ├── 01-user-management.spec.js
│   ├── 02-tenant-management.spec.js
│   ├── 03-permission-management.spec.js
│   ├── 04-charging-workflow.spec.js
│   ├── 05-device-management.spec.js
│   └── 06-workorder-workflow.spec.js
├── helpers/                 # 辅助工具
│   ├── semi-auto-helper.js  # 核心辅助类
│   └── test-data.js         # 测试数据生成器
├── test-results/            # 测试结果
│   ├── screenshots/         # 截图
│   ├── reports/             # JSON 报告
│   ├── html-report/         # HTML 报告
│   └── output/              # 其他输出
├── package.json
├── playwright.config.js
└── README.md
```

### 核心类：SemiAutoHelper

位于 `helpers/semi-auto-helper.js`，提供以下功能：

**导航与登录**
- `navigate(path)` - 导航到指定路径
- `login(role)` - 使用预定义角色登录

**用户交互**
- `showPrompt(title, message, duration)` - 显示提示框
- `waitForUserConfirm(message)` - 等待用户确认
- `waitForUserAction(timeout)` - 等待用户完成操作
- `closePrompt()` - 关闭提示框

**元素高亮**
- `highlightElement(selector, duration)` - 高亮指定元素

**截图与报告**
- `takeScreenshot(name)` - 截图保存
- `logStep(description)` - 记录步骤
- `generateReport(scenarioName, metadata)` - 生成报告

**断言验证**
- `assertVisible(selector, message)` - 验证元素可见
- `assertText(selector, text, message)` - 验证文本内容
- `assertCount(selector, count, message)` - 验证元素数量

**API 监控**
- `monitorAPI(pattern)` - 监控并记录 API 请求

### 测试数据生成器：TestData

位于 `helpers/test-data.js`，提供以下方法：

- `generateUser()` - 生成随机用户数据
- `generateTenant()` - 生成随机租户数据
- `generateDevice()` - 生成随机设备数据
- `generateChargingOrder()` - 生成随机充电订单数据
- `generateWorkOrder()` - 生成随机工单数据
- `generateStation()` - 生成随机站点数据
- `generatePermission()` - 生成随机权限数据
- `generateRule()` - 生成随机规则数据
- `generateSettlement()` - 生成随机结算数据

---

## 常见问题

### Q1: 浏览器自动关闭了怎么办？

**A:** 修改 `playwright.config.js`，确保 `headless: false`：

```javascript
use: {
  headless: false,  // 保持浏览器可见
  ...
}
```

### Q2: 如何调整操作速度？

**A:** 在 `playwright.config.js` 中调整 `slowMo` 参数：

```javascript
launchOptions: {
  slowMo: 500  // 每个操作延迟 500ms
}
```

### Q3: 如何在调试模式下运行？

**A:** 使用调试命令：

```bash
npm run test:debug
```

或者：

```bash
npx playwright test --debug scenarios/01-user-management.spec.js
```

### Q4: 截图保存在哪里？

**A:** 所有截图保存在 `test-results/screenshots/` 目录，文件名格式：

```
2024-01-15T10-30-45-123Z-step-name.png
```

### Q5: 如何生成 HTML 报告？

**A:** 测试完成后运行：

```bash
npm run report
```

会自动打开 HTML 报告页面。

### Q6: 能否并行运行多个场景？

**A:** 不建议。半自动测试需要人工交互，建议一次运行一个场景。如需并行，修改 `playwright.config.js`：

```javascript
fullyParallel: true,
workers: 2,  // 并发数量
```

### Q7: 如何跳过某些步骤？

**A:** 使用 `.skip` 标记：

```javascript
test.skip('步骤2：配置租户信息', async () => {
  // 此步骤会被跳过
});
```

### Q8: 提示框遮挡了页面元素怎么办？

**A:** 按 `Esc` 键或点击提示框外部区域可以临时隐藏提示框。

### Q9: 如何自定义超时时间？

**A:** 在场景脚本中设置：

```javascript
test.setTimeout(60 * 60 * 1000);  // 设置为 60 分钟
```

或修改 `playwright.config.js` 的全局超时：

```javascript
timeout: 30 * 60 * 1000,  // 30 分钟
```

### Q10: 如何添加自定义场景？

**A:** 参考现有场景脚本，创建新文件：

```javascript
// scenarios/99-custom-scenario.spec.js
import { test } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';

let helper;

test.describe('自定义场景', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    await helper.login('admin');
  });

  test('您的测试步骤', async () => {
    await helper.navigate('/your/path');
    await helper.showPrompt('标题', '说明', 0);
    await helper.highlightElement('button', 3000);
    await helper.waitForUserConfirm('确认消息');
    await helper.takeScreenshot('step-name');
  });
});
```

然后在 `package.json` 添加脚本：

```json
"scenario:custom": "playwright test scenarios/99-custom-scenario.spec.js --headed"
```

---

## 技术栈

- **Playwright** ^1.42.0 - 浏览器自动化
- **Chalk** ^4.1.2 - 终端彩色输出
- **Faker** ^5.5.3 - 随机测试数据生成
- **Dotenv** ^16.4.5 - 环境变量管理

---

## 相关资源

- [Playwright 官方文档](https://playwright.dev/)
- [项目完整文档](../../docs/)
- [油猴脚本工具](../tampermonkey/)

---

## 贡献指南

欢迎贡献新的场景脚本或改进现有脚本！

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/new-scenario`)
3. 编写场景脚本
4. 提交更改 (`git commit -m 'Add new scenario: xxx'`)
5. 推送到分支 (`git push origin feature/new-scenario`)
6. 创建 Pull Request

---

## 许可证

MIT License

---

## 联系我们

- **团队**: JGSY AGI Team
- **邮箱**: support@jgsy.com
- **文档**: `/docs/`

---

**Happy Testing! 🚀**
