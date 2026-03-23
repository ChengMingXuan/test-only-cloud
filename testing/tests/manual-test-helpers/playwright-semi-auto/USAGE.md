# Playwright 半自动测试指南

> 详细使用 Playwright 半自动测试脚本

---

## 📖 概述

Playwright 半自动测试脚本结合了自动化测试的效率和人工测试的灵活性：

- ✅ 自动化重复性操作（导航、点击、等待）
- ✅ 在关键点暂停，等待人工验证
- ✅ 截图记录测试过程
- ✅ 录制操作步骤以便重放

---

## 🚀 安装

### 前置条件

- Node.js 16+ 已安装
- npm 或 yarn 包管理器

### 安装步骤

```powershell
# 1. 进入目录
cd tests/manual-test-helpers/playwright-semi-auto

# 2. 安装依赖
npm install

# 3. 安装浏览器（首次运行）
npx playwright install chromium

# 4. （可选）安装其他浏览器
npx playwright install firefox
npx playwright install webkit
```

### 验证安装

```powershell
# 运行测试命令（会显示菜单）
npm run test:interactive
```

---

## 📝 配置

### 环境变量

创建 `.env` 文件（可选）：

```bash
# 测试环境 URL
BASE_URL=https://aiops.jgsy.com

# 浏览器选择（chromium, firefox, webkit）
BROWSER=chromium

# 录制模式（true/false）
RECORD_MODE=false

# 慢速模式延迟（毫秒）
SLOW_MO=500

# 无头模式（true/false）
HEADLESS=false
```

### 配置文件

编辑 `semi-auto-tester.js` 中的 `CONFIG` 对象：

```javascript
const CONFIG = {
  // 基础 URL
  baseURL: process.env.BASE_URL || 'https://aiops.jgsy.com',
  
  // 浏览器选择
  browser: process.env.BROWSER || 'chromium', // chromium, firefox, webkit
  
  // 录制模式
  recordMode: process.env.RECORD_MODE === 'true',
  
  // 慢速模式（每个操作延迟）
  slowMo: parseInt(process.env.SLOW_MO || '500'),
  
  // 无头模式
  headless: process.env.HEADLESS === 'true',
  
  // 截图保存目录
  screenshotDir: './screenshots',
  
  // 录制保存目录
  recordingDir: './recordings',
};
```

---

## 🎮 使用方式

### 模式一：预定义场景测试

运行内置的测试场景：

```powershell
# 充电订单场景
npm run test:charging

# 工单场景
npm run test:workorder

# 设备管理场景
npm run test:device
```

#### 充电订单场景流程

```
1. 自动导航到充电订单列表页
   ⏸️  暂停 - 人工验证列表是否正常

2. 自动点击"新建订单"按钮
   ⏸️  暂停 - 人工填充表单数据

3. 自动截图保存表单

4. 自动点击"提交"按钮

5. 自动等待成功提示
   ⏸️  暂停 - 人工验证订单是否创建成功

6. 自动截图保存结果

7. 测试完成
```

#### 工单场景流程

```
1. 自动导航到工单列表页
   ⏸️  暂停 - 人工验证

2. 自动点击"创建工单"按钮
   ⏸️  暂停 - 人工填充表单

3. 自动截图

4. 测试完成
```

#### 设备管理场景流程

```
1. 自动导航到设备列表页
   ⏸️  暂停 - 人工验证

2. 自动点击第一行的"编辑"按钮
   ⏸️  暂停 - 人工修改设备信息

3. 自动截图

4. 测试完成
```

---

### 模式二：交互式测试

完全手动控制浏览器：

```powershell
npm run test:interactive
# 选择 "2. 交互式模式"
```

#### 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `goto <url>` | 导航到 URL | `goto /charging/orders` |
| `click <selector>` | 点击元素 | `click button.create-btn` |
| `fill <selector> <value>` | 填充输入框 | `fill #username admin` |
| `screenshot [name]` | 截图 | `screenshot order-list` |
| `wait <selector>` | 等待元素出现 | `wait .ant-table` |
| `back` | 浏览器后退 | `back` |
| `forward` | 浏览器前进 | `forward` |
| `reload` | 刷新页面 | `reload` |
| `save` | 保存录制 | `save` |
| `quit` | 退出测试 | `quit` |

#### 交互式测试示例

```powershell
🎮 > goto /charging/orders
✅ 已导航到 /charging/orders

🎮 > screenshot list-page
📸 截图已保存: screenshots/2026-03-05T14-30-00_list-page.png

🎮 > click button:has-text("新建订单")
✅ 已点击: button:has-text("新建订单")

🎮 > fill #stationName 测试充电站
✅ 已填充: #stationName = 测试充电站

🎮 > fill #power 120
✅ 已填充: #power = 120

🎮 > screenshot form-filled
📸 截图已保存: screenshots/2026-03-05T14-31-00_form-filled.png

🎮 > click button[type="submit"]
✅ 已点击: button[type="submit"]

🎮 > wait .ant-message-success
✅ 元素已出现: .ant-message-success

🎮 > screenshot order-created
📸 截图已保存: screenshots/2026-03-05T14-32-00_order-created.png

🎮 > save
💾 录制已保存: recordings/recording_2026-03-05T14-32-00.json

🎮 > quit
👋 测试结束
```

---

### 模式三：录制与重放

#### 录制操作

```powershell
# 启用录制模式
npm run test:record

# 或设置环境变量
RECORD_MODE=true npm run test:interactive
```

所有操作会被记录到 JSON 文件：

```json
{
  "timestamp": "2026-03-05T14:30:00.000Z",
  "browser": "chromium",
  "baseURL": "https://aiops.jgsy.com",
  "actions": [
    {
      "type": "navigate",
      "url": "/charging/orders",
      "timestamp": "2026-03-05T14:30:01.000Z"
    },
    {
      "type": "click",
      "selector": "button.create-btn",
      "timestamp": "2026-03-05T14:30:05.000Z"
    },
    {
      "type": "fill",
      "selector": "#stationName",
      "value": "测试充电站",
      "timestamp": "2026-03-05T14:30:10.000Z"
    }
  ]
}
```

#### 重放录制（功能待实现）

```powershell
npm run test:replay -- recordings/recording_xxx.json
```

---

### 模式四：调试模式

显示浏览器窗口并减慢操作速度：

```powershell
# 慢速模式（1秒延迟）
npm run test:slow

# 调试模式（显示浏览器 + 1秒延迟）
npm run test:debug

# 或自定义延迟
SLOW_MO=2000 npm run test:interactive
```

---

## 💡 暂停点交互

### 暂停点显示

当脚本执行到暂停点时：

```
============================================================
⏸️  暂停点
📋 验证充电订单列表页面是否正常加载
按 Enter 继续执行，输入 s 截图，输入 q 退出...
============================================================
> 
```

### 操作选项

| 输入 | 操作 |
|------|------|
| `Enter` | 继续执行下一步 |
| `s` | 截图当前页面（然后再次显示暂停点） |
| `q` | 退出测试 |

### 使用暂停点的场景

1. **验证数据加载**
   - 在列表页暂停，确认数据显示正确

2. **填充表单数据**
   - 在表单页暂停，手动或使用油猴脚本填充

3. **确认操作结果**
   - 提交后暂停，验证成功消息或跳转

4. **调试问题**
   - 在出错位置暂停，检查页面状态

---

## 📸 截图管理

### 自动截图

在场景中定义截图步骤：

```javascript
const scenarios = {
  chargingOrder: {
    name: '充电订单完整流程',
    steps: [
      { type: 'navigate', url: '/charging/orders' },
      { type: 'screenshot', name: 'order-list' },  // 自动截图
      // ...
    ]
  }
};
```

### 手动截图

#### 在暂停点截图

```
⏸️  暂停点
> s
📸 截图已保存: screenshots/2026-03-05T14-30-00_pause_001.png
⏸️  暂停点
> 
```

#### 在交互模式截图

```
🎮 > screenshot my-screenshot-name
📸 截图已保存: screenshots/2026-03-05T14-30-00_my-screenshot-name.png
```

### 截图文件

**保存位置**: `tests/manual-test-helpers/playwright-semi-auto/screenshots/`

**命名规则**: 
- 带名称: `2026-03-05T14-30-00_screenshot-name.png`
- 不带名称: `2026-03-05T14-30-00_001.png`

### 截图最佳实践

1. **关键步骤截图**
   - 表单填充前后
   - 数据提交前后
   - 错误信息
   - 成功提示

2. **截图命名规范**
   - 使用描述性名称（如 `order-created`, `form-validation-error`）
   - 使用连字符分隔单词
   - 避免使用空格或特殊字符

3. **定期清理**
   - 截图文件会累积，定期清理旧截图
   ```powershell
   rm screenshots/*
   ```

---

## 🎯 典型使用场景

### 场景1：端到端业务流程测试

```powershell
# 1. 运行充电订单场景
npm run test:charging

# 执行流程：
# - 自动导航到订单列表
# - 暂停 → 人工验证列表数据
# - 自动点击"新建订单"
# - 暂停 → 使用油猴脚本填充表单（Alt+F）
# - 自动提交表单
# - 暂停 → 验证订单创建成功
# - 自动截图保存证据
```

### 场景2：探索性测试

```powershell
# 1. 启动交互模式
npm run test:interactive
# 选择 "2. 交互式模式"

# 2. 自由探索
🎮 > goto /admin/users
🎮 > screenshot users-page
🎮 > click button:has-text("添加用户")
🎮 > fill #userName test_user_001
🎮 > fill #email test@example.com
🎮 > screenshot user-form
🎮 > click button[type="submit"]
🎮 > wait .ant-message-success
🎮 > screenshot user-created
🎮 > save
🎮 > quit
```

### 场景3：回归测试

```powershell
# 1. 第一次测试时录制操作
RECORD_MODE=true npm run test:interactive
# ... 执行测试步骤 ...
🎮 > save
💾 录制已保存: recordings/regression_test_001.json

# 2. 后续回归测试时重放
npm run test:replay -- recordings/regression_test_001.json
```

### 场景4：多浏览器兼容性测试

```powershell
# Chrome
BROWSER=chromium npm run test:charging

# Firefox
BROWSER=firefox npm run test:charging

# Safari (需要 macOS)
BROWSER=webkit npm run test:charging
```

### 场景5：性能测试

```powershell
# 关闭慢速模式，全速执行
SLOW_MO=0 npm run test:charging
# 观察页面响应时间，在暂停点查看性能指标
```

---

## 🔧 高级用法

### 自定义场景

编辑 `semi-auto-tester.js`，添加新场景：

```javascript
const scenarios = {
  // ... 现有场景 ...
  
  // 新场景：用户管理
  userManagement: {
    name: '用户管理流程',
    steps: [
      { type: 'navigate', url: '/admin/users' },
      { type: 'pause', message: '验证用户列表是否显示' },
      { type: 'screenshot', name: 'user-list' },
      { type: 'click', selector: 'button:has-text("添加用户")' },
      { type: 'pause', message: '填充用户表单' },
      { type: 'screenshot', name: 'user-form' },
      { type: 'click', selector: 'button[type="submit"]' },
      { type: 'wait', selector: '.ant-message-success' },
      { type: 'pause', message: '验证用户创建成功' },
      { type: 'screenshot', name: 'user-created' },
    ]
  },
};
```

运行自定义场景：

```powershell
# 修改 package.json 添加新脚本
"test:user": "node semi-auto-tester.js",

# 设置环境变量
SCENARIO=userManagement npm run test:user
```

### 自定义选择器

使用更精确的选择器：

```javascript
// CSS 选择器
click('button.ant-btn-primary')

// 文本选择器
click('button:has-text("创建")')

// XPath 选择器
click('//button[contains(text(), "创建")]')

// 数据属性选择器（推荐）
click('[data-testid="create-button"]')
```

### 等待策略

```javascript
// 等待元素出现
{ type: 'wait', selector: '.order-list' }

// 等待网络空闲（在 navigate 后自动执行）
{ type: 'navigate', url: '/orders' }  // 默认等待 networkidle

// 等待特定时间（不推荐）
await page.waitForTimeout(3000)
```

### 条件执行

在交互模式中根据结果决定下一步：

```powershell
🎮 > goto /orders
🎮 > wait .order-list
# 如果列表为空，创建新订单
🎮 > click button:has-text("新建订单")
# 如果列表不为空，编辑第一条
# 🎮 > click tr:first-child button:has-text("编辑")
```

---

## 🐛 故障排查

### 问题1：浏览器启动失败

**错误信息**:
```
browserType.launch: Executable doesn't exist at ...
```

**解决方案**:
```powershell
# 安装浏览器
npx playwright install chromium

# 或安装所有浏览器
npx playwright install
```

---

### 问题2：找不到元素

**错误信息**:
```
Timeout 30000ms exceeded.
waiting for selector "button.create-btn"
```

**解决方案**:

1. 检查选择器是否正确
   ```powershell
   # 在浏览器开发者工具中测试选择器
   document.querySelector('button.create-btn')
   ```

2. 增加等待时间
   ```javascript
   await page.waitForSelector('button.create-btn', { timeout: 60000 })
   ```

3. 等待页面加载完成
   ```javascript
   await page.waitForLoadState('networkidle')
   ```

4. 使用更宽松的选择器
   ```javascript
   // 从精确到模糊
   'button#create-order-btn'              // 精确 ID
   'button.create-btn'                    // Class
   'button:has-text("创建")'              // 文本包含
   'button'                               // 任意 button
   ```

---

### 问题3：脚本卡在暂停点

**症状**: 按 Enter 没有反应

**解决方案**:

1. 确认终端窗口有焦点（点击终端）

2. 如果完全无响应，按 `Ctrl+C` 强制退出

3. 重新运行脚本

---

### 问题4：截图失败

**错误信息**:
```
ENOENT: no such file or directory, open 'screenshots/...'
```

**解决方案**:
```powershell
# 创建截图目录
mkdir screenshots
mkdir recordings
```

---

### 问题5：npm install 失败

**解决方案**:
```powershell
# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 清理缓存后重试
rm -r node_modules
rm package-lock.json
npm install

# 切换到 yarn
yarn install
```

---

## 📚 参考资料

### Playwright 选择器

- [官方选择器文档](https://playwright.dev/docs/selectors)
- [CSS 选择器参考](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_Selectors)
- [XPath 教程](https://www.w3schools.com/xml/xpath_intro.asp)

### Playwright API

- [Page API](https://playwright.dev/docs/api/class-page)
- [Locator API](https://playwright.dev/docs/api/class-locator)
- [Browser API](https://playwright.dev/docs/api/class-browser)

### 相关文档

- [完整使用手册](../README.md)
- [快速开始指南](../QUICKSTART.md)
- [油猴脚本安装指南](../tampermonkey/INSTALLATION.md)

---

**问题反馈**: 联系测试团队  
**更新日期**: 2026年3月5日
