# ⚡ k6（性能压测） — 测试报告

> 来源：GitHub Actions CI | 级别：full | 2026-03-24 16:09:15 UTC

## 执行概要

| 指标 | 数值 |
|------|------|
| 标准用例数 | 3651 |
| 实际执行 | 43489 |
| ✅ 通过 | 43485 |
| ❌ 失败 | 4 |
| ⏭️ 跳过 | 0 |
| 通过率 | 99.99% |
| 耗时(s) | 44 |

## 发布门禁

- **状态**：❌ 有失败 (4)
- **结论**：存在失败用例 - 不可发布

## 环境信息

| 项 | 值 |
|----|-----|
| Git Commit | `7d5473fca1be77804f2751c3adc978f1ce7722f1` |
| 触发方式 | push |
| 运行环境 | ubuntu-latest |
| 测试级别 | full |

## 失败详情

```
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 102[0m      [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 101[0m
     data_received[2m..................:[0m [36m66 kB[0m   [36;2m2.2 kB/s[0m
     data_sent[2m......................:[0m [36m36 kB[0m   [36;2m1.2 kB/s[0m
     group_duration[2m.................:[0m avg=[36m527.55µs[0m min=[36m359.87µs[0m med=[36m456.13µs[0m max=[36m1.64ms[0m   p(90)=[36m720.08µs[0m p(95)=[36m752.45µs[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 102[0m
     http_req_receiving[2m.............:[0m avg=[36m50.75µs[0m  min=[36m25.24µs[0m  med=[36m46.97µs[0m  max=[36m355.53µs[0m p(90)=[36m70.56µs[0m  p(95)=[36m76.59µs[0m 
     http_req_sending[2m...............:[0m avg=[36m22.72µs[0m  min=[36m8.97µs[0m   med=[36m19.95µs[0m  max=[36m63.92µs[0m  p(90)=[36m34.87µs[0m  p(95)=[36m37.63µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
  - Error Rate: 0.00%

🎯 Service Latency (P95)
  - Gateway: 0.48ms
--
[31m       ✗ AI Dashboard success
        ↳  0% — ✓ 0 / ✗ 4[0m
[32m       ✓ AI Fault Warning[0m
[32m       ✓ AI Health Monitor[0m

--
   [31m✗[0m ai_success[2m.....................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 4[0m  
     checks[2m.........................:[0m [36m96.29%[0m  [36;2m✓ 104[0m      [36;2m✗ 4[0m  
     data_received[2m..................:[0m [36m53 kB[0m   [36;2m1.7 kB/s[0m
     data_sent[2m......................:[0m [36m16 kB[0m   [36;2m531 B/s[0m
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 26[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.16ms[0m   min=[36m902.99µs[0m med=[36m1.16ms[0m   max=[36m1.43ms[0m   p(90)=[36m1.26ms[0m   p(95)=[36m1.39ms[0m   p(99)=[36m1.43ms[0m   count=[36m30[0m
     http_req_blocked[2m...............:[0m avg=[36m8.33µs[0m   min=[36m0s[0m       med=[36m2.97µs[0m   max=[36m311.05µs[0m p(90)=[36m6.02µs[0m   p(95)=[36m8.17µs[0m   p(99)=[36m165.32µs[0m count=[36m95[0m
     http_req_connecting[2m............:[0m avg=[36m2.37µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m119.28µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m107.23µs[0m count=[36m95[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m12.63%[0m  [36;2m✓ 12[0m       [36;2m✗ 83[0m 
     http_req_receiving[2m.............:[0m avg=[36m41.52µs[0m  min=[36m0s[0m       med=[36m39.88µs[0m  max=[36m243.16µs[0m p(90)=[36m66.94µs[0m  p(95)=[36m74.85µs[0m  p(99)=[36m97.83µs[0m  count=[36m95[0m
     http_req_sending[2m...............:[0m avg=[36m13.26µs[0m  min=[36m0s[0m       med=[36m8.19µs[0m   max=[36m81.05µs[0m  p(90)=[36m29.58µs[0m  p(95)=[36m32.18µs[0m  p(99)=[36m54.35µs[0m  count=[36m95[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m95[0m
--
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     p95_duration[2m...................:[0m avg=[36m0.423257[0m min=[36m0.303696[0m med=[36m0.436[0m    max=[36m0.492416[0m p(90)=[36m0.483346[0m p(95)=[36m0.487881[0m p(99)=[36m0.491509[0m count=[36m5[0m 
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     total_energy_requests[2m..........:[0m [36m30[0m      [36;2m0.998158/s[0m
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0mtime="2026-03-24T14:29:29Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/energy-load-results.json': open results/energy-load-results.json: no such file or directory"

--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m      [36;2m✗ 0[0m    
     data_received[2m..................:[0m [36m9.2 MB[0m  [36;2m306 kB/s[0m
     data_sent[2m......................:[0m [36m3.2 MB[0m  [36;2m105 kB/s[0m
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     group_duration[2m.................:[0m avg=[36m865.11µs[0m min=[36m414.74µs[0m med=[36m662.54µs[0m max=[36m3.27ms[0m   p(90)=[36m1.49ms[0m   p(95)=[36m1.64ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m2.97µs[0m   min=[36m1.38µs[0m   med=[36m2.54µs[0m   max=[36m921.1µs[0m  p(90)=[36m3.42µs[0m   p(95)=[36m3.85µs[0m  
     http_req_connecting[2m............:[0m avg=[36m13ns[0m     min=[36m0s[0m       med=[36m0s[0m       max=[36m100.61µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     http_req_receiving[2m.............:[0m avg=[36m31.02µs[0m  min=[36m12.07µs[0m  med=[36m28.44µs[0m  max=[36m457.94µs[0m p(90)=[36m41.36µs[0m  p(95)=[36m45.61µs[0m 
     http_req_sending[2m...............:[0m avg=[36m9.88µs[0m   min=[36m4.25µs[0m   med=[36m8.02µs[0m   max=[36m249.59µs[0m p(90)=[36m16.73µs[0m  p(95)=[36m19.1µs[0m  
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
time="2026-03-24T14:30:30Z" level=error msg="ReferenceError: textSummary is not defined\n\tat handleSummary (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/full-service-stress.js:437:24(16))\n" hint="script exception"


  █ THRESHOLDS 
--
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
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-24T14:30:30Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/load-test.js:55:28(15))\n" executor=constant-vus scenario=default source=stacktrace
```
