# 全量测试汇总报告

- **执行时间**: 2026-03-24 06:24:50 UTC
- **Git Commit**: 6f232d004bed373a4783d65def5e616c54dd134a
- **测试级别**: full
- **触发方式**: push

## 各工具执行状态

| 工具 | 标准用例 | 状态 | 说明 |
|------|----------|------|------|
| pytest | 57774 | ⚠️ | 未收集到结果 |
| cypress | 9877 | ❌ | 执行 130, 通过 116, 失败 14 |
| playwright | 11093 | ⚠️ | 未收集到结果 |
| puppeteer | 8137 | ❌ | 执行 8612, 通过 8585, 失败 27 |
| selenium | 6540 | ⚠️ | 未收集到结果 |
| k6 | 3651 | ⚠️ | 未收集到结果 |
| integration | 1999 | ⚠️ | 未收集到结果 |

## 综合统计

- **总执行**: 8742
- **通过**: 8701
- **失败**: 41
- **通过率**: 99.5%

## 失败详情

### pytest
```
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-users/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-configs/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-products/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-orders/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-invoices/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-payments/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-recharges/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-transactions/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-bills/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/dashboards/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/charts/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/datasets/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/indicators/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-configs/export] 
```

### cypress
```
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '<input#username.ant-input>' to be 'visible'
[0m[31m     AssertionError: Timed out retrying after 15000ms: expected 'http://127.0.0.1:8000/station/list' to include '/user/login'[0m[90m
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '[ <table.ant-table>, 66 more... ]' to be 'visible'
[0m[31m     AssertionError: Timed out retrying after 10000ms: Expected to find element: `.ant-drawer:not(.drawer-hidden)`, but never found it.[0m[90m
[0m[31m     AssertionError: Timed out retrying after 10000ms: Expected to find content: '新建围栏' but never did.[0m[90m
      [31mAssertionError: Timed out retrying after 10000ms: Too many elements found. Found '226', expected '6'.[0m
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.clear()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10000ms: `cy.type()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
[0m[31m     CypressError: Timed out retrying after 10050ms: `cy.click()` failed because this element is not visible:
```

### playwright
```
  ✘   7546 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:128:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (5.8s)
  ✘   7547 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:169:7 › 碳认证完整业务流程 › 证书转让流程 (5.9s)
  ✘   7548 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:185:7 › 碳认证完整业务流程 › CCER项目注册流程 (6.6s)
  ✘   7549 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:211:7 › 有序充电完整业务流程 › 排队到调度完整流程 (6.5s)
  ✘   7550 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:128:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #1) (6.1s)
  ✘   7551 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:169:7 › 碳认证完整业务流程 › 证书转让流程 (retry #1) (6.2s)
  ✘   7553 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:185:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #1) (6.5s)
  ✘   7552 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:211:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #1) (6.6s)
  ✘   7554 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:128:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #2) (6.2s)
  ✘   7555 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:169:7 › 碳认证完整业务流程 › 证书转让流程 (retry #2) (6.0s)
  ✘   7556 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:185:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #2) (6.5s)
  ✘   7557 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:211:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #2) (6.5s)
  ✘   7558 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:246:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (6.0s)
  ✘   7561 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:356:7 › CIM协议配置业务流程 › 配置CIM端点并查看调度记录 (6.0s)
  ✘   7564 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:466:7 › 备件核销业务流程 › 创建核销单到审批完整流程 (5.8s)
  ✘   7565 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:246:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #1) (5.8s)
  ✘   7566 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:356:7 › CIM协议配置业务流程 › 配置CIM端点并查看调度记录 (retry #1) (5.9s)
  ✘   7567 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:466:7 › 备件核销业务流程 › 创建核销单到审批完整流程 (retry #1) (6.0s)
  ✘   7559 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:299:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (16.9s)
  ✘   7568 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:246:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #2) (5.9s)
```

### puppeteer
```
FAIL tests/v318-incremental-render.test.js (19.832 s)
FAIL tests/generated/render-067-ai-chat.test.js (62.28 s)
FAIL tests/v318-supplement-render.test.js
    TypeError: Cannot read properties of null (reading 'scrollWidth')
FAIL tests/v246-security-switches.test.js
FAIL tests/v318-incremental-render.test.js (19.832 s)
FAIL tests/generated/render-067-ai-chat.test.js (62.28 s)
FAIL tests/v318-supplement-render.test.js
    TypeError: Cannot read properties of null (reading 'scrollWidth')
FAIL tests/v246-security-switches.test.js
```

### selenium
```
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
BrokenPipeError: [Errno 32] Broken pipe
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=4444): Max retries exceeded with url: /session (Caused by NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused"))
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
WARNING  urllib3.connectionpool:connectionpool.py:868 Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError("HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused")': /session
E   ConnectionRefusedError: [Errno 111] Connection refused
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='localhost', port=4444): Failed to establish a new connection: [Errno 111] Connection refused
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
```

