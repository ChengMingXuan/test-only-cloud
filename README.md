# 🧪 JGSY.AGI 测试专用仓库

> **仅存放测试脚本，严禁上传业务代码、配置、密钥**

## 概述

本仓库为 JGSY.AGI 平台的**测试专用公开仓库**，利用 GitHub Actions 免费额度执行自动化测试。

## 测试工具矩阵

| 工具 | 用例数 | 目录 | 说明 |
|------|--------|------|------|
| pytest | 57,774 | `testing/tests/api/` | API 自动化 + 单元测试 |
| Cypress | 9,877 | `testing/tests/cypress-tests/` | UI 交互测试 |
| Playwright | 11,093 | `testing/tests/playwright-tests/` | E2E 端到端 |
| Puppeteer | 8,137 | `testing/tests/puppeteer-tests/` | 性能 + 视觉回归 |
| Selenium | 6,540 | `testing/tests/selenium-tests/` | 多浏览器兼容 |
| k6 | 3,651 | `testing/k6/` | 性能压测 |

## 使用方式

### 手动触发测试

1. 进入 [Actions 页面](../../actions)
2. 选择对应的测试工作流
3. 点击 "Run workflow"
4. 选择测试级别（smoke / standard / full）

### 自动触发

每次 push 到 `main` 分支时，自动运行受影响的测试工具。

### 查看错误报告

测试完成后，错误报告自动提交到 `test-error-reports/latest/` 目录。

## 分支规则

- 主分支：`main`
- 独立项目，无需合并
- 仅通过本地覆盖更新
- 不接受 Pull Request

## 安全

- 无业务代码
- 无数据库连接配置
- 无密钥/Token
- 测试 100% Mock，不依赖外部服务
