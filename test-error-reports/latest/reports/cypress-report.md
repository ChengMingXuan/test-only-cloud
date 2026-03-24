# 🌲 Cypress（UI交互测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 02:46:30 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 9877 |
| 实际执行 | 130 |
| ✅ 通过 | 116 |
| ❌ 失败 | 14 |
| ⏭️ 跳过 | 0 |
| 通过率 | 89.23% |
| 耗时(s) | 0 |

## 发布门禁

- **状态**：❌ 有失败 (14)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `2387a9a4fd97127a800c6327b29067c3d4372742` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

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

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<div class="ant-select ant-select-selector">...</div>`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.

https://on.cypress.io/wait[0m[90m
      at cypressErr (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:76065:18)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: `cy.type()` cannot accept an empty string. You need to actually type something.

https://on.cypress.io/type[0m[90m
      at Context.type (http://127.0.0.1:8000/__cypress/runner/cypress_runner.js:115388:68)
--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<input type="checkbox" checked="">`

--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<input type="checkbox" checked="">`

--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<input type="checkbox" checked="">`

--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<input type="checkbox" checked="">`

--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<input type="checkbox" checked="">`

--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<input type="checkbox" checked="">`

--
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:

`<input type="checkbox" checked="">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input type="text" name="username" id="username" class="ant-input" placeholder="请输入用户名" autocomplete="off">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input class="ant-input" placeholder="请输入名称">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input class="ant-input" placeholder="请输入名称">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input class="ant-input" placeholder="请输入名称">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input class="ant-input" placeholder="请输入名称">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input class="ant-input" placeholder="请输入名称">`

--
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:

`<input class="ant-input" placeholder="请输入名称">`

--
```
