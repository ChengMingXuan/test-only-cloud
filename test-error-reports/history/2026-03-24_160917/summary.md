# 全量测试汇总报告

- **执行时间**: 2026-03-24 16:09:17 UTC
- **Git Commit**: 7d5473fca1be77804f2751c3adc978f1ce7722f1
- **测试级别**: full
- **触发方式**: push

## 各工具执行状态

| 工具 | 标准用例 | 状态 | 说明 |
|------|----------|------|------|
| pytest | 57774 | ⚠️ | 未收集到结果 |
| cypress | 9877 | ❌ | 执行 130, 通过 116, 失败 14 |
| playwright | 11093 | ⚠️ | 未收集到结果 |
| puppeteer | 8137 | ✅ | 执行 8527, 全部通过 |
| selenium | 6540 | ⚠️ | 未收集到结果 |
| k6 | 3651 | ❌ | 执行 43489, 通过 43485, 失败 4 |
| integration | 1999 | ✅ | 执行 14, 全部通过 |

## 综合统计

- **总执行**: 52154
- **通过**: 52136
- **失败**: 18
- **通过率**: 100.0%

## 失败详情

### pytest
```
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_update_order_status 
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_update_user 
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_change_password 
[gw3] [ 42%] FAILED api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_update_rule_chain 
[gw3] [ 42%] FAILED api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_delete_rule_chain 
[gw3] [ 42%] FAILED api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestDemandResponseController::test_settle_response 
[gw3] [ 42%] FAILED api/test_v318_adaptive_predict.py::TestAdaptivePredict::test_predict_missing_device 
[gw3] [ 42%] FAILED api/test_v318_adaptive_predict.py::TestAdaptiveFeedback::test_submit_feedback_invalid 
[gw3] [ 43%] FAILED api/test_v318_agent.py::TestAgentExecution::test_execute_missing_agent 
[gw3] [ 47%] FAILED api/test_v318_business_no_generator.py::TestBusinessNoViaCharging::test_order_no_uniqueness 
[gw3] [ 47%] FAILED api/test_v318_carbon_certification.py::TestIRecRegistration::test_register_missing_fields 
[gw3] [ 47%] FAILED api/test_v318_device_health.py::TestDeviceHealthBatchCheck::test_batch_check_empty_list 
[gw3] [ 47%] FAILED api/test_v318_export_services.py::TestExcelExport::test_export_excel_missing_source 
[gw3] [ 47%] FAILED api/test_v318_export_services.py::TestPdfExport::test_export_pdf_missing_template 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_register_success 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_register_missing_required_fields 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_issue_certificate 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_transfer_certificate 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_retire_certificate 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_get_certificates_list 
```

### cypress
```
[0m[31m     AssertionError: Timed out retrying after 10000ms: expected '<input#username.ant-login-input>' to be 'visible'
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
  ✘  11390 [chromium] › tests/incremental-geofence-ai-coldarchive.spec.ts:76:7 › Station GeoFence E2E › 围栏列表加载 (11.1s)
  ✘  11438 [chromium] › tests/incremental-geofence-ai-coldarchive.spec.ts:76:7 › Station GeoFence E2E › 围栏列表加载 (retry #1) (12.4s)
  ✘  11522 [chromium] › tests/v318-incremental-e2e.spec.ts:141:7 › 智能排队充电完整业务流程 E2E › 排队 → 调度 → 充电完整流程 (1.9s)
  ✘  11525 [chromium] › tests/v318-incremental-e2e.spec.ts:263:7 › CIM调度执行流程 E2E › 配置 → 接收指令 → 执行 → 反馈 (1.8s)
  ✘  11528 [chromium] › tests/v318-incremental-e2e.spec.ts:141:7 › 智能排队充电完整业务流程 E2E › 排队 → 调度 → 充电完整流程 (retry #1) (1.9s)
  ✘  11529 [chromium] › tests/v318-incremental-e2e.spec.ts:356:7 › AI预测与反馈流程 E2E › 选择场景 → 执行预测 → 查看结果 → 提交反馈 (1.8s)
  ✘  11530 [chromium] › tests/v318-incremental-e2e.spec.ts:263:7 › CIM调度执行流程 E2E › 配置 → 接收指令 → 执行 → 反馈 (retry #1) (2.0s)
  ✘  11531 [chromium] › tests/v318-incremental-e2e.spec.ts:141:7 › 智能排队充电完整业务流程 E2E › 排队 → 调度 → 充电完整流程 (retry #2) (1.9s)
  ✘  11532 [chromium] › tests/v318-incremental-e2e.spec.ts:356:7 › AI预测与反馈流程 E2E › 选择场景 → 执行预测 → 查看结果 → 提交反馈 (retry #1) (1.9s)
  ✘  11533 [chromium] › tests/v318-incremental-e2e.spec.ts:263:7 › CIM调度执行流程 E2E › 配置 → 接收指令 → 执行 → 反馈 (retry #2) (2.0s)
  ✘  11526 [chromium] › tests/incremental-geofence-ai-coldarchive.spec.ts:76:7 › Station GeoFence E2E › 围栏列表加载 (retry #2) (11.7s)
  ✘  11535 [chromium] › tests/v318-incremental-e2e.spec.ts:356:7 › AI预测与反馈流程 E2E › 选择场景 → 执行预测 → 查看结果 → 提交反馈 (retry #2) (2.1s)
  ✘  11536 [chromium] › tests/v318-incremental-e2e.spec.ts:449:7 › 设备健康评估流程 E2E › 单台评估 → 批量评估 → 查看趋势 (2.2s)
  ✘  11539 [chromium] › tests/v318-supplement-e2e.spec.ts:47:7 › 移动端认证完整流程 E2E › 短信验证码登录 → 查看个人信息 → 退出 (305ms)
  ✘  11538 [chromium] › tests/v318-incremental-e2e.spec.ts:539:7 › 跨功能集成流程 E2E › AI预测 → 调度优化 → 设备控制 (1.7s)
  ✘  11543 [chromium] › tests/v318-supplement-e2e.spec.ts:92:7 › 移动端认证完整流程 E2E › 小程序登录 → 绑定手机号 (461ms)
  ✘  11542 [chromium] › tests/v318-supplement-e2e.spec.ts:47:7 › 移动端认证完整流程 E2E › 短信验证码登录 → 查看个人信息 → 退出 (retry #1) (520ms)
  ✘  11541 [chromium] › tests/v318-incremental-e2e.spec.ts:449:7 › 设备健康评估流程 E2E › 单台评估 → 批量评估 → 查看趋势 (retry #1) (2.1s)
  ✘  11544 [chromium] › tests/v318-incremental-e2e.spec.ts:539:7 › 跨功能集成流程 E2E › AI预测 → 调度优化 → 设备控制 (retry #1) (1.7s)
  ✘  11546 [chromium] › tests/v318-supplement-e2e.spec.ts:92:7 › 移动端认证完整流程 E2E › 小程序登录 → 绑定手机号 (retry #1) (591ms)
```

### k6
```
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 102[0m      [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 101[0m
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 102[0m
  - Error Rate: 0.00%
[31m       ✗ AI Dashboard success
        ↳  0% — ✓ 0 / ✗ 4[0m
   [31m✗[0m ai_success[2m.....................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 4[0m  
     checks[2m.........................:[0m [36m96.29%[0m  [36;2m✓ 104[0m      [36;2m✗ 4[0m  
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 26[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m12.63%[0m  [36;2m✓ 12[0m       [36;2m✗ 83[0m 
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m      [36;2m✗ 0[0m    
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
time="2026-03-24T14:30:30Z" level=error msg="ReferenceError: textSummary is not defined\n\tat handleSummary (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/full-service-stress.js:437:24(16))\n" hint="script exception"
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
```

