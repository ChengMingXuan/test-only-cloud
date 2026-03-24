# pytest 测试错误报告

- **执行时间**: 2026-03-24 16:09:18 UTC
- **Git Commit**: 7d5473fca1be77804f2751c3adc978f1ce7722f1

## 失败详情

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
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_irec_get_certificates_with_pagination 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_register_project 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_get_projects_list 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_request_credits 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_verify_credit 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_trade_credit 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestCarbonCertificationApi::test_ccer_retire_credit 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_enqueue_charging_request 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_enqueue_urgent_request 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_dispatch_charging 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_get_queue_status 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_cancel_queue 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_cancel_nonexistent_queue 
[gw3] [ 47%] FAILED api/test_v318_incremental_features.py::TestOrderlyChargingApi::test_get_pile_load_status 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_energy_overview 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_daily_report 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_monthly_report 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_get_trend_comparison 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestMgEnergyReportApi::test_record_energy_data 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_receive_dispatch_command 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_dispatch_feedback 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_dispatch_records 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_cim_config 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_save_cim_config 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_record_deviation_sample 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_deviation_analysis 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_deviation_records 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestCimProtocolApi::test_get_feedback_summary 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestStringMonitorApi::test_detect_anomalies 
[gw3] [ 48%] FAILED api/test_v318_incremental_features.py::TestStringMonitorApi::test_get_anomalies_list 
```
