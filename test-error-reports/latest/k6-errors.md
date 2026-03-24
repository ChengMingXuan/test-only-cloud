# k6 测试错误报告

- **执行时间**: 2026-03-24 16:09:18 UTC
- **Git Commit**: 7d5473fca1be77804f2751c3adc978f1ce7722f1

## 失败详情

```
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 102[0m      [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 101[0m
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 102[0m
  - Error Rate: 0.00%
[31m       ✗ AI Dashboard success
        ↳  0% — ✓ 0 / ✗ 4[0m
   [31m✗[0m ai_success[2m.....................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 4[0m  
     checks[2m.........................:[0m [36m96.29%[0m  [36;2m✓ 104[0m      [36;2m✗ 4[0m  
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 26[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m http_req_failed[2m................:[0m [36m12.63%[0m  [36;2m✓ 12[0m       [36;2m✗ 83[0m 
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m      [36;2m✗ 0[0m    
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
time="2026-03-24T14:30:30Z" level=error msg="ReferenceError: textSummary is not defined\n\tat handleSummary (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/full-service-stress.js:437:24(16))\n" hint="script exception"
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
```
