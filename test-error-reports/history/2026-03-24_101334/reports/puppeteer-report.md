# 🤖 Puppeteer（渲染/性能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 10:13:18 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 8137 |
| 实际执行 | 8612 |
| ✅ 通过 | 8586 |
| ❌ 失败 | 26 |
| ⏭️ 跳过 | 0 |
| 通过率 | 99.7% |
| 耗时(s) | 0 |

## 发布门禁

- **状态**：❌ 有失败 (26)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `95e9dd1ad48744b2ac9c82f7bc5114d19085de42` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
FAIL tests/v318-incremental-render.test.js (21.624 s)
  ● v3.18 增量功能 - 渲染测试 › 碳认证页面渲染 › I-REC证书列表页面应正确渲染表格

    net::ERR_CONNECTION_REFUSED at http://localhost:3000/carbon/irec/certificates
--
FAIL tests/generated/render-067-ai-chat.test.js (64.406 s)
  ● [渲染测试] AI智能对话 › 异常处理 › [E006] 快速连续导航不崩溃

    net::ERR_ABORTED at http://localhost:8000/ai/chat
--
FAIL tests/v246-security-switches.test.js
  ● [v2.4.6][SEC-PP] 安全响应头 - 浏览器实际接收 › [SEC-PP01] X-Content-Type-Options: nosniff

    expect(received).toBe(expected) // Object.is equality
--
FAIL tests/v318-incremental-render.test.js (21.624 s)
  ● v3.18 增量功能 - 渲染测试 › 碳认证页面渲染 › I-REC证书列表页面应正确渲染表格

    net::ERR_CONNECTION_REFUSED at http://localhost:3000/carbon/irec/certificates
--
FAIL tests/generated/render-067-ai-chat.test.js (64.406 s)
  ● [渲染测试] AI智能对话 › 异常处理 › [E006] 快速连续导航不崩溃

    net::ERR_ABORTED at http://localhost:8000/ai/chat
--
FAIL tests/v246-security-switches.test.js
  ● [v2.4.6][SEC-PP] 安全响应头 - 浏览器实际接收 › [SEC-PP01] X-Content-Type-Options: nosniff

    expect(received).toBe(expected) // Object.is equality
```
