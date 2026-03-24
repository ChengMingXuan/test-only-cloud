# 全量测试汇总报告

- **执行时间**: 2026-03-24 12:14:41 UTC
- **Git Commit**: 53cee85606eb17c24882e1f1552bfc0bf9b1829f
- **测试级别**: full
- **触发方式**: push

## 各工具执行状态

| 工具 | 标准用例 | 状态 | 说明 |
|------|----------|------|------|
| pytest | 57774 | ⚠️ | 未收集到结果 |
| cypress | 9877 | ✅ | 执行 300, 全部通过 |
| playwright | 11093 | ⚠️ | 未收集到结果 |
| puppeteer | 8137 | ⚠️ | 未收集到结果 |
| selenium | 6540 | ⚠️ | 未收集到结果 |
| k6 | 3651 | ⚠️ | 未收集到结果 |
| integration | 1999 | ✅ | 执行 14, 全部通过 |

## 综合统计

- **总执行**: 314
- **通过**: 314
- **失败**: 0
- **通过率**: 100.0%

## 失败详情

### pytest
```
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/stats] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/options] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/tree] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/summary] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/count] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/page] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/list] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/detail] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/export] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/stats] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/options] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/tree] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/summary] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/count] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/page] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/list] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/detail] 
[gw1] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/export] 
```

