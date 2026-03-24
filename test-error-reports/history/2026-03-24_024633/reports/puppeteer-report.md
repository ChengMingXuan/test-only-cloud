# 🤖 Puppeteer（渲染/性能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 02:46:30 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 8137 |
| 实际执行 | 8576 |
| ✅ 通过 | 8362 |
| ❌ 失败 | 214 |
| ⏭️ 跳过 | 0 |
| 通过率 | 97.5% |
| 耗时(s) | 0 |

## 发布门禁

- **状态**：❌ 有失败 (214)
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
FAIL tests/v318-incremental-render.test.js
  ● Test suite failed to run

    Cannot find module 'chai' from 'tests/v318-incremental-render.test.js'
--
      at Resolver._throwModNotFoundError (node_modules/jest-resolve/build/resolver.js:427:11)
      at Object.require (tests/v318-incremental-render.test.js:12:20)

FAIL tests/generated/render-041-charging-pile-detail.test.js (52.921 s)
  ● [渲染测试] 充电桩详情 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-067-ai-chat.test.js (58.442 s)
  ● [渲染测试] AI智能对话 › 异常处理 › [E002] 未捕获Promise异常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 310 |[39m       page[33m.[39mon([32m'pageerror'[39m[33m,[39m err [33m=>[39m rejections[33m.[39mpush(err[33m.[39mmessage))[33m;[39m
     [90m 311 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m[33m,[39m timeout[33m:[39m [35m10000[39m })[33m;[39m
--
    TypeError: page.waitForTimeout is not a function

    [0m [90m 322 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m[33m,[39m timeout[33m:[39m [35m10000[39m })[33m;[39m
     [90m 323 |[39m       [36mawait[39m page[33m.[39msetOfflineMode([36mtrue[39m)[33m;[39m
--
FAIL tests/generated/render-109-blockchain-verify.test.js (51.653 s)
  ● [渲染测试] 区块链验证 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-015-menus-create.test.js (51.672 s)
  ● [渲染测试] 菜单创建 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-108-blockchain-certs.test.js (51.647 s)
  ● [渲染测试] 区块链存证 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-074-analytics-custom.test.js (51.627 s)
  ● [渲染测试] 自定义分析 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-039-charging-order-detail.test.js (51.609 s)
  ● [渲染测试] 订单详情 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-017-permissions-list.test.js (51.634 s)
  ● [渲染测试] 权限列表 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-096-settlement-reconcile.test.js (51.654 s)
  ● [渲染测试] 对账管理 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-087-rule-templates.test.js (51.639 s)
  ● [渲染测试] 规则模板 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-078-dt-simulate.test.js (51.584 s)
  ● [渲染测试] 仿真模拟 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-072-analytics-indicators.test.js (51.579 s)
  ● [渲染测试] 指标管理 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-016-resources-list.test.js (51.601 s)
  ● [渲染测试] 资源列表 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-010-roles-create.test.js (51.574 s)
  ● [渲染测试] 角色创建 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-007-users-create.test.js (51.558 s)
  ● [渲染测试] 用户创建 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-093-workorder-templates.test.js (51.572 s)
  ● [渲染测试] 工单模板 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-080-dt-monitor.test.js (51.552 s)
  ● [渲染测试] 孪生监控 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-070-analytics-dashboard.test.js (51.566 s)
  ● [渲染测试] 数据大屏 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-054-energy-orchestrator.test.js (51.577 s)
  ● [渲染测试] 调度中心 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-098-settlement-reports.test.js (51.579 s)
  ● [渲染测试] 结算报表 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-097-settlement-invoice.test.js (51.559 s)
  ● [渲染测试] 发票管理 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-094-settlement-billing.test.js (51.557 s)
  ● [渲染测试] 账单管理 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-081-dt-config.test.js (51.576 s)
  ● [渲染测试] 孪生配置 › 异常恢复 › [X005] 窗口大小变化正常

    TypeError: page.waitForTimeout is not a function

    [0m [90m 403 |[39m       [36mawait[39m page[33m.[39mgoto([33mPAGE_URL[39m[33m,[39m { waitUntil[33m:[39m [32m'networkidle2'[39m })[33m;[39m
     [90m 404 |[39m       [36mawait[39m page[33m.[39msetViewport({ width[33m:[39m [35m800[39m[33m,[39m height[33m:[39m [35m600[39m })[33m;[39m
--
FAIL tests/generated/render-077-dt-scenes.test.js (51.628 s)
  ● [渲染测试] 场景管理 › 异常恢复 › [X005] 窗口大小变化正常
```
