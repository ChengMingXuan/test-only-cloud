# 🐍 pytest（API功能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 12:13:31 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 57774 |
| 实际执行 | 107578 |
| ✅ 通过 | 100257 |
| ❌ 失败 | 7105 |
| ⏭️ 跳过 | 216 |
| 通过率 | 93.19% |
| 耗时(s) | 270.800
0 |

## 发布门禁

- **状态**：❌ 有失败 (7105)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `53cee85606eb17c24882e1f1552bfc0bf9b1829f` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/account/accounts/options] 
[gw2] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/account/accounts/options] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/tree] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/instances/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/instances/stats] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/safecontrol/evacuation-routes/detail] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/safecontrol/evacuation-routes/detail] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/summary] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/models/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/models/stats] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/models/stats] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/properties/page] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/properties/page] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/account/account-orders/summary] 
[gw2] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/account/account-orders/summary] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/list] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/scenarios/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/scenarios/detail] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/scenarios/detail] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/account/account-invoices/summary] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/devices/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/export] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/data-streams/tree] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/data-streams/tree] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/stats] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/simulation-configs/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s02_pagination_valid_structure[/api/simulator/behavior-profiles] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/realtime-data/page] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/options] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/realtime-data/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/simulation-tasks] 
[gw2] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/account/account-transactions/export] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/simulation-tasks/stats] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/simulation-tasks/stats] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/count] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/visualization-configs/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/visualization-configs/export] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/page] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/visualization-configs/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/digitaltwin/visualization-configs/count] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/list] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/detail] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/export] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/stats] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/options] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/tree] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/summary] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/count] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/sources/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/sources/tree] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/page] 
[gw2] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/analytics/datasets/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/analytics/datasets/stats] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/list] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/pipelines] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/pipelines/page] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-packages/detail] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-packages/detail] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/ingestion-rules/list] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/ingestion-rules/list] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/ingestion-rules/summary] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/ingestion-rules/summary] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/stats] 
[gw2] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/analytics/query-templates/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/field-mappings/list] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/field-mappings/list] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/tree] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-features/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-quotas] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/summary] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/protocol-configs/options] 
[gw2] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/analytics/scheduled-reports/list] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/count] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/data-schemas/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/data-schemas/list] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/sessions/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/operations/count] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/operations/count] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/list] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-domains/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-subscriptions] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/detail] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/plans/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/plans/list] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/detail] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-statistics/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/tenants/tenant-admins] 
[gw2] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/charging/connectors/count] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/export] 
[gw0] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/users/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/charging/piles/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/users/list] 
--
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/stats] 
[gw3] [ 24%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/schedules/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/schedules/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/roles/list] 
--
[gw1] [ 25%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/options] 
[gw0] [ 25%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/orgs/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/charging/tariffs/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/orgs/export] 
--
[gw1] [ 25%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/tree] 
[gw0] [ 25%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/departments/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/departments/tree] 
[gw2] [ 25%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/charging/promotions/stats] 
--
[gw1] [ 25%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/summary] 
[gw2] [ 25%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/charging/abnormal-events/page] 
[gw3] [ 25%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/maintenance-types/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/charging/abnormal-events/list] 
--
[gw1] [ 25%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/scenarios/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s13_empty_keyword_returns_all[/api/deviceops/parts-inventory/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s12_accept_json_content_type[/api/station/station-images/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/devices] 
--
[gw1] [ 25%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/devices] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/charging/billing-records/stats] 
[gw0] [ 25%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s12_accept_json_content_type[/api/workorder/workorders] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s12_accept_json_content_type[/api/workorder/workorders/page] 
--
[gw1] [ 25%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/simulator/devices/page] 
[gw2] [ 25%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s09_status_filter_valid[/api/ingestion/ingestion-logs/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s12_accept_json_content_type[/api/workorder/workorder-types/list] 
```
