# k6 测试错误报告

- **执行时间**: 2026-03-25 07:38:38 UTC
- **Git Commit**: f3ab915d77ba67a333eb9dc622486ca9283cd1cd

## 失败详情

```
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 99[0m       [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 98[0m 
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 99[0m 
  - Error Rate: 0.00%
   [32m✓[0m ai_success[2m.....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 104[0m      [36;2m✗ 0[0m  
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 92[0m 
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m     [36;2m✗ 0[0m    
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
   [32m✓[0m global_success_rate[2m............:[0m [36m100.00%[0m [36;2m✓ 441[0m       [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 442[0m
     svc_analytics_success[2m..........:[0m [36m100.00%[0m [36;2m✓ 441[0m       [36;2m✗ 0[0m  
   [32m✓[0m svc_blockchain_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_charging_success[2m...........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_iotai_success[2m..............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_pvessc_success[2m.............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_settlement_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
     api_success_rate[2m...............:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
     auth_success_rate[2m..............:[0m [36m100.00%[0m [36;2m✓ 1[0m        [36;2m✗ 0[0m  
     charging_api_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 52[0m       [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 26[0m 
   [32m✓[0m carbontrade_success[2m............:[0m [36m100.00%[0m [36;2m✓ 10[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 141[0m      [36;2m✗ 0[0m  
   [32m✓[0m demandresp_event_success[2m.......:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m deviceops_workorder_success[2m....:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m electrade_spot_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 142[0m
   [32m✓[0m microgrid_protection_success[2m...:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m overall_phase2_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 56[0m       [36;2m✗ 0[0m  
   [32m✓[0m vpp_enhanced_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 10[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 60[0m       [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 28[0m 
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
```
