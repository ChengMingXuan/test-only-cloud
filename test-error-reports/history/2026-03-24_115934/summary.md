# 全量测试汇总报告

- **执行时间**: 2026-03-24 11:59:34 UTC
- **Git Commit**: aeaa508c0930cedd26a49ac3f04d53b991a9431c
- **测试级别**: full
- **触发方式**: push

## 各工具执行状态

| 工具 | 标准用例 | 状态 | 说明 |
|------|----------|------|------|
| pytest | 57774 | ⚠️ | 未收集到结果 |
| cypress | 9877 | ✅ | 执行 21, 全部通过 |
| playwright | 11093 | ⚠️ | 未收集到结果 |
| puppeteer | 8137 | ⚠️ | 未收集到结果 |
| selenium | 6540 | ⚠️ | 未收集到结果 |
| k6 | 3651 | ⚠️ | 未收集到结果 |
| integration | 1999 | ⚠️ | 未收集到结果 |

## 综合统计

- **总执行**: 21
- **通过**: 21
- **失败**: 0
- **通过率**: 100.0%

## 失败详情

### pytest
```
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/stats] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/options] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/tree] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/summary] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/evacuation-routes/count] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/page] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/list] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/detail] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/export] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/stats] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/options] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/tree] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/summary] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/inspection-records/count] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/page] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/list] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/detail] 
[gw0] [ 24%] FAILED api/test_api_full_endpoint_matrix.py::TestApiEndpointMatrix::test_s10_put_nonexistent_error[/api/safecontrol/safety-statistics/export] 
```

