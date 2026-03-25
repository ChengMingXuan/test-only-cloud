# Tampermonkey 脚本安装指南

> 油猴脚本详细安装步骤

---

## 📦 脚本列表

| 脚本文件 | 功能 | 大小 |
|---------|------|------|
| `aiops-form-autofill.user.js` | 表单自动填充助手 | ~450行 |
| `aiops-test-toolbar.user.js` | 测试工具栏 | ~550行 |

---

## 🚀 安装步骤

### 步骤一：安装 Tampermonkey 扩展

#### Chrome / Edge 用户

1. 访问 Chrome Web Store:
   ```
   https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo
   ```

2. 点击 **"添加到 Chrome"** 按钮

3. 在弹出的确认对话框中点击 **"添加扩展程序"**

4. 安装完成后，浏览器工具栏会出现 Tampermonkey 图标

#### Firefox 用户

1. 访问 Firefox Add-ons:
   ```
   https://addons.mozilla.org/zh-CN/firefox/addon/tampermonkey/
   ```

2. 点击 **"添加到 Firefox"** 按钮

3. 在弹出的权限确认中点击 **"添加"**

4. 安装完成后，工具栏会出现 Tampermonkey 图标

#### Safari 用户

1. 访问 Mac App Store:
   ```
   https://apps.apple.com/app/tampermonkey/id1482490089
   ```

2. 下载并安装

3. 在 Safari → 偏好设置 → 扩展中启用 Tampermonkey

---

### 步骤二：导入脚本

#### 方法1：从文件导入（推荐）

1. **打开管理面板**
   - 点击浏览器工具栏中的 Tampermonkey 图标
   - 选择 **"管理面板"**（Dashboard）

2. **进入实用工具**
   - 点击 **"实用工具"**（Utilities）标签

3. **导入脚本文件**
   - 点击 **"文件"** 标签下的 **"选择文件"** 按钮
   - 浏览到项目目录：
     ```
     tests/manual-test-helpers/tampermonkey/
     ```
   - 选择 `aiops-form-autofill.user.js`
   - 点击 **"安装"**

4. **重复导入**
   - 重复步骤 3，导入 `aiops-test-toolbar.user.js`

5. **完成**
   - 返回 **"已安装脚本"** 标签
   - 确认两个脚本都已列出

#### 方法2：复制粘贴安装

1. **创建新脚本**
   - 打开 Tampermonkey 管理面板
   - 点击右上角的 **"+"** 按钮

2. **清空默认内容**
   - 删除编辑器中的所有默认代码

3. **粘贴脚本内容**
   - 打开 `aiops-form-autofill.user.js` 文件
   - 复制全部内容（Ctrl+A, Ctrl+C）
   - 粘贴到 Tampermonkey 编辑器（Ctrl+V）

4. **保存脚本**
   - 点击 **"文件"** → **"保存"**
   - 或按 `Ctrl+S` (Windows/Linux) / `Cmd+S` (Mac)

5. **重复安装第二个脚本**
   - 重复步骤 1-4，安装 `aiops-test-toolbar.user.js`

#### 方法3：拖放安装

1. **打开管理面板**
   - 点击 Tampermonkey 图标 → 管理面板

2. **拖放文件**
   - 将 `.user.js` 文件直接拖到浏览器窗口
   - 或拖到 Tampermonkey 管理面板

3. **确认安装**
   - 在弹出的安装确认页面点击 **"安装"**

---

### 步骤三：验证安装

#### 检查脚本是否启用

1. 打开 Tampermonkey 管理面板
2. 查看 **"已安装脚本"** 列表
3. 确认两个脚本的状态：
   - **启用状态**（开关是绿色的）✅
   - 如果是灰色，点击开关启用

#### 检查脚本匹配规则

确认脚本的 `@match` 规则包含你要测试的域名：

**aiops-form-autofill.user.js**:
```javascript
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
```

**aiops-test-toolbar.user.js**:
```javascript
// @match        http://localhost:8000/*
// @match        http://localhost:*/*
```

> 如果你的域名不同，需要修改 `@match` 规则

---

### 步骤四：测试脚本

#### 测试脚本 #1：表单自动填充

1. 访问 AIOPS 平台：http://localhost:8000
2. 登录系统
3. 导航到任何表单页面（如"新建充电订单"）
4. 查看页面右下角是否出现 3 个浮动按钮：
   - 🚀 智能填充
   - 🗑️ 清空表单
   - 🎲 随机数据

5. **测试功能**：
   - 点击 "智能填充" 按钮
   - 或按快捷键 `Alt+F`
   - 表单字段应自动填充测试数据

#### 测试脚本 #2：测试工具栏

1. 继续停留在 AIOPS 平台
2. 查看页面右上角是否出现悬浮工具栏
3. 工具栏应显示：
   - 当前用户信息
   - 当前租户信息
   - 快速切换下拉框
   - 操作按钮

4. **测试功能**：
   - 按快捷键 `Alt+T` 隐藏/显示工具栏
   - 点击工具栏上的按钮测试功能
   - 尝试切换用户/租户

---

## 🔧 高级配置

### 修改匹配规则

如果你的测试环境域名不同，需要修改 `@match` 规则：

1. 打开 Tampermonkey 管理面板
2. 点击要编辑的脚本
3. 修改 `@match` 行：
   ```javascript
   // @match        https://your-test-domain.com/*
   // @match        http://localhost:8080/*
   ```
4. 保存（Ctrl+S）

### 添加更多测试用户

编辑 `aiops-test-toolbar.user.js`：

```javascript
const CONFIG = {
  testUsers: [
    { id: '00000000-0000-0000-0000-000000000001', name: 'SUPER_ADMIN', role: '超级管理员', token: '' },
    { id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', name: 'your_user', role: '自定义角色', token: '' },
    // 添加更多用户...
  ],
};
```

### 添加更多测试租户

编辑 `aiops-test-toolbar.user.js`：

```javascript
const CONFIG = {
  testTenants: [
    { id: '00000000-0000-0000-0000-000000000001', name: 'JGSY集团', code: 'JGSY' },
    { id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', name: '自定义租户', code: 'CUSTOM' },
    // 添加更多租户...
  ],
};
```

### 自定义工具栏位置

编辑 `aiops-test-toolbar.user.js`：

```javascript
const CONFIG = {
  position: 'top-right', // 可选: top-right, top-left, bottom-right, bottom-left
};
```

### 自定义快捷键

编辑脚本中的快捷键监听代码：

**表单填充快捷键** (`aiops-form-autofill.user.js`):
```javascript
function setupHotkeys() {
  document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key === 'f') { // 修改为其他按键
      e.preventDefault();
      FormFillers.smartFill();
    }
    // ...
  });
}
```

---

## 🐛 故障排查

### 问题1：脚本不生效

**症状**: 访问 AIOPS 平台，没有看到浮动按钮或工具栏

**解决方案**:

1. ✅ 检查 Tampermonkey 是否已安装
   - 浏览器工具栏应有 Tampermonkey 图标

2. ✅ 检查脚本是否已启用
   - 打开管理面板
   - 确认开关为绿色

3. ✅ 检查 URL 是否匹配
   - 当前页面 URL 是否匹配 `@match` 规则
   - 如不匹配，修改 `@match` 规则

4. ✅ 清除浏览器缓存并刷新
   - 按 `Ctrl+Shift+R` 强制刷新

5. ✅ 查看浏览器控制台是否有错误
   - 按 `F12` 打开开发者工具
   - 切换到 "Console" 标签
   - 查看是否有红色错误信息

### 问题2：脚本功能异常

**症状**: 脚本加载了，但功能不工作

**解决方案**:

1. ✅ 查看控制台错误
   - 按 `F12` 打开控制台
   - 查找错误信息

2. ✅ 检查页面结构是否变化
   - 如果平台更新，选择器可能失效
   - 需要更新脚本中的选择器

3. ✅ 检查脚本权限
   - 确认脚本有足够的权限（`@grant` 指令）

4. ✅ 重新安装脚本
   - 删除旧脚本
   - 重新导入

### 问题3：快捷键不生效

**症状**: 按快捷键没有反应

**解决方案**:

1. ✅ 确认页面已加载完成
   - 等待页面完全加载后再按快捷键

2. ✅ 检查是否有快捷键冲突
   - 某些网站或浏览器可能占用了相同的快捷键
   - 尝试修改脚本中的快捷键

3. ✅ 确认焦点在页面上
   - 点击页面任意位置
   - 不要让焦点在浏览器地址栏或开发者工具中

### 问题4：脚本卡顿或性能问题

**解决方案**:

1. ✅ 关闭不需要的脚本
   - 只保留必要的脚本启用

2. ✅ 减少性能监控频率
   - 编辑 `aiops-test-toolbar.user.js`
   - 修改 `setInterval` 的间隔时间（默认 3 秒）

3. ✅ 清理浏览器缓存
   - 清理 localStorage
   - 清理 cookies

---

## 📋 卸载脚本

如果需要卸载脚本：

1. 打开 Tampermonkey 管理面板
2. 找到要卸载的脚本
3. 点击右侧的 **垃圾桶图标** 🗑️
4. 确认删除

---

## 🔄 更新脚本

当脚本有新版本时：

1. **自动更新**（如果配置了 `@updateURL`）:
   - Tampermonkey 会自动检查更新
   - 或手动点击 "检查更新"

2. **手动更新**:
   - 删除旧版本脚本
   - 按照安装步骤重新导入新版本

---

## 📚 相关文档

- [完整使用手册](../README.md)
- [快速开始指南](../QUICKSTART.md)
- [Tampermonkey 官方文档](https://www.tampermonkey.net/documentation.php)

---

**问题反馈**: 联系测试团队  
**更新日期**: 2026年3月5日
