# 🐍 pytest（API功能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 02:43:25 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 57774 |
| 实际执行 | 107578 |
| ✅ 通过 | 106580 |
| ❌ 失败 | 793 |
| ⏭️ 跳过 | 205 |
| 通过率 | 99.07% |
| 耗时(s) | 203.929
0 |

## 发布门禁

- **状态**：❌ 有失败 (793)
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
api/test_account_charging_identity_enhanced.py::TestWalletService::test_get_or_create_wallet FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestWalletService::test_get_balance FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestWalletService::test_recharge_wallet 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 钱包充值 ✓
--
api/test_account_charging_identity_enhanced.py::TestWalletService::test_wallet_transaction_history FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestWalletService::test_wallet_no_auth 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 钱包无认证拒绝 ✓
--
api/test_account_charging_identity_enhanced.py::TestMembershipBenefitAutoActivation::test_trigger_birthday_benefits FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestMembershipBenefitAutoActivation::test_trigger_anniversary_benefits FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestMembershipBenefitAutoActivation::test_upgrade_trigger_benefits 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 升级权益 ✓
--
api/test_account_charging_identity_enhanced.py::TestMembershipBenefitAutoActivation::test_get_user_benefits FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_create_order FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_create_order_with_authorization 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 授权订单 ✓
--
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_update_order_status FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_settle_order 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 订单结算 ✓
--
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_calculate_order_fee FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_cross_shard_statistics 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 跨分片统计 ✓
--
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_get_current_auth FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_get_auth_history FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_is_verified FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_idcard_encrypted_storage 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 加密存储验证 ✓
--
api/test_account_charging_identity_enhanced.py::TestUserService::test_create_user FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestUserService::test_update_user FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestUserService::test_query_users 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] 查询用户 ✓
--
api/test_account_charging_identity_enhanced.py::TestUserService::test_change_password FAILED [  0%]
api/test_account_charging_identity_enhanced.py::TestUserService::test_user_dto_no_password 
-------------------------------- live log call ---------------------------------
2026-03-24 01:05:57 [INFO] DTO无密码 ✓
--
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_start_session FAILED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_stop_session FAILED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_get_session_status PASSED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_send_command FAILED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_list_commands PASSED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_purge_session_data PASSED [ 44%]
api/test_coverage_gap_services.py::TestSimulatorDeepAPI::test_batch_purge PASSED [ 44%]
--
api/test_dag_workflow_api.py::TestDagWorkflowList::test_list_workflows_contains_seven_builtins FAILED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowList::test_list_workflows_unauthorized PASSED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowDetail::test_get_workflow_detail_success PASSED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowDetail::test_get_workflow_with_version PASSED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowDetail::test_get_workflow_nodes_structure FAILED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowDetail::test_get_nonexistent_workflow PASSED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowDetail::test_get_each_builtin_workflow[pv_power_forecast] PASSED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowDetail::test_get_each_builtin_workflow[ai_patrol] PASSED [ 45%]
--
api/test_dag_workflow_api.py::TestDagWorkflowExecute::test_execute_result_structure FAILED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowExecute::test_execute_result_has_fusion_fields PASSED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowExecute::test_execute_all_seven_workflows[pv_power_forecast] PASSED [ 45%]
api/test_dag_workflow_api.py::TestDagWorkflowExecute::test_execute_all_seven_workflows[ai_patrol] PASSED [ 45%]
--
api/test_dag_workflow_incremental.py::TestDagExecutionHistoryIncremental::test_execution_list_default_limit FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecutionHistoryIncremental::test_execution_list_custom_limit FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecutionHistoryIncremental::test_execution_list_filter_all_workflows PASSED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecutionHistoryIncremental::test_execution_list_empty_workflow_filter PASSED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecutionHistoryIncremental::test_execution_list_negative_limit PASSED [ 45%]
--
api/test_dag_workflow_incremental.py::TestDagExecutionDetailIncremental::test_detail_invalid_uuid_format FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecutionDetailIncremental::test_detail_response_has_execution_and_nodes PASSED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecutionDetailIncremental::test_detail_nodes_have_model_info PASSED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecutionDetailIncremental::test_detail_nodes_have_retry_info PASSED [ 45%]
--
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_all_seven_return_execution_id[pv_power_forecast] FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_all_seven_return_execution_id[ai_patrol] FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_all_seven_return_execution_id[load_forecast] FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_all_seven_return_execution_id[price_forecast] FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_all_seven_return_execution_id[charging_forecast] FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_all_seven_return_execution_id[battery_forecast] FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_all_seven_return_execution_id[fault_diagnosis] FAILED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_concurrent_requests PASSED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_large_input_data PASSED [ 45%]
api/test_dag_workflow_incremental.py::TestDagExecuteFusionIncremental::test_execute_special_chars_in_input PASSED [ 45%]
--
api/test_dapr_compliance.py::TestServiceTransportRegistration::test_extensions_file_exists FAILED [ 45%]
api/test_dapr_compliance.py::TestServiceTransportRegistration::test_extensions_registers_dapr FAILED [ 45%]
api/test_dapr_compliance.py::TestServiceTransportRegistration::test_extensions_has_dapr_client FAILED [ 45%]
api/test_dapr_compliance.py::TestServiceTransportRegistration::test_no_dual_mode_switch FAILED [ 45%]
api/test_dapr_compliance.py::TestServiceTransportRegistration::test_resilience_pipeline_registered FAILED [ 45%]
api/test_dapr_compliance.py::TestDockerComposeDapr::test_compose_store_has_dapr FAILED [ 45%]
api/test_dapr_compliance.py::TestDockerComposeDapr::test_compose_addon_exists FAILED [ 45%]
api/test_dapr_compliance.py::TestDockerComposeDapr::test_no_development_appsettings PASSED [ 45%]
api/test_dapr_compliance.py::TestNewMicroserviceScript::test_script_exists FAILED [ 45%]
api/test_dapr_compliance.py::TestNewMicroserviceScript::test_script_uses_dapr_mode FAILED [ 45%]
api/test_device_charging_station_workorder.py::TestDeviceManagement::test_device_list PASSED [ 45%]
api/test_device_charging_station_workorder.py::TestDeviceManagement::test_device_list_filter_by_type PASSED [ 45%]
api/test_device_charging_station_workorder.py::TestDeviceManagement::test_device_list_filter_by_status PASSED [ 45%]
--
api/test_gateway_ingestion_enhanced.py::TestWalBufferedStorage::test_wal_replay_pending FAILED [ 45%]
api/test_gateway_ingestion_enhanced.py::TestWalBufferedStorage::test_wal_checkpoint 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:48 [INFO] WAL检查点 ✓
--
api/test_gateway_ingestion_enhanced.py::TestBatchIngestionWriter::test_enqueue_single_message FAILED [ 45%]
api/test_gateway_ingestion_enhanced.py::TestBatchIngestionWriter::test_enqueue_batch_messages FAILED [ 45%]
api/test_gateway_ingestion_enhanced.py::TestBatchIngestionWriter::test_get_queue_depth 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:48 [INFO] 队列深度 ✓
--
api/test_gateway_ingestion_enhanced.py::TestBatchIngestionWriter::test_flush_buffer FAILED [ 45%]
api/test_gateway_ingestion_enhanced.py::TestOcpp20MessageHandler::test_transaction_event_started 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:48 [INFO] TransactionEvent Started ✓
--
api/test_gateway_ingestion_enhanced.py::TestIngestionTaskEngine::test_create_task FAILED [ 45%]
api/test_gateway_ingestion_enhanced.py::TestIngestionTaskEngine::test_start_task FAILED [ 45%]
api/test_gateway_ingestion_enhanced.py::TestIngestionTaskEngine::test_stop_task FAILED [ 45%]
api/test_identity/test_auth.py::TestAuthLogin::test_login_success PASSED [ 45%]
api/test_identity/test_auth.py::TestAuthLogin::test_login_wrong_password PASSED [ 45%]
api/test_identity/test_auth.py::TestAuthLogin::test_login_empty_username PASSED [ 45%]
--
api/test_ruleengine_edge_mode.py::TestRuleSyncUpload::test_upload_execution_logs_endpoint FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestRuleSyncUpload::test_upload_alarm_instances_endpoint FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestRuleSyncUpload::test_upload_empty_batch 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 空批次上传 ✓
--
api/test_ruleengine_edge_mode.py::TestMqttTriggerSimulation::test_trigger_rule_execution FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestMqttTriggerSimulation::test_trigger_with_alarm_type FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestMqttTriggerSimulation::test_trigger_with_event_type FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestMqttTriggerSimulation::test_trigger_missing_payload_rejected FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestMqttTriggerSimulation::test_trigger_invalid_tenant_rejected FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestRuleExecutionLogs::test_list_execution_logs 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 执行日志列表 ✓
--
api/test_ruleengine_edge_mode.py::TestAlarmInstances::test_acknowledge_alarm FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestAlarmInstances::test_resolve_alarm FAILED [ 45%]
api/test_ruleengine_edge_mode.py::TestEdgeConfiguration::test_cloud_mode_chains_accessible 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 云端模式 CRUD ✓
--
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_get_chain_detail FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_create_rule_chain FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_create_duplicate_code_rejected FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_update_rule_chain FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_delete_rule_chain FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_delete_builtin_chain_blocked FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleChainService::test_cache_cleared_on_create FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleExecutionEngine::test_process_message FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleExecutionEngine::test_match_chains FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleExecutionEngine::test_match_universal_chains FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleExecutionEngine::test_execution_result_statistics FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleExecutionEngine::test_max_nodes_protection FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestRuleExecutionEngine::test_external_node_whitelist FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestVppDispatchService::test_list_dispatches 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 调度列表 ✓
--
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestVppDispatchService::test_get_dispatch_result FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestVppDispatchService::test_cancel_pending_dispatch 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 取消调度 ✓
--
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestCarbonTradingController::test_calculate_emission FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestCarbonTradingController::test_get_carbon_asset FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestCarbonTradingController::test_forecast_carbon_price 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 碳价预测 ✓
--
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestCarbonTradingController::test_generate_trading_strategy FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestCarbonTradingController::test_execute_carbon_trade 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 执行碳交易 ✓
--
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestCarbonTradingController::test_generate_compliance_report FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestCarbonTradingController::test_emission_no_auth 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 碳排放无认证拒绝 ✓
--
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestDemandResponseController::test_assess_capability FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestDemandResponseController::test_generate_response_plan FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestDemandResponseController::test_participate_in_event 
-------------------------------- live log call ---------------------------------
2026-03-24 01:06:49 [INFO] 确认参与 ✓
--
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestDemandResponseController::test_settle_response FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestInsightController::test_get_device_insights FAILED [ 45%]
api/test_ruleengine_vpp_iotcloudai_enhanced.py::TestInsightController::test_get_energy_optimization 
```
