# 🐍 pytest（API功能测试） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 03:58:20 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 57774 |
| 实际执行 | 107578 |
| ✅ 通过 | 103766 |
| ❌ 失败 | 3596 |
| ⏭️ 跳过 | 216 |
| 通过率 | 96.46% |
| 耗时(s) | 280.584
0 |

## 发布门禁

- **状态**：❌ 有失败 (3596)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `d7cd74e2b862e40637cac72d93b9bfb18862aae5` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/devices/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/schedules/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/tree] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/user-profiles/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/user-profiles/list] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/identity/user-profiles/stats] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-types] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-types/page] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-types/options] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-types/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/thumbnails/count] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-types/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/permissions/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata] 
--
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestChargingOrderService::test_update_order_status 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/page] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-groups/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-groups/list] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-groups/list] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/detail] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-groups/summary] 
[gw0] [  0%] PASSED api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_submit_invalid_idcard_format 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-params/list] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/roles/summary] 
api/test_account_charging_identity_enhanced.py::TestRealNameAuthService::test_get_auth_history 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-params/stats] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-params/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-params/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/options] 
api/test_account_charging_identity_enhanced.py::TestInternalUserController::test_external_access_blocked 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-models/list] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes] 
api/test_account_charging_identity_enhanced.py::TestUserService::test_update_user 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/tree] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/summary] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes/export] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-locations/page] 
--
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_update_user 
api/test_account_charging_identity_enhanced.py::TestUserService::test_query_users 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/routes/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-locations/tree] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-locations/tree] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/metadata/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-certs/page] 
[gw0] [  0%] FAILED api/test_account_charging_identity_enhanced.py::TestUserService::test_change_password 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/buttons/list] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/list] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/buttons/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/role-menus] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/list] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesEndpoints::test_get_endpoint_returns_200[account.list] 
api/test_all_services.py::TestAllServicesEndpoints::test_get_endpoint_returns_200[account.detail] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesEndpoints::test_get_endpoint_returns_200[account.detail] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/detail] 
api/test_all_services.py::TestAllServicesEndpoints::test_get_endpoint_returns_200[device.detail] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesEndpoints::test_get_endpoint_returns_200[device.detail] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-firmware/tree] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/user-roles/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/user-roles/count] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/user-roles/count] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-alarm/summary] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-alarm/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-alarm/count] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/tree] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/tree] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-commands/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-templates] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/device/device-templates] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/api-resources] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/api-resources] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/permission/api-resources/page] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/access-controls/count] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics] 
[gw2] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/page] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alerts/list] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alerts/list] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/models/summary] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/models/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/export] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesSearch::test_search_single_field[tenant] 
api/test_all_services.py::TestAllServicesSearch::test_search_single_field[permission] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/metrics/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/metrics/list] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/options] 
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/dashboards/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/dashboards/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/dashboards/options] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/summary] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/events/options] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/service-maps/tree] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/summary] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesSearch::test_pagination_and_sort[tenant] 
api/test_all_services.py::TestAllServicesSearch::test_pagination_and_sort[permission] 
[gw0] [  0%] PASSED api/test_all_services.py::TestAllServicesSearch::test_pagination_and_sort[permission] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/storage/storage-statistics/count] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alert-rules/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alert-rules/stats] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/alert-rules/stats] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/page] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/list] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/log-streams/tree] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/log-streams/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/list] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/probe-configs] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/probe-configs] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/detail] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/export] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/probe-configs/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/probe-configs/stats] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/export] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/probe-configs/count] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/probe-configs/count] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/options] 
api/test_all_services.py::TestAllServicesDbVerify::test_api_count_matches_db[content] 
[gw1] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s03_keyword_search_valid[/api/observability/performance-reports/list] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/tree] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/sync-tasks] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/sync-tasks/page] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/tree] 
[gw0] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenants/stats] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s01_get_returns_valid_api_result[/api/tenants/tenants/options] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/summary] 
--
[gw2] [  0%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/summary] 
api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s05_post_empty_returns_validation_error[/api/account/accounts/count] 
[gw3] [  0%] PASSED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s07_delete_nonexistent_error[/api/digitaltwin/sync-tasks/options] 
```
