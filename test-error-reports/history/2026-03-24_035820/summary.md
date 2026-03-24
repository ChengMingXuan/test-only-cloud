# 全量测试汇总报告

- **执行时间**: 2026-03-24 03:58:20 UTC
- **Git Commit**: d7cd74e2b862e40637cac72d93b9bfb18862aae5
- **测试级别**: full
- **触发方式**: push

## 各工具执行状态

| 工具 | 标准用例 | 状态 | 说明 |
|------|----------|------|------|
| pytest | 57774 | ⚠️ | 未收集到结果 |
| cypress | 9877 | ❌ | 执行 626, 通过 625, 失败 1 |
| playwright | 11093 | ⚠️ | 未收集到结果 |
| puppeteer | 8137 | ⚠️ | 未收集到结果 |
| selenium | 6540 | ⚠️ | 未收集到结果 |
| k6 | 3651 | ⚠️ | 未收集到结果 |
| integration | 1999 | ⚠️ | 未收集到结果 |

## 综合统计

- **总执行**: 626
- **通过**: 625
- **失败**: 1
- **通过率**: 99.8%

## 失败详情

### pytest
```
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/stats] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/options] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/tree] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/summary] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/count] 
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_update_order_status 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/page] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/list] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/detail] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/export] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/stats] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/options] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/tree] 
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_update_user 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/summary] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/count] 
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_change_password 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/page] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/list] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/detail] 
```

### cypress
```
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '<input#username.ant-input>' to be 'visible'
```

### playwright
```
  ✘   7546 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:96:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (254ms)
  ✘   7550 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:96:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #1) (360ms)
  ✘   7551 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:96:7 › 碳认证完整业务流程 › I-REC设备注册到证书签发完整流程 (retry #2) (303ms)
  ✘   7552 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:214:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (10.9s)
  ✘   7547 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:137:7 › 碳认证完整业务流程 › 证书转让流程 (17.0s)
  ✘   7549 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:179:7 › 有序充电完整业务流程 › 排队到调度完整流程 (17.4s)
  ✘   7548 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:153:7 › 碳认证完整业务流程 › CCER项目注册流程 (17.6s)
  ✘   7553 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:214:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #1) (10.9s)
  ✘   7554 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:137:7 › 碳认证完整业务流程 › 证书转让流程 (retry #1) (16.5s)
  ✘   7555 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:179:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #1) (16.9s)
  ✘   7556 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:153:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #1) (16.9s)
  ✘   7557 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:214:7 › 有序充电完整业务流程 › 查看充电桩负荷并取消排队 (retry #2) (10.8s)
  ✘   7561 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:267:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (10.8s)
  ✘   7558 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:137:7 › 碳认证完整业务流程 › 证书转让流程 (retry #2) (16.6s)
  ✘   7559 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:179:7 › 有序充电完整业务流程 › 排队到调度完整流程 (retry #2) (17.2s)
  ✘   7560 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:153:7 › 碳认证完整业务流程 › CCER项目注册流程 (retry #2) (17.3s)
  ✘   7562 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:267:7 › 微电网能耗报表业务流程 › 查看概览到导出报表完整流程 (retry #1) (11.1s)
  ✘   7563 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:290:7 › 微电网能耗报表业务流程 › 日报表和月报表切换 (11.0s)
  ✘   7565 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:367:7 › CIM协议配置业务流程 › 查看偏差分析 (10.8s)
  ✘   7564 [chromium] › tests/generated/e2e-302-v318-boundary-incremental.spec.ts:324:7 › CIM协议配置业务流程 › 配置CIM端点并查看调度记录 (16.1s)
```

### puppeteer
```
FAIL tests/v318-incremental-render.test.js
    TypeError: this.timeout is not a function
FAIL tests/generated/render-067-ai-chat.test.js (63.311 s)
```

### selenium
```
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py", line 197, in exec_module
OSError: [Errno 98] Address already in use
_pytest.config.ConftestImportFailure: OSError: [Errno 98] Address already in use (from /home/runner/work/test-only-cloud/test-only-cloud/testing/tests/selenium-tests/conftest.py)
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py", line 197, in exec_module
OSError: [Errno 98] Address already in use
_pytest.config.ConftestImportFailure: OSError: [Errno 98] Address already in use (from /home/runner/work/test-only-cloud/test-only-cloud/testing/tests/selenium-tests/conftest.py)
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py", line 197, in exec_module
OSError: [Errno 98] Address already in use
_pytest.config.ConftestImportFailure: OSError: [Errno 98] Address already in use (from /home/runner/work/test-only-cloud/test-only-cloud/testing/tests/selenium-tests/conftest.py)
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py", line 197, in exec_module
OSError: [Errno 98] Address already in use
_pytest.config.ConftestImportFailure: OSError: [Errno 98] Address already in use (from /home/runner/work/test-only-cloud/test-only-cloud/testing/tests/selenium-tests/conftest.py)
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py", line 197, in exec_module
OSError: [Errno 98] Address already in use
_pytest.config.ConftestImportFailure: OSError: [Errno 98] Address already in use (from /home/runner/work/test-only-cloud/test-only-cloud/testing/tests/selenium-tests/conftest.py)
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py", line 197, in exec_module
OSError: [Errno 98] Address already in use
_pytest.config.ConftestImportFailure: OSError: [Errno 98] Address already in use (from /home/runner/work/test-only-cloud/test-only-cloud/testing/tests/selenium-tests/conftest.py)
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/_pytest/assertion/rewrite.py", line 197, in exec_module
OSError: [Errno 98] Address already in use
```

