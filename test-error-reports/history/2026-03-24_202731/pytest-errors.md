# pytest 测试错误报告

- **执行时间**: 2026-03-24 20:27:32 UTC
- **Git Commit**: 7eb91d5b58a344390c38c9e46a5b096346858347

## 失败详情

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
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_401_no_user_distinction 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/device] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/device] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/stations] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/stations] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/charging/orders] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/charging/orders] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/workorder] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/workorder] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/settlements] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/settlements] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/tenants] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/tenants] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/system/role] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/system/role] 
[gw1] [ 99%] FAILED security/test_full_compliance_100.py::TestHACompliance::test_HA_003_circuit_breaker 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/analytics/charging/overview] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_response_no_database_info[/api/analytics/charging/overview] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_file_path 
[gw3] [ 99%] FAILED security/test_dual_deployment_compliance.py::TestInfrastructureCompleteness::test_clamav_in_infrastructure_compose 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_file_path 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[' OR 1=1 --] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[' OR 1=1 --] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[<script>alert(1)</script>] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[<script>alert(1)</script>] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[${7*7}] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[${7*7}] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[{{7*7}}] 
[gw2] [ 99%] PASSED security/test_http_security_headers.py::TestErrorInfoLeakage::test_error_no_payload_reflect[{{7*7}}] 
security/test_http_security_headers.py::TestErrorInfoLeakage::test_api_version_not_exposed 
```
