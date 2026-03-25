# 5分钟快速开始

> 快速安装并体验人工测试辅助工具

---

## 🎯 目标

5分钟内完成：
1. ✅ 安装 2 个油猴脚本
2. ✅ 安装 Playwright 半自动脚本
3. ✅ 运行第一个测试场景

---

## ⚡ 第一步：安装油猴扩展（1分钟）

### Chrome/Edge 用户

1. 访问 https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo
2. 点击"添加到 Chrome"
3. 确认安装

### Firefox 用户

1. 访问 https://addons.mozilla.org/zh-CN/firefox/addon/tampermonkey/
2. 点击"添加到 Firefox"
3. 确认安装

---

## ⚡ 第二步：安装油猴脚本（2分钟）

### 方法1：从文件导入（推荐）

1. 点击浏览器工具栏中的 **Tampermonkey 图标**
2. 选择 **"管理面板"**
3. 点击 **"实用工具"** 标签
4. 选择 **"从文件导入"**
5. 依次导入两个脚本：
   ```
   tests/manual-test-helpers/tampermonkey/aiops-form-autofill.user.js
   tests/manual-test-helpers/tampermonkey/aiops-test-toolbar.user.js
   ```

### 方法2：复制粘贴

1. 打开 Tampermonkey 管理面板
2. 点击 **"+"** 按钮（新建脚本）
3. 删除默认内容
4. 打开 `aiops-form-autofill.user.js`，复制所有内容，粘贴
5. `Ctrl+S` 保存
6. 重复步骤 2-5 安装第二个脚本 `aiops-test-toolbar.user.js`

---

## ⚡ 第三步：验证油猴脚本（30秒）

1. 访问 AIOPS 平台：https://aiops.jgsy.com
2. 登录系统
3. 查看右上角是否出现 **测试工具栏**
4. 导航到任意表单页面（如创建充电订单）
5. 查看右下角是否出现 **3个浮动按钮**（智能填充/清空表单/随机数据）

### ✅ 验证成功标志

- 右上角有悬浮工具栏
- 右下角有3个浮动按钮
- 按 `Alt+T` 可隐藏/显示工具栏
- 按 `Alt+F` 可自动填充表单

---

## ⚡ 第四步：安装 Playwright 半自动脚本（1分钟）

打开 PowerShell/终端，执行：

```powershell
cd tests/manual-test-helpers/playwright-semi-auto
npm install
```

> 如果安装慢，使用淘宝镜像：
> ```powershell
> npm install --registry=https://registry.npmmirror.com
> ```

---

## ⚡ 第五步：运行第一个测试（30秒）

```powershell
npm run test:charging
```

### 预期过程

```
🚀 启动浏览器...
✅ 浏览器已启动
📍 导航到充电订单页面...
============================================================
⏸️  暂停点
📋 验证页面是否正常加载
按 Enter 继续执行，输入 s 截图，输入 q 退出...
============================================================
> 
```

**操作**:
1. 观察浏览器中的页面是否正常
2. 按 **Enter** 继续
3. 脚本会自动点击"新建订单"按钮
4. 再次暂停，提示你填充表单
5. 按 **Alt+F**（油猴脚本会自动填充）
6. 按 **Enter** 继续
7. 脚本自动提交表单
8. 验证订单创建成功
9. 测试完成，浏览器自动关闭

---

## 🎉 完成！

你已经成功安装并运行了所有人工测试辅助工具！

---

## 📖 下一步

### 学习快捷键

| 快捷键 | 功能 |
|-------|------|
| `Alt+T` | 显示/隐藏测试工具栏 |
| `Alt+F` | 智能填充表单 |
| `Alt+C` | 清空表单 |
| `Alt+R` | 随机数据填充 |
| `Alt+S` | 提交表单 |

### 尝试更多场景

```powershell
cd tests/manual-test-helpers/playwright-semi-auto

# 工单场景
npm run test:workorder

# 设备管理场景
npm run test:device

# 交互式模式（自由控制）
npm run test:interactive
```

### 油猴脚本功能探索

**测试工具栏**（右上角）:
- 切换测试用户
- 切换测试租户
- 查看性能监控
- 导出测试日志

**表单填充助手**（右下角）:
- 智能识别页面并填充
- 生成随机测试数据
- 快速清空表单

---

## ❓ 遇到问题？

### Q: 油猴脚本不显示

**A**: 
1. 检查 Tampermonkey 图标是否有红色数字（已启用脚本数量）
2. 刷新页面（F5）
3. 检查脚本是否启用（管理面板中开关应为绿色）

### Q: npm install 失败

**A**:
```powershell
# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 或清理缓存后重试
rm -r node_modules
npm install
```

### Q: Playwright 浏览器启动失败

**A**:
```powershell
# 安装浏览器
npx playwright install chromium
```

---

## 📚 完整文档

详细使用指南请阅读：[README.md](README.md)

---

**问题反馈**: 联系测试团队  
**更新日期**: 2026年3月5日
