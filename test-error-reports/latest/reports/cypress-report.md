# 🌲 Cypress（UI交互测试） — 测试报告

> 来源：GitHub Actions CI | 级别：smoke | 2026-03-23 22:19:32 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 9877 |
| 实际执行 | 29 |
| ✅ 通过 | 28 |
| ❌ 失败 | 1 |
| ⏭️ 跳过 | 0 |
| 通过率 | 96.55% |
| 耗时(s) | 0 |

## 发布门禁

- **状态**：❌ 有失败 (1)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `75eee389b707d0c3c5489029b23ccbe8d9587442` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | smoke |

## 失败详情

```
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '<input#username.ant-input>' to be 'visible'

This element `<input#username.ant-input>` is not visible because its parent `<div#page-login.hidden>` has CSS property: `display: none`[0m[90m
      at Context.eval (webpack://aiops-cypress-tests/./e2e/56-ai-iotcloud-chat.cy.js:32:30)
--
[0m[31m     AssertionError: Timed out retrying after 15000ms: expected 'http://127.0.0.1:8000/station/list' to include '/user/login'[0m[90m
      at Context.eval (webpack://aiops-cypress-tests/./e2e/66-compliance-security.cy.js:17:31)
[0m
[0m  2) 等保三级合规 - 认证与鉴权
--
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '[ <table.ant-table>, 66 more... ]' to be 'visible'

This element `[ <table.ant-table>, 66 more... ]` is not visible because its parent `<div#content-station.page-content.hidden>` has CSS property: `display: none`[0m[90m
      at Context.eval (webpack://aiops-cypress-tests/./e2e/67-service-mesh.cy.js:79:31)
--
[0m[31m     AssertionError: Timed out retrying after 10000ms: Expected to find element: `.ant-drawer:not(.drawer-hidden)`, but never found it.[0m[90m
      at Context.eval (webpack://aiops-cypress-tests/./e2e/charging.cy.js:88:66)
[0m

--
[0m[31m     AssertionError: Timed out retrying after 10000ms: Expected to find content: '新建围栏' but never did.[0m[90m
      at Context.eval (webpack://aiops-cypress-tests/./e2e/incremental-geofence-ai-coldarchive.cy.js:43:11)
[0m
```
