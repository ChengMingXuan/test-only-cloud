# 🐍 pytest（API功能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 06:24:49 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 57774 |
| 实际执行 | 107578 |
| ✅ 通过 | 99939 |
| ❌ 失败 | 7423 |
| ⏭️ 跳过 | 216 |
| 通过率 | 92.9% |
| 耗时(s) | 283.379
0 |

## 发布门禁

- **状态**：❌ 有失败 (7423)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `6f232d004bed373a4783d65def5e616c54dd134a` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/permissions/tree] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-types/detail] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/menus] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-groups/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/stats] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/buttons/tree] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/buttons/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/buttons/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-users/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-users/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/user-roles/summary] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/user-roles/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-configs/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-configs/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/data-scopes/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/data-scopes/tree] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-products/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/audit-logs] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/audit-logs/page] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-commands/count] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-orders/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alerts/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/models] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/models] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-invoices/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-invoices/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-invoices/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-invoices/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-payments/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/dashboards/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/dashboards/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-payments/stats] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-recharges/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alert-rules/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alert-rules/export] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/events/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-transactions/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-transactions/stats] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/realtime-data/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/realtime-data/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-statistics/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-bills/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-bills/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/account-bills/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/performance-reports/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/reports/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/dashboards/export] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/subscriptions/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/subscriptions/detail] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/subscriptions/detail] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/charts/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/storage/folders/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/transforms/stats] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/transforms/stats] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/datasets/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/datasets/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/datasets/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/datasets/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/indicators/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/indicators/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/indicators/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/indicators/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-configs/export] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/field-mappings/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/field-mappings/detail] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/field-mappings/detail] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/data-sources/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/data-sources/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/storage/storage-statistics/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/storage/storage-statistics/export] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/query-templates/export] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/data-schemas/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/data-schemas/options] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/ingestion/data-schemas/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/export-tasks/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/export-tasks/stats] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/export-tasks/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/export-tasks/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/scheduled-reports/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/scheduled-reports/stats] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/settlement/bills/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/settlement/bills/list] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-rules/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-rules/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-rules/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/analytics/analytics-rules/options] 
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
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/stations/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/stations/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/connectors/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/piles/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/piles/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/piles/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/piles/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/tariffs/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/tariffs/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/settlement/settlement-items/count] 
[gw3] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/settlement/settlement-items/count] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/promotions/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/abnormal-events/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/abnormal-events/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/abnormal-events/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/abnormal-events/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/billing-records/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/billing-records/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/billing-records/stats] 
[gw0] [  1%] PASSED api/test_all_services.py::TestAllServicesSearch::test_pagination_and_sort[permission] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/refunds/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/refunds/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/refunds/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/refunds/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/pile-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/pile-statistics/stats] 
[gw0] [  1%] PASSED api/test_all_services.py::TestAllServicesSearch::test_empty_result[blockchain] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/charging/pile-statistics/stats] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/devices/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/devices/stats] 
[gw0] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenants/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenants/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-types/export] 
[gw0] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-packages/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-types/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenant-packages/summary] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-groups/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-groups/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-groups/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-groups/options] 
--
[gw2] [  1%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-params/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-params/stats] 
[gw2] [  1%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-params/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/device/device-params/options] 
--
```
