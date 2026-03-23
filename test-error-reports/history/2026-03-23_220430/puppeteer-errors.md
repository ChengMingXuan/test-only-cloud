# 🤖 Puppeteer 测试错误报告

- **执行时间**: 2026-03-23 22:04:30 UTC
- **Git Commit**: 75eee389b707d0c3c5489029b23ccbe8d9587442
- **触发方式**: push

## 失败详情

```
FAIL tests/v318-incremental-render.test.js
      at Resolver._throwModNotFoundError (node_modules/jest-resolve/build/resolver.js:427:11)
FAIL tests/generated/render-041-charging-pile-detail.test.js (53.358 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-041-charging-pile-detail.test.js:405:18)
FAIL tests/generated/render-067-ai-chat.test.js (58.837 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 312 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m2000[39m)[33m;[39m
     [90m 313 |[39m       expect(rejections[33m.[39mlength)[33m.[39mtoBeLessThanOrEqual([35m3[39m)[33m;[39m
      at Object.waitForTimeout (tests/generated/render-067-ai-chat.test.js:312:18)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 324 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m1000[39m)[33m;[39m
     [90m 326 |[39m       expect(bodyExists)[33m.[39mtoBeTruthy()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-067-ai-chat.test.js:324:18)
FAIL tests/generated/render-109-blockchain-verify.test.js (51.424 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-109-blockchain-verify.test.js:405:18)
FAIL tests/generated/render-015-menus-create.test.js (51.47 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-015-menus-create.test.js:405:18)
FAIL tests/generated/render-108-blockchain-certs.test.js (51.547 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-108-blockchain-certs.test.js:405:18)
FAIL tests/generated/render-074-analytics-custom.test.js (51.528 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-074-analytics-custom.test.js:405:18)
FAIL tests/generated/render-039-charging-order-detail.test.js (51.517 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-039-charging-order-detail.test.js:405:18)
FAIL tests/generated/render-017-permissions-list.test.js (51.547 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-017-permissions-list.test.js:405:18)
FAIL tests/generated/render-096-settlement-reconcile.test.js (51.502 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-096-settlement-reconcile.test.js:405:18)
FAIL tests/generated/render-087-rule-templates.test.js (51.475 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-087-rule-templates.test.js:405:18)
FAIL tests/generated/render-078-dt-simulate.test.js (51.449 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-078-dt-simulate.test.js:405:18)
FAIL tests/generated/render-072-analytics-indicators.test.js (51.456 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-072-analytics-indicators.test.js:405:18)
FAIL tests/generated/render-016-resources-list.test.js (51.439 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-016-resources-list.test.js:405:18)
FAIL tests/generated/render-010-roles-create.test.js (51.49 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-010-roles-create.test.js:405:18)
FAIL tests/generated/render-007-users-create.test.js (51.457 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-007-users-create.test.js:405:18)
FAIL tests/generated/render-093-workorder-templates.test.js (51.403 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-093-workorder-templates.test.js:405:18)
FAIL tests/generated/render-080-dt-monitor.test.js (51.425 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-080-dt-monitor.test.js:405:18)
FAIL tests/generated/render-070-analytics-dashboard.test.js (51.444 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
      at Object.waitForTimeout (tests/generated/render-070-analytics-dashboard.test.js:405:18)
FAIL tests/generated/render-054-energy-orchestrator.test.js (51.455 s)
    TypeError: page.waitForTimeout is not a function
    [31m[1m>[22m[39m[90m 405 |[39m       [36mawait[39m page[33m.[39mwaitForTimeout([35m500[39m)[33m;[39m
     [90m 407 |[39m       expect(body)[33m.[39mnot[33m.[39mtoBeNull()[33m;[39m
```
