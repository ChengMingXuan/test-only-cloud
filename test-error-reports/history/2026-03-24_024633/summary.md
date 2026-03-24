# 全量测试汇总报告

- **执行时间**: 2026-03-24 02:46:33 UTC
- **Git Commit**: 2387a9a4fd97127a800c6327b29067c3d4372742
- **测试级别**: full
- **触发方式**: push

## 各工具执行状态

| 工具 | 标准用例 | 状态 | 说明 |
|------|----------|------|------|
| pytest | 57774 | ⚠️ | 未收集到结果 |
| cypress | 9877 | ❌ | 执行 130, 通过 116, 失败 14 |
| playwright | 11093 | ⚠️ | 未收集到结果 |
| puppeteer | 8137 | ❌ | 执行 8576, 通过 8362, 失败 214 |
| selenium | 6540 | ⚠️ | 未收集到结果 |
| k6 | 3651 | ⚠️ | 未收集到结果 |
| integration | 1999 | ⚠️ | 未收集到结果 |

## 综合统计

- **总执行**: 8706
- **通过**: 8478
- **失败**: 228
- **通过率**: 97.4%

## 失败详情

### pytest
```
api/test_account_charging_identity_enhanced.py::TestWalletService::test_get_or_create_wallet FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestWalletService::test_get_balance FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestWalletService::test_wallet_transaction_history FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestMembershipBenefitAutoActivation::test_trigger_birthday_benefits FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestMembershipBenefitAutoActivation::test_trigger_anniversary_benefits FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestMembershipBenefitAutoActivation::test_get_user_benefits FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_create_order FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_update_order_status FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_calculate_order_fee FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_get_current_auth FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_get_auth_history FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_is_verified FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestUserService::test_create_user FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestUserService::test_update_user FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestUserService::test_change_password FAILED [  0%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_start_session FAILED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_stop_session FAILED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_send_command FAILED [ 44%]
api/test_dag_workflow_api.py::TestDagWorkflowList::test_list_workflows_contains_seven_builtins FAILED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowDetail::test_get_workflow_nodes_structure FAILED [ 45%]
```

### cypress
```
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '<input#username.ant-input>' to be 'visible'
[0m[31m     AssertionError: Timed out retrying after 15000ms: expected 'http://127.0.0.1:8000/station/list' to include '/user/login'[0m[90m
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '[ <table.ant-table>, 66 more... ]' to be 'visible'
[0m[31m     AssertionError: Timed out retrying after 10000ms: Expected to find element: `.ant-drawer:not(.drawer-hidden)`, but never found it.[0m[90m
[0m[31m     AssertionError: Timed out retrying after 10000ms: Expected to find content: '新建围栏' but never did.[0m[90m
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getTools`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.wait()` timed out waiting `10000ms` for the 1st request to the route: `getHealth`. No request ever occurred.
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:
[0m[31m     CypressError: `cy.type()` cannot accept an empty string. You need to actually type something.
```

### playwright
```
  ✘   7546 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:51:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (229ms)
  ✘   7547 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:92:7 › 碳认证完整业务流程 › 证书转让流程 (371ms)
  ✘   7548 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:51:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #1) (431ms)
  ✘   7549 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:92:7 › 碳认证完整业务流程 › 证书转让流程 (retry #1) (363ms)
  ✘   7550 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:51:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #2) (371ms)
  ✘   7551 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:92:7 › 碳认证完整业务流程 › 证书转让流程 (retry #2) (360ms)
  ✘   7552 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:108:7 › 碳认证完整业务流程 › CCER项目注册流程 (352ms)
  ✘   7553 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:134:7 › 有序充电完整业务流程 › 排队到调度完整流程 (344ms)
  ✘   7554 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:108:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #1) (375ms)
  ✘   7555 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:134:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #1) (356ms)
  ✘   7556 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:108:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #2) (337ms)
  ✘   7557 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:134:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #2) (371ms)
  ✘   7558 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:169:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (380ms)
  ✘   7559 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:222:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (355ms)
  ✘   7560 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:169:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #1) (349ms)
  ✘   7561 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:222:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (retry #1) (360ms)
  ✘   7562 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:169:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #2) (336ms)
  ✘   7563 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:222:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (retry #2) (348ms)
  ✘   7564 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:245:7 › 微电网能耗报表业务流程 › 日报表和月报表切换 (375ms)
  ✘   7565 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:279:7 › CIM协议配置业务流程 › 配置CIM端点并查看调度记录 (351ms)
```

### puppeteer
```
FAIL tests/v318-incremental-render.test.js
      at Resolver._throwModNotFoundError (node_modules/jest-resolve/build/resolver.js:427:11)
FAIL tests/generated/render-041-charging-pile-detail.test.js (52.921 s)
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-067-ai-chat.test.js (58.442 s)
    TypeError: page.waitForTimeout is not a function
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-109-blockchain-verify.test.js (51.653 s)
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-015-menus-create.test.js (51.672 s)
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-108-blockchain-certs.test.js (51.647 s)
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-074-analytics-custom.test.js (51.627 s)
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-039-charging-order-detail.test.js (51.609 s)
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-017-permissions-list.test.js (51.634 s)
    TypeError: page.waitForTimeout is not a function
FAIL tests/generated/render-096-settlement-reconcile.test.js (51.654 s)
```

### selenium
```
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
E   TypeError: WebDriver.__init__() got an unexpected keyword argument 'desired_capabilities'
```

