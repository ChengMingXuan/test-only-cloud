# 🐍 pytest（API功能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 10:13:18 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 57774 |
| 实际执行 | 107578 |
| ✅ 通过 | 99939 |
| ❌ 失败 | 7423 |
| ⏭️ 跳过 | 216 |
| 通过率 | 92.9% |
| 耗时(s) | 273.694
0 |

## 发布门禁

- **状态**：❌ 有失败 (7423)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `95e9dd1ad48744b2ac9c82f7bc5114d19085de42` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/permissions/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-params/options] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-params/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-users/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-users/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-users/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-users/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-configs/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-configs/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-configs/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-configs/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-products/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/instances/summary] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/perm-codes/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/perm-codes/tree] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-orders/export] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesSearch::test_pagination_and_sort[content] 
api/test_all_services.py::TestAllServicesSearch::test_pagination_and_sort[blockchain] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesSearch::test_pagination_and_sort[blockchain] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-invoices/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/api-resources/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-invoices/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/historical-data] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-payments/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-payments/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-payments/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-payments/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-recharges/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-recharges/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-recharges/stats] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesSearch::test_empty_result[storage] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-transactions/export] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/simulation-tasks/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/simulation-tasks/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-transactions/stats] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-bills/export] 
[gw0] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-packages] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-packages/page] 
[gw0] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-packages/page] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/dashboards/count] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/dashboards/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/dashboards/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/dashboards/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/dashboards/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/charts/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/charts/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/charts/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/charts/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/datasets/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/protocol-configs/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/datasets/stats] 
[gw0] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-contacts/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/indicators/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/log-streams/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/log-streams/list] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/data-schemas/detail] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-configs/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-configs/stats] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/quality-checks] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-configs/stats] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/data-sources/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/health-checks/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/health-checks/tree] 
[gw0] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-modules] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/query-templates/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/query-templates/stats] 
[gw3] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/settlement/settlements] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/settlement/settlements/page] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/export-tasks/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/export-tasks/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/export-tasks/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-admins/stats] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/scheduled-reports/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/scheduled-reports/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/scheduled-reports/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/scheduled-reports/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-rules/export] 
[gw0] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/identity/departments/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/identity/departments/count] 
[gw0] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/identity/departments/count] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/orders/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/orders/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/orders/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/orders/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/sessions/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/sessions/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/sessions/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/sessions/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/stations/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/stations/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/storage/metadata/options] 
[gw1] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/storage/metadata/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/piles/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/piles/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/piles/stats] 
[gw1] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/storage/storage-statistics/page] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/tariffs/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/tariffs/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/tariffs/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/tariffs/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/abnormal-events/export] 
[gw3] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-types/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-types/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/abnormal-events/stats] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/billing-records/export] 
[gw1] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/account/account-orders/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-areas/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/billing-records/stats] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/refunds/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/account/account-payments/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/refunds/stats] 
[gw1] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/account/account-payments/stats] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/pile-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/pile-statistics/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/pile-statistics/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/account/account-recharges/list] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/devices/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/devices/stats] 
[gw0] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/permission/role-menus] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/permission/role-menus/page] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-types/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/permission/perm-codes/page] 
[gw3] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-facilities/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-types/stats] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-groups/export] 
[gw0] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/permission/api-resources/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-services/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-groups/stats] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-params/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-statistics/tree] 
[gw3] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-statistics/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/station/station-statistics/summary] 
--
```
