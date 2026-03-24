# 云端独立报告执行摘要

- **执行时间**: 2026-03-24 20:27:31 UTC
- **Git Commit**: 7eb91d5b58a344390c38c9e46a5b096346858347
- **测试级别**: full
- **触发方式**: push
- **执行模式**: full
- **所选工具**: pytest,cypress,playwright,puppeteer,selenium,k6

## 本次独立报告状态

| 工具 | 标准用例 | 状态 | 说明 |
|------|----------|------|------|
| pytest | 57774 | ❌ | 执行 107578, 通过 106886, 失败 249 |
| cypress | 9877 | ⚠️ | 未收集到结果 |
| playwright | 11093 | ✅ | 执行 17398, 全部通过 |
| puppeteer | 8137 | ✅ | 执行 8000, 全部通过 |
| selenium | 6540 | ❌ | 执行 8258, 通过 7055, 失败 334 |
| k6 | 3651 | ⚠️ | 未收集到结果 |

## 综合统计

- **总执行**: 139896
- **通过**: 139313
- **失败**: 583
- **通过率**: 99.6%

## 失败详情

### pytest
```
[gw1] [ 49%] FAILED automated/test_03_crud.py::TestCrudLifecycle::test_create_and_read[\u89c4\u5219\u94fe] 
[gw1] [ 49%] FAILED automated/test_03_crud.py::TestCrudLifecycle::test_full_lifecycle[\u89c4\u5219\u94fe] 
[gw1] [ 49%] FAILED automated/test_03_crud.py::TestCrudLifecycle::test_create_missing_required_fields[\u5b57\u5178\u7ba1\u7406] 
[gw1] [ 52%] FAILED automated/test_07_integration.py::TestRolePermissionAssignment::test_init_tenant_permissions_missing_tenant_id 
[gw1] [ 99%] FAILED security/test_compliance_enforcement.py::TestWatermark::test_watermark_enabled 
[gw0] [ 99%] FAILED security/test_dual_deployment_compliance.py::TestSharedDeploymentAbstraction::test_deployment_mode_file_exists 
[gw1] [ 99%] FAILED security/test_full_compliance_100.py::TestCtrlCompliance::test_CTRL_004_modbus_protocol_interface 
[gw1] [ 99%] FAILED security/test_full_compliance_100.py::TestCtrlCompliance::test_CTRL_005_modbus_function_codes 
[gw0] [ 99%] FAILED security/test_dual_deployment_compliance.py::TestSharedDeploymentAbstraction::test_deployment_mode_enum 
[gw1] [ 99%] FAILED security/test_full_compliance_100.py::TestCtrlCompliance::test_CTRL_006_modbus_byte_order 
[gw0] [ 99%] FAILED security/test_dual_deployment_compliance.py::TestSharedDeploymentAbstraction::test_security_zone_enum 
[gw1] [ 99%] FAILED security/test_full_compliance_100.py::TestCtrlCompliance::test_CTRL_007_data_accuracy_monitor 
[gw1] [ 99%] FAILED security/test_full_compliance_100.py::TestHACompliance::test_HA_001_health_check_endpoints 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_404_no_stack_trace 
[gw0] [ 99%] FAILED security/test_dual_deployment_compliance.py::TestSharedDeploymentAbstraction::test_edge_mode_base_options 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_404_no_stack_trace 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_400_no_internal_details 
[gw1] [ 99%] FAILED security/test_full_compliance_100.py::TestHACompliance::test_HA_002_consul_service_discovery 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_400_no_internal_details 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_401_no_user_distinction 
```

