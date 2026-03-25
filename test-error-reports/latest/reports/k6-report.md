# ⚡ k6（性能压测） 测试报告

> **报告版本**：独立工具报告 v1.0  
> **生成时间**：2026-03-25 06:33:57 UTC  
> **数据来源**：GitHub Actions CI（full）  
> **覆盖基准**：147 文件 × ~24.8 检查点/文件（check() 调用）

---

## 📊 执行摘要

| 指标             | 数值               |
|------------------|--------------------|
| 标准用例数（基准）| 3651 |
| 实际执行检查点数 | 1409927 |
| 通过用例数       | 1409803 ✅ |
| 失败用例数       | 124 ❌ |
| 跳过用例数       | 0 ⏭️ |
| 通过率           | 99.99% |
| 执行总耗时       | 0s |
| 最后执行时间     | 2026-03-25T06:33:57 |
| 发布门禁状态     | 🔴 **不可发布** |

---

## 📁 文件级执行结果（45 个测试文件）

| 状态 | 文件路径 | 总计 | 通过 | 失败 | 跳过 | 耗时 |
|------|---------|------|------|------|------|------|
| ⚪ | `scenario-1` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-2` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-3` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-4` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-5` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-6` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-7` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-8` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-9` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-10` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-11` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-12` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-13` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-14` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-15` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-16` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-17` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-18` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-19` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-20` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-21` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-22` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-23` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-24` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-25` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-26` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-27` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-28` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-29` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-30` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-31` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-32` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-33` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-34` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-35` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-36` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-37` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-38` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-39` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-40` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-41` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-42` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-43` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-44` | 0 | 0 | 0 | 0 | 0s |
| ⚪ | `scenario-45` | 0 | 0 | 0 | 0 | 0s |

---

## ❌ 失败用例详情（共 1 条）


```
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 105[0m      [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 104[0m
     data_received[2m..................:[0m [36m68 kB[0m   [36;2m2.2 kB/s[0m
     data_sent[2m......................:[0m [36m37 kB[0m   [36;2m1.2 kB/s[0m
     group_duration[2m.................:[0m avg=[36m747.93µs[0m min=[36m375.1µs[0m  med=[36m733.51µs[0m max=[36m1.6ms[0m    p(90)=[36m928.11µs[0m p(95)=[36m1.04ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 105[0m
     http_req_receiving[2m.............:[0m avg=[36m55.65µs[0m  min=[36m32.19µs[0m  med=[36m55.76µs[0m  max=[36m264.06µs[0m p(90)=[36m66.29µs[0m  p(95)=[36m73.51µs[0m 
     http_req_sending[2m...............:[0m avg=[36m31.58µs[0m  min=[36m10.35µs[0m  med=[36m32.29µs[0m  max=[36m73.34µs[0m  p(90)=[36m41.83µs[0m  p(95)=[36m47.37µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
  - Error Rate: 0.00%

🎯 Service Latency (P95)
  - Gateway: 0.64ms
--
[31m       ✗ AI Dashboard success
        ↳  0% — ✓ 0 / ✗ 4[0m
[32m       ✓ AI Fault Warning[0m
[32m       ✓ AI Health Monitor[0m

--
   [31m✗[0m ai_success[2m.....................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 4[0m  
     checks[2m.........................:[0m [36m96.15%[0m  [36;2m✓ 100[0m      [36;2m✗ 4[0m  
     data_received[2m..................:[0m [36m51 kB[0m   [36;2m1.7 kB/s[0m
     data_sent[2m......................:[0m [36m15 kB[0m   [36;2m509 B/s[0m
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.46ms[0m   min=[36m946.98µs[0m med=[36m1.38ms[0m   max=[36m2.29ms[0m   p(90)=[36m2.01ms[0m   p(95)=[36m2.09ms[0m   p(99)=[36m2.25ms[0m   count=[36m29[0m
     http_req_blocked[2m...............:[0m avg=[36m7.92µs[0m   min=[36m0s[0m       med=[36m3.13µs[0m   max=[36m291.91µs[0m p(90)=[36m6.03µs[0m   p(95)=[36m6.62µs[0m   p(99)=[36m155.49µs[0m count=[36m92[0m
     http_req_connecting[2m............:[0m avg=[36m2.22µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m111.61µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m94.96µs[0m  count=[36m92[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m13.04%[0m  [36;2m✓ 12[0m       [36;2m✗ 80[0m 
     http_req_receiving[2m.............:[0m avg=[36m39.7µs[0m   min=[36m0s[0m       med=[36m41.72µs[0m  max=[36m92.48µs[0m  p(90)=[36m62.89µs[0m  p(95)=[36m69.1µs[0m   p(99)=[36m76.42µs[0m  count=[36m92[0m
     http_req_sending[2m...............:[0m avg=[36m13.63µs[0m  min=[36m0s[0m       med=[36m9.43µs[0m   max=[36m76.62µs[0m  p(90)=[36m26.65µs[0m  p(95)=[36m31.83µs[0m  p(99)=[36m51.89µs[0m  count=[36m92[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m92[0m
--
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     p95_duration[2m...................:[0m avg=[36m0.58642[0m  min=[36m0.495642[0m med=[36m0.51577[0m  max=[36m0.812509[0m p(90)=[36m0.730415[0m p(95)=[36m0.771462[0m p(99)=[36m0.8043[0m   count=[36m5[0m 
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     total_energy_requests[2m..........:[0m [36m29[0m      [36;2m0.959169/s[0m
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0mtime="2026-03-25T06:31:05Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/energy-load-results.json': open results/energy-load-results.json: no such file or directory"

--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m     [36;2m✗ 0[0m    
     data_received[2m..................:[0m [36m9.2 MB[0m  [36;2m305 kB/s[0m
     data_sent[2m......................:[0m [36m3.2 MB[0m  [36;2m105 kB/s[0m
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
     group_duration[2m.................:[0m avg=[36m877.54µs[0m min=[36m441.55µs[0m med=[36m664.54µs[0m max=[36m6.62ms[0m   p(90)=[36m1.5ms[0m    p(95)=[36m1.68ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m3.11µs[0m   min=[36m1.36µs[0m   med=[36m2.61µs[0m   max=[36m1.12ms[0m   p(90)=[36m3.44µs[0m   p(95)=[36m3.79µs[0m  
     http_req_connecting[2m............:[0m avg=[36m15ns[0m     min=[36m0s[0m       med=[36m0s[0m       max=[36m114.46µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
     http_req_receiving[2m.............:[0m avg=[36m30.7µs[0m   min=[36m11.82µs[0m  med=[36m27.97µs[0m  max=[36m1.69ms[0m   p(90)=[36m41.56µs[0m  p(95)=[36m45.71µs[0m 
     http_req_sending[2m...............:[0m avg=[36m9.83µs[0m   min=[36m4.18µs[0m   med=[36m7.99µs[0m   max=[36m311.04µs[0m p(90)=[36m16.08µs[0m  p(95)=[36m19.47µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m global_success_rate[2m............:[0m [36m100.00%[0m [36;2m✓ 471[0m       [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.22ms[0m   min=[36m873.5µs[0m  med=[36m1.19ms[0m   max=[36m2.19ms[0m   p(90)=[36m1.43ms[0m   p(95)=[36m1.58ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m4.61µs[0m   min=[36m1.88µs[0m   med=[36m3.19µs[0m   max=[36m275.06µs[0m p(90)=[36m5.42µs[0m   p(95)=[36m6.05µs[0m  
     http_req_connecting[2m............:[0m avg=[36m538ns[0m    min=[36m0s[0m       med=[36m0s[0m       max=[36m135.41µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 472[0m
     http_req_receiving[2m.............:[0m avg=[36m43.47µs[0m  min=[36m21.99µs[0m  med=[36m40.77µs[0m  max=[36m180.48µs[0m p(90)=[36m60.3µs[0m   p(95)=[36m67.31µs[0m 
     http_req_sending[2m...............:[0m avg=[36m13.47µs[0m  min=[36m4.98µs[0m   med=[36m9.71µs[0m   max=[36m63.96µs[0m  p(90)=[36m25.64µs[0m  p(95)=[36m28.89µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     svc_analytics_success[2m..........:[0m [36m100.00%[0m [36;2m✓ 471[0m       [36;2m✗ 0[0m  
   [32m✓[0m svc_blockchain_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_charging_success[2m...........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_iotai_success[2m..............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_pvessc_success[2m.............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_settlement_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0mtime="2026-03-25T06:31:02Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/full-service-stress.json': open results/full-service-stress.json: no such file or directory"

--
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

---

## 🚦 发布门禁检查

| 检查项                   | 状态 |
|--------------------------|------|
| 测试已执行               | ✅ 是 |
| 无失败用例               | ❌ 否（124 条失败） |
| 无异常态（非全跳过）     | ✅ 正常 |
| 实际执行场景文件数 | ✅ 45 |
| 通过率 ≥ 95%             | ✅ 99.99% |

**最终结论**：🔴 **不可发布**

---

*本报告由 `generate-ci-report.sh` 自动生成，结构与本地独立工具报告保持一致。*
*如需重新生成：`.github/scripts/generate-ci-report.sh k6 ...`*
