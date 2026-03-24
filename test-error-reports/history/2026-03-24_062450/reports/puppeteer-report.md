# 🤖 Puppeteer（渲染/性能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 06:24:50 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 8137 |
| 实际执行 | 8612 |
| ✅ 通过 | 8585 |
| ❌ 失败 | 27 |
| ⏭️ 跳过 | 0 |
| 通过率 | 99.69% |
| 耗时(s) | 0 |

## 发布门禁

- **状态**：❌ 有失败 (27)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `6f232d004bed373a4783d65def5e616c54dd134a` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
FAIL tests/v318-incremental-render.test.js (19.832 s)
  ● v3.18 增量功能 - 渲染测试 › 碳认证页面渲染 › I-REC证书列表页面应正确渲染表格

    net::ERR_CONNECTION_REFUSED at http://localhost:3000/carbon/irec/certificates
--
FAIL tests/generated/render-067-ai-chat.test.js (62.28 s)
  ● [渲染测试] AI智能对话 › 异常处理 › [E006] 快速连续导航不崩溃

    net::ERR_ABORTED at http://localhost:8000/ai/chat
--
FAIL tests/v318-supplement-render.test.js
  ● v3.18 补充模块 - 渲染测试 › 移动端登录页渲染 › 移动端页面应正确适配手机分辨率

    TypeError: Cannot read properties of null (reading 'scrollWidth')

      at evaluate (evaluate at Object.<anonymous> (tests/v318-supplement-render.test.js:83:36), <anonymous>:0:21)
      at ExecutionContext.#evaluate (node_modules/puppeteer-core/src/cdp/ExecutionContext.ts:456:34)
--
FAIL tests/v246-security-switches.test.js
  ● [v2.4.6][SEC-PP] 安全响应头 - 浏览器实际接收 › [SEC-PP01] X-Content-Type-Options: nosniff

    expect(received).toBe(expected) // Object.is equality
--
FAIL tests/v318-incremental-render.test.js (19.832 s)
  ● v3.18 增量功能 - 渲染测试 › 碳认证页面渲染 › I-REC证书列表页面应正确渲染表格

    net::ERR_CONNECTION_REFUSED at http://localhost:3000/carbon/irec/certificates
--
FAIL tests/generated/render-067-ai-chat.test.js (62.28 s)
  ● [渲染测试] AI智能对话 › 异常处理 › [E006] 快速连续导航不崩溃

    net::ERR_ABORTED at http://localhost:8000/ai/chat
--
FAIL tests/v318-supplement-render.test.js
  ● v3.18 补充模块 - 渲染测试 › 移动端登录页渲染 › 移动端页面应正确适配手机分辨率

    TypeError: Cannot read properties of null (reading 'scrollWidth')

      at evaluate (evaluate at Object.<anonymous> (tests/v318-supplement-render.test.js:83:36), <anonymous>:0:21)
      at ExecutionContext.#evaluate (node_modules/puppeteer-core/src/cdp/ExecutionContext.ts:456:34)
--
FAIL tests/v246-security-switches.test.js
  ● [v2.4.6][SEC-PP] 安全响应头 - 浏览器实际接收 › [SEC-PP01] X-Content-Type-Options: nosniff

    expect(received).toBe(expected) // Object.is equality
```
