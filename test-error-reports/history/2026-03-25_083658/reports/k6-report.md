# ⚡ k6（性能压测） 测试报告

> **报告版本**：独立工具报告 v1.0  
> **生成时间**：2026-03-25 08:36:57 UTC  
> **数据来源**：GitHub Actions CI（full）  
> **覆盖基准**：147 文件 × ~24.8 检查点/文件（check() 调用）

---

## 📊 执行摘要

| 指标             | 数值               |
|------------------|--------------------|
| 标准用例数（基准）| 3651 |
| 实际执行检查点数 | 1380714 |
| 通过用例数       | 1380594 ✅ |
| 失败用例数       | 120 ❌ |
| 跳过用例数       | 0 ⏭️ |
| 通过率           | 99.99% |
| 执行总耗时       | 0s |
| 最后执行时间     | 2026-03-25T08:36:57 |
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
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 99[0m       [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 98[0m 
     data_received[2m..................:[0m [36m64 kB[0m   [36;2m2.1 kB/s[0m
     data_sent[2m......................:[0m [36m34 kB[0m   [36;2m1.1 kB/s[0m
     group_duration[2m.................:[0m avg=[36m735.66µs[0m min=[36m486.69µs[0m med=[36m707.73µs[0m max=[36m1.19ms[0m   p(90)=[36m984.56µs[0m p(95)=[36m1.01ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 99[0m 
     http_req_receiving[2m.............:[0m avg=[36m55.29µs[0m  min=[36m35.67µs[0m  med=[36m55.45µs[0m  max=[36m90.95µs[0m  p(90)=[36m65.93µs[0m  p(95)=[36m73.11µs[0m 
     http_req_sending[2m...............:[0m avg=[36m29.19µs[0m  min=[36m19µs[0m     med=[36m26.85µs[0m  max=[36m62.23µs[0m  p(90)=[36m35.15µs[0m  p(95)=[36m43.02µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
  - Error Rate: 0.00%

🎯 Service Latency (P95)
  - Gateway: 0.50ms
--
   [32m✓[0m ai_success[2m.....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 112[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m63 kB[0m   [36;2m2.0 kB/s[0m
     data_sent[2m......................:[0m [36m19 kB[0m   [36;2m608 B/s[0m
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 27[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.57ms[0m   min=[36m1.2ms[0m    med=[36m1.4ms[0m    max=[36m2.83ms[0m   p(90)=[36m2.12ms[0m   p(95)=[36m2.38ms[0m   p(99)=[36m2.69ms[0m   count=[36m31[0m
     http_req_blocked[2m...............:[0m avg=[36m9.88µs[0m   min=[36m1.69µs[0m   med=[36m3.5µs[0m    max=[36m287.32µs[0m p(90)=[36m7.17µs[0m   p(95)=[36m11.3µs[0m   p(99)=[36m188.59µs[0m count=[36m98[0m
     http_req_connecting[2m............:[0m avg=[36m2.52µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m135.92µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m111.78µs[0m count=[36m98[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 98[0m 
     http_req_receiving[2m.............:[0m avg=[36m45.69µs[0m  min=[36m22.08µs[0m  med=[36m43.9µs[0m   max=[36m94.6µs[0m   p(90)=[36m70.24µs[0m  p(95)=[36m74.66µs[0m  p(99)=[36m85.59µs[0m  count=[36m98[0m
     http_req_sending[2m...............:[0m avg=[36m16.16µs[0m  min=[36m5.33µs[0m   med=[36m11.98µs[0m  max=[36m60.54µs[0m  p(90)=[36m30.12µs[0m  p(95)=[36m33.61µs[0m  p(99)=[36m53.04µs[0m  count=[36m98[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m98[0m
--
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     p95_duration[2m...................:[0m avg=[36m0.589386[0m min=[36m0.480874[0m med=[36m0.522809[0m max=[36m0.827076[0m p(90)=[36m0.740875[0m p(95)=[36m0.783976[0m p(99)=[36m0.818456[0m count=[36m5[0m 
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     total_energy_requests[2m..........:[0m [36m31[0m      [36;2m1.014386/s[0m
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.6s), 0/1 VUs, 31 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m      [36;2m✗ 0[0m    
     data_received[2m..................:[0m [36m9.2 MB[0m  [36;2m305 kB/s[0m
     data_sent[2m......................:[0m [36m3.2 MB[0m  [36;2m105 kB/s[0m
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     group_duration[2m.................:[0m avg=[36m897.01µs[0m min=[36m460.88µs[0m med=[36m677.9µs[0m  max=[36m7.6ms[0m    p(90)=[36m1.53ms[0m   p(95)=[36m1.74ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m2.97µs[0m   min=[36m1.48µs[0m   med=[36m2.59µs[0m   max=[36m399.01µs[0m p(90)=[36m3.48µs[0m   p(95)=[36m4.13µs[0m  
     http_req_connecting[2m............:[0m avg=[36m25ns[0m     min=[36m0s[0m       med=[36m0s[0m       max=[36m246.69µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     http_req_receiving[2m.............:[0m avg=[36m31.81µs[0m  min=[36m11.91µs[0m  med=[36m28.84µs[0m  max=[36m1.14ms[0m   p(90)=[36m42.08µs[0m  p(95)=[36m46.32µs[0m 
     http_req_sending[2m...............:[0m avg=[36m9.99µs[0m   min=[36m4.34µs[0m   med=[36m8.03µs[0m   max=[36m264.6µs[0m  p(90)=[36m17.38µs[0m  p(95)=[36m19.49µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m global_success_rate[2m............:[0m [36m100.00%[0m [36;2m✓ 438[0m       [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.4ms[0m    min=[36m1.15ms[0m   med=[36m1.34ms[0m   max=[36m2.64ms[0m   p(90)=[36m1.59ms[0m   p(95)=[36m1.75ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m5.37µs[0m   min=[36m1.81µs[0m   med=[36m3.43µs[0m   max=[36m244.33µs[0m p(90)=[36m6.5µs[0m    p(95)=[36m7.12µs[0m  
     http_req_connecting[2m............:[0m avg=[36m533ns[0m    min=[36m0s[0m       med=[36m0s[0m       max=[36m126.11µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 439[0m
     http_req_receiving[2m.............:[0m avg=[36m47.55µs[0m  min=[36m24.36µs[0m  med=[36m44.74µs[0m  max=[36m139.77µs[0m p(90)=[36m64.98µs[0m  p(95)=[36m71.62µs[0m 
     http_req_sending[2m...............:[0m avg=[36m15.7µs[0m   min=[36m5.31µs[0m   med=[36m10.68µs[0m  max=[36m76.31µs[0m  p(90)=[36m28.38µs[0m  p(95)=[36m31.17µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     svc_analytics_success[2m..........:[0m [36m100.00%[0m [36;2m✓ 438[0m       [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
running (0m30.1s), 0/1 VUs, 146 complete and 0 interrupted iterations
--
     api_success_rate[2m...............:[0m [36m100.00%[0m [36;2m✓ 20[0m       [36;2m✗ 0[0m  
     auth_success_rate[2m..............:[0m [36m100.00%[0m [36;2m✓ 1[0m        [36;2m✗ 0[0m  
     charging_api_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 20[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 42[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m14 kB[0m   [36;2m449 B/s[0m
     data_sent[2m......................:[0m [36m4.5 kB[0m  [36;2m151 B/s[0m
     group_duration[2m.................:[0m avg=[36m1s[0m       min=[36m1s[0m       med=[36m1s[0m       max=[36m1s[0m       p(90)=[36m1s[0m       p(95)=[36m1s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 21[0m 
     http_req_receiving[2m.............:[0m avg=[36m73.87µs[0m  min=[36m38.89µs[0m  med=[36m64.54µs[0m  max=[36m288.68µs[0m p(90)=[36m81.6µs[0m   p(95)=[36m86.3µs[0m  
     http_req_sending[2m...............:[0m avg=[36m28.39µs[0m  min=[36m19.73µs[0m  med=[36m28.27µs[0m  max=[36m50.67µs[0m  p(90)=[36m40.66µs[0m  p(95)=[36m40.66µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m carbontrade_success[2m............:[0m [36m100.00%[0m [36;2m✓ 10[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 138[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m91 kB[0m   [36;2m3.0 kB/s[0m
     data_sent[2m......................:[0m [36m28 kB[0m   [36;2m931 B/s[0m
   [32m✓[0m demandresp_event_success[2m.......:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m deviceops_workorder_success[2m....:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m electrade_spot_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.21ms[0m   min=[36m573.68µs[0m med=[36m1.22ms[0m   max=[36m2.31ms[0m   p(90)=[36m1.59ms[0m   p(95)=[36m1.77ms[0m   p(99)=[36m2.25ms[0m   count=[36m55[0m 
     http_req_blocked[2m...............:[0m avg=[36m7.48µs[0m   min=[36m1.84µs[0m   med=[36m4.24µs[0m   max=[36m290.26µs[0m p(90)=[36m7.32µs[0m   p(95)=[36m8.09µs[0m   p(99)=[36m96.32µs[0m  count=[36m139[0m
     http_req_connecting[2m............:[0m avg=[36m1.72µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m127.8µs[0m  p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m69.23µs[0m  count=[36m139[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 139[0m
     http_req_receiving[2m.............:[0m avg=[36m47.81µs[0m  min=[36m22.55µs[0m  med=[36m43.77µs[0m  max=[36m92.83µs[0m  p(90)=[36m69.37µs[0m  p(95)=[36m72.35µs[0m  p(99)=[36m82.02µs[0m  count=[36m139[0m
     http_req_sending[2m...............:[0m avg=[36m16.93µs[0m  min=[36m5.71µs[0m   med=[36m13.47µs[0m  max=[36m49.63µs[0m  p(90)=[36m31.41µs[0m  p(95)=[36m34.04µs[0m  p(99)=[36m46.64µs[0m  count=[36m139[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m139[0m
--
   [32m✓[0m microgrid_protection_success[2m...:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m overall_phase2_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 55[0m       [36;2m✗ 0[0m  
     phase2_api_latency[2m.............:[0m avg=[36m0.380396[0m min=[36m0.184274[0m med=[36m0.284197[0m max=[36m0.962248[0m p(90)=[36m0.574223[0m p(95)=[36m0.674762[0m p(99)=[36m0.883686[0m count=[36m138[0m
     phase2_total_requests[2m..........:[0m [36m55[0m      [36;2m1.805392/s[0m
   [32m✓[0m vpp_enhanced_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.5s), 0/1 VUs, 55 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 60[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m15 kB[0m   [36;2m453 B/s[0m
     data_sent[2m......................:[0m [36m5.4 kB[0m  [36;2m170 B/s[0m
     group_duration[2m.................:[0m avg=[36m995.9µs[0m  min=[36m709.9µs[0m  med=[36m892.15µs[0m max=[36m1.85ms[0m   p(90)=[36m1.25ms[0m   p(95)=[36m1.66ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 28[0m 
     http_req_receiving[2m.............:[0m avg=[36m72.79µs[0m  min=[36m40.46µs[0m  med=[36m67.18µs[0m  max=[36m254.27µs[0m p(90)=[36m87.04µs[0m  p(95)=[36m90.51µs[0m 
     http_req_sending[2m...............:[0m avg=[36m38.96µs[0m  min=[36m22.98µs[0m  med=[36m29.73µs[0m  max=[36m185.04µs[0m p(90)=[36m44.81µs[0m  p(95)=[36m95.15µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m32.0s), 0/1 VUs, 4 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 2[0m        [36;2m✗ 0[0m  
     connection_errors[2m..............:[0m [36m22[0m      [36;2m0.715176/s[0m
     data_received[2m..................:[0m [36m84 kB[0m   [36;2m2.7 kB/s[0m
     data_sent[2m......................:[0m [36m29 kB[0m   [36;2m938 B/s[0m
     error_rate[2m.....................:[0m [36m14.10%[0m  [36;2m✓ 22[0m       [36;2m✗ 134[0m
     http_req_blocked[2m...............:[0m avg=[36m10.75µs[0m  min=[36m2.63µs[0m   med=[36m5.77µs[0m   max=[36m334.71µs[0m p(90)=[36m8.24µs[0m   p(95)=[36m10.43µs[0m 
     http_req_connecting[2m............:[0m avg=[36m2.35µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m169.61µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [32m✓[0m http_req_duration[2m..............:[0m avg=[36m549.79µs[0m min=[36m285.12µs[0m med=[36m544.76µs[0m max=[36m980.15µs[0m p(90)=[36m715.26µs[0m p(95)=[36m830.61µs[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 135[0m
     http_req_receiving[2m.............:[0m avg=[36m62.25µs[0m  min=[36m28.61µs[0m  med=[36m60.7µs[0m   max=[36m153.04µs[0m p(90)=[36m83.32µs[0m  p(95)=[36m94.23µs[0m 
     http_req_sending[2m...............:[0m avg=[36m28.71µs[0m  min=[36m14.75µs[0m  med=[36m25.98µs[0m  max=[36m81.08µs[0m  p(90)=[36m39.79µs[0m  p(95)=[36m45.07µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     success_rate[2m...................:[0m [36m100.00%[0m [36;2m✓ 134[0m      [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.8s), 0/1 VUs, 32 complete and 0 interrupted iterations
--
    ✗ [S02] X-Content-Type-Options 存在
      ↳  0% — ✓ 0 / ✗ 60
    ✗ [S03] 未认证返回 401/403
      ↳  0% — ✓ 0 / ✗ 60
    ✓ [S04] Server 头不含 Kestrel

    CUSTOM
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 28[0m       [36;2m✗ 0[0m  
   [32m✓[0m dashboard_latency_ms[2m...........:[0m avg=[36m0.293382[0m min=[36m0.234468[0m med=[36m0.268918[0m max=[36m0.417288[0m p(90)=[36m0.361916[0m p(95)=[36m0.389602[0m
     data_received[2m..................:[0m [36m27 kB[0m   [36;2m852 B/s[0m
     data_sent[2m......................:[0m [36m9.2 kB[0m  [36;2m295 B/s[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 46[0m 
     http_req_receiving[2m.............:[0m avg=[36m49.84µs[0m  min=[36m27.82µs[0m  med=[36m50.9µs[0m   max=[36m80.57µs[0m  p(90)=[36m67.19µs[0m  p(95)=[36m73.72µs[0m 
     http_req_sending[2m...............:[0m avg=[36m26.09µs[0m  min=[36m7.19µs[0m   med=[36m22.24µs[0m  max=[36m67.45µs[0m  p(90)=[36m42.79µs[0m  p(95)=[36m48.5µs[0m  
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m operations_api_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     total_api_requests[2m.............:[0m [36m23[0m      [36;2m0.739856/s[0m
   [32m✓[0m trading_api_success[2m............:[0m [36m100.00%[0m [36;2m✓ 14[0m       [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0mtime="2026-03-25T08:33:17Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/v320-operations-trading-results.json': open results/v320-operations-trading-results.json: no such file or directory"
```

---

## 🚦 发布门禁检查

| 检查项                   | 状态 |
|--------------------------|------|
| 测试已执行               | ✅ 是 |
| 无失败用例               | ❌ 否（120 条失败） |
| 无异常态（非全跳过）     | ✅ 正常 |
| 实际执行场景文件数 | ✅ 45 |
| 通过率 ≥ 95%             | ✅ 99.99% |

**最终结论**：🔴 **不可发布**

---

*本报告由 `generate-ci-report.sh` 自动生成，结构与本地独立工具报告保持一致。*
*如需重新生成：`.github/scripts/generate-ci-report.sh k6 ...`*
