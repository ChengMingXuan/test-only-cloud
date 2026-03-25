# k6 测试错误报告

- **执行时间**: 2026-03-25 06:33:57 UTC
- **Git Commit**: f279bdfe6226fa1abefe8d8953bd59aa01f3d504

## 失败详情

```
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 105[0m      [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 104[0m
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 105[0m
  - Error Rate: 0.00%
[31m       ✗ AI Dashboard success
        ↳  0% — ✓ 0 / ✗ 4[0m
   [31m✗[0m ai_success[2m.....................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 4[0m  
     checks[2m.........................:[0m [36m96.15%[0m  [36;2m✓ 100[0m      [36;2m✗ 4[0m  
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m13.04%[0m  [36;2m✓ 12[0m       [36;2m✗ 80[0m 
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m     [36;2m✗ 0[0m    
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
   [32m✓[0m global_success_rate[2m............:[0m [36m100.00%[0m [36;2m✓ 471[0m       [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 472[0m
     svc_analytics_success[2m..........:[0m [36m100.00%[0m [36;2m✓ 471[0m       [36;2m✗ 0[0m  
   [32m✓[0m svc_blockchain_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_charging_success[2m...........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_iotai_success[2m..............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_pvessc_success[2m.............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_settlement_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T06:30:36Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:59:28(29))\n" executor=constant-vus scenario=default source=stacktrace
```
