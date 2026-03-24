# 🐍 pytest（API功能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 16:08:59 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 57774 |
| 实际执行 | 107578 |
| ✅ 通过 | 106637 |
| ❌ 失败 | 725 |
| ⏭️ 跳过 | 216 |
| 通过率 | 99.13% |
| 耗时(s) | 264.092
0.000
0.106
0.115
0.001
0.001
0.002
0.102
0.001
0.001
0.001
0.001
0.002
0.001
0.001
0.003
0.001
0.001
0.001
0.001
0.003
0.003
0.001
0.002
0.003
0.004
0.003
0.001
0.001
0.003
0.001
0.002
0.116
0.001
0.001
0.002
0.001
0.001
0.002
0.001
0.001
0.002
0.001
0.001
0.001
0.001
0.001
0.003
0.001
0.001
0.001
0.001
0.001
0.001
0.004
0.001
0.001
0.001
0.004
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.001
0.002 |

## 发布门禁

- **状态**：❌ 有失败 (725)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `7d5473fca1be77804f2751c3adc978f1ce7722f1` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_update_order_status 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-params] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-products/options] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-products/options] 
--
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_update_user 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes/summary] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes/summary] 
--
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_change_password 
api/test_account_charging_identity_enhanced.py::TestUserService::test_user_dto_no_password 
[gw0] [  0%] PASSED api/test_account_charging_identity_enhanced.py::TestUserService::test_user_dto_no_password 
api/test_all_services.py::TestAllServicesEndpoints::test_get_endpoint_returns_200[tenant.list] 
--
[gw3] [ 42%] FAILED api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_update_rule_chain 
[gw2] [ 42%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/deviceops/diagnostics/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/deviceops/diagnostics/detail] 
[gw2] [ 42%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/deviceops/diagnostics/detail] 
--
[gw3] [ 42%] FAILED api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_delete_rule_chain 
[gw2] [ 42%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/deviceops/diagnostics/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/deviceops/diagnostics/count] 
[gw2] [ 42%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/deviceops/diagnostics/count] 
--
[gw3] [ 42%] FAILED api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestDemandResponseController::test_settle_response 
[gw0] [ 42%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/device/device-groups/export] 
[gw2] [ 42%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/deviceops/incident-reports/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/device/device-groups/stats] 
--
[gw3] [ 42%] FAILED api/test_v318_adaptive_predict.py::TestAdaptivePredict::test_predict_missing_device 
api/test_v318_adaptive_predict.py::TestAdaptivePredict::test_predict_unauthorized 
[gw3] [ 42%] ERROR api/test_v318_adaptive_predict.py::TestAdaptivePredict::test_predict_unauthorized 
api/test_v318_adaptive_predict.py::TestAdaptiveModelStatus::test_get_model_status 
--
[gw3] [ 42%] FAILED api/test_v318_adaptive_predict.py::TestAdaptiveFeedback::test_submit_feedback_invalid 
api/test_v318_adaptive_predict.py::TestAdaptiveFeedback::test_submit_feedback_unauthorized 
[gw3] [ 42%] ERROR api/test_v318_adaptive_predict.py::TestAdaptiveFeedback::test_submit_feedback_unauthorized 
api/test_v318_agent.py::TestAgentConfig::test_create_agent 
--
[gw3] [ 43%] FAILED api/test_v318_agent.py::TestAgentExecution::test_execute_missing_agent 
api/test_v318_agent.py::TestAgentExecution::test_execute_unauthorized 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/multienergy/supply-networks/export] 
[gw2] [ 43%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/multienergy/supply-networks/export] 
--
[gw3] [ 47%] FAILED api/test_v318_business_no_generator.py::TestBusinessNoViaCharging::test_order_no_uniqueness 
api/test_v318_business_no_generator.py::TestBusinessNoViaWorkOrder::test_create_workorder_generates_no 
[gw3] [ 47%] PASSED api/test_v318_business_no_generator.py::TestBusinessNoViaWorkOrder::test_create_workorder_generates_no 
api/test_v318_business_no_generator.py::TestBusinessNoViaSettlement::test_create_settlement_generates_no 
--
[gw3] [ 47%] FAILED api/test_v318_carbon_certification.py::TestIRecRegistration::test_register_missing_fields 
api/test_v318_carbon_certification.py::TestIRecRegistration::test_register_unauthorized 
[gw3] [ 47%] ERROR api/test_v318_carbon_certification.py::TestIRecRegistration::test_register_unauthorized 
api/test_v318_carbon_certification.py::TestIRecIssuance::test_issue_success 
--
[gw3] [ 47%] FAILED api/test_v318_device_health.py::TestDeviceHealthBatchCheck::test_batch_check_empty_list 
api/test_v318_device_health.py::TestDeviceHealthBatchCheck::test_batch_check_unauthorized 
[gw3] [ 47%] ERROR api/test_v318_device_health.py::TestDeviceHealthBatchCheck::test_batch_check_unauthorized 
api/test_v318_device_health.py::TestDeviceHealthHistory::test_get_health_history 
--
[gw3] [ 47%] FAILED api/test_v318_export_services.py::TestExcelExport::test_export_excel_missing_source 
api/test_v318_export_services.py::TestExcelExport::test_export_excel_unauthorized 
[gw3] [ 47%] ERROR api/test_v318_export_services.py::TestExcelExport::test_export_excel_unauthorized 
api/test_v318_export_services.py::TestExcelExport::test_export_templates 
--
[gw3] [ 47%] FAILED api/test_v318_export_services.py::TestPdfExport::test_export_pdf_missing_template 
api/test_v318_export_services.py::TestPdfExport::test_export_pdf_unauthorized 
[gw3] [ 47%] ERROR api/test_v318_export_services.py::TestPdfExport::test_export_pdf_unauthorized 
api/test_v318_export_services.py::TestPdfExport::test_pdf_templates 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_register_success 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_register_missing_required_fields 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_register_missing_required_fields 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_issue_certificate 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_issue_certificate 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_transfer_certificate 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_transfer_certificate 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_retire_certificate 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/energyeff/certification-records/export] 
[gw0] [ 47%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/energyeff/certification-records/export] 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_retire_certificate 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_get_certificates_list 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_get_certificates_list 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_get_certificates_with_pagination 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/energyeff/certification-records/tree] 
[gw0] [ 47%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/energyeff/certification-records/tree] 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_get_certificates_with_pagination 
[gw2] [ 47%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_11_boundary_0069 
test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_11_sql_injection_0069 
[gw2] [ 47%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_11_sql_injection_0069 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_register_project 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_get_projects_list 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/energyeff/efficiency-configs/count] 
[gw0] [ 47%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/energyeff/efficiency-configs/count] 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_get_projects_list 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_request_credits 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/energy-types/list] 
[gw0] [ 47%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/energy-types/list] 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_request_credits 
[gw1] [ 47%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Certificate_post_12_large_payload_0012 
test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_empty_body_0070 
[gw2] [ 47%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_empty_body_0070 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_verify_credit 
[gw0] [ 47%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/energy-types/options] 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Certificate_post_12_timeout_0012 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_trade_credit 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_trade_credit 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Certificate_post_12_permission_denied_0012 
api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_retire_credit 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/energy-types/tree] 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_retire_credit 
api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_enqueue_charging_request 
[gw1] [ 47%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Certificate_post_12_field_validation_0012 
[gw2] [ 47%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_large_payload_0070 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_enqueue_charging_request 
api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_enqueue_urgent_request 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_0_positive_0013 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_enqueue_urgent_request 
[gw2] [ 47%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_timeout_0070 
test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_permission_denied_0070 
api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_dispatch_charging 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_dispatch_charging 
[gw2] [ 47%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_field_validation_0070 
test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_response_format_0070 
api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_get_queue_status 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_get_queue_status 
api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_cancel_queue 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/supply-networks/list] 
[gw2] [ 47%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_post_12_response_format_0070 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_cancel_queue 
api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_cancel_nonexistent_queue 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/supply-networks/export] 
[gw1] [ 47%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_0_boundary_0013 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_cancel_nonexistent_queue 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/supply-networks/stats] 
[gw1] [ 47%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_0_sql_injection_0013 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_0_concurrent_0013 
--
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_get_pile_load_status 
api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_energy_overview 
[gw0] [ 47%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/supply-networks/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/supply-networks/tree] 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_energy_overview 
api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_daily_report 
[gw1] [ 48%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_0_permission_denied_0013 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_0_response_format_0013 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_daily_report 
[gw1] [ 48%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_0_response_format_0013 
api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_monthly_report 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_1_positive_0014 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_monthly_report 
api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_trend_comparison 
[gw0] [ 48%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/supply-networks/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/supply-networks/count] 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_trend_comparison 
api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_record_energy_data 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_record_energy_data 
[gw2] [ 48%] PASSED test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_put_13_large_payload_0071 
test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_put_13_concurrent_0071 
api/test_v318_incremental_features.py::TestCimProtocolApi::test_receive_dispatch_command 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_receive_dispatch_command 
api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_dispatch_feedback 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_1_sql_injection_0014 
test-automation/tests/api/test_charging_api.py::TestChargingApi::test_Charging_OcppDebug_put_13_idempotent_0071 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_dispatch_feedback 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_1_concurrent_0014 
[gw0] [ 48%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/demand-data/page] 
api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_dispatch_records 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_dispatch_records 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_1_timeout_0014 
api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_cim_config 
[gw1] [ 48%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_1_timeout_0014 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_cim_config 
[gw0] [ 48%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/demand-data/detail] 
test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_1_permission_denied_0014 
[gw1] [ 48%] PASSED test-automation/tests/api/test_blockchain_api.py::TestBlockchainApi::test_Blockchain_Contract_get_1_permission_denied_0014 
--
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_save_cim_config 
[gw0] [ 48%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s15_patch_nonexistent_error[/api/multienergy/demand-data/export] 
```
