# 🌲 Cypress（UI交互测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 03:58:20 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 9877 |
| 实际执行 | 626 |
| ✅ 通过 | 625 |
| ❌ 失败 | 1 |
| ⏭️ 跳过 | 0 |
| 通过率 | 99.84% |
| 耗时(s) | 0 |

## 发布门禁

- **状态**：❌ 有失败 (1)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `d7cd74e2b862e40637cac72d93b9bfb18862aae5` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '<input#username.ant-input>' to be 'visible'

This element `<input#username.ant-input>` is not visible because its parent `<div#page-login.hidden>` has CSS property: `display: none`[0m[90m
      at Context.eval (webpack://aiops-cypress-tests/./e2e/56-ai-iotcloud-chat.cy.js:32:30)
```
