# ⚡ k6（性能压测） 测试报告

> **报告版本**：独立工具报告 v1.0  
> **生成时间**：2026-03-25 08:20:44 UTC  
> **数据来源**：GitHub Actions CI（full）  
> **覆盖基准**：147 文件 × ~24.8 检查点/文件（check() 调用）

---

## 📊 执行摘要

| 指标             | 数值               |
|------------------|--------------------|
| 标准用例数（基准）| 3651 |
| 实际执行检查点数 | 1798047 |
| 通过用例数       | 1797927 ✅ |
| 失败用例数       | 120 ❌ |
| 跳过用例数       | 0 ⏭️ |
| 通过率           | 99.99% |
| 执行总耗时       | 0s |
| 最后执行时间     | 2026-03-25T08:20:44 |
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
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 98[0m       [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 97[0m 
     data_received[2m..................:[0m [36m64 kB[0m   [36;2m2.1 kB/s[0m
     data_sent[2m......................:[0m [36m34 kB[0m   [36;2m1.1 kB/s[0m
     group_duration[2m.................:[0m avg=[36m590.21µs[0m min=[36m371.65µs[0m med=[36m528.47µs[0m max=[36m1.17ms[0m   p(90)=[36m833µs[0m    p(95)=[36m1.02ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 98[0m 
     http_req_receiving[2m.............:[0m avg=[36m47.2µs[0m   min=[36m26.63µs[0m  med=[36m44.98µs[0m  max=[36m96.79µs[0m  p(90)=[36m62.5µs[0m   p(95)=[36m69.82µs[0m 
     http_req_sending[2m...............:[0m avg=[36m22.52µs[0m  min=[36m9.37µs[0m   med=[36m20.43µs[0m  max=[36m81.76µs[0m  p(90)=[36m31.13µs[0m  p(95)=[36m42.34µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
  - Error Rate: 0.00%

🎯 Service Latency (P95)
  - Gateway: 0.61ms
--
   [32m✓[0m ai_success[2m.....................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 122[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m68 kB[0m   [36;2m2.3 kB/s[0m
     data_sent[2m......................:[0m [36m20 kB[0m   [36;2m668 B/s[0m
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 29[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.51ms[0m   min=[36m1.01ms[0m   med=[36m1.39ms[0m   max=[36m2.53ms[0m   p(90)=[36m2ms[0m      p(95)=[36m2.22ms[0m   p(99)=[36m2.46ms[0m   count=[36m34[0m 
     http_req_blocked[2m...............:[0m avg=[36m8.25µs[0m   min=[36m1.58µs[0m   med=[36m3.62µs[0m   max=[36m309.29µs[0m p(90)=[36m6.68µs[0m   p(95)=[36m7.47µs[0m   p(99)=[36m149.61µs[0m count=[36m107[0m
     http_req_connecting[2m............:[0m avg=[36m2.24µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m120.67µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m112.5µs[0m  count=[36m107[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 107[0m
     http_req_receiving[2m.............:[0m avg=[36m45.25µs[0m  min=[36m22.66µs[0m  med=[36m43.59µs[0m  max=[36m90.7µs[0m   p(90)=[36m65.86µs[0m  p(95)=[36m69.98µs[0m  p(99)=[36m75.29µs[0m  count=[36m107[0m
     http_req_sending[2m...............:[0m avg=[36m16.38µs[0m  min=[36m5.06µs[0m   med=[36m10.27µs[0m  max=[36m97.93µs[0m  p(90)=[36m29.39µs[0m  p(95)=[36m34.44µs[0m  p(99)=[36m95.22µs[0m  count=[36m107[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m107[0m
--
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     p95_duration[2m...................:[0m avg=[36m0.671171[0m min=[36m0.507709[0m med=[36m0.583029[0m max=[36m0.978253[0m p(90)=[36m0.887427[0m p(95)=[36m0.93284[0m  p(99)=[36m0.96917[0m  count=[36m5[0m  
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     total_energy_requests[2m..........:[0m [36m34[0m      [36;2m1.126667/s[0m
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.2s), 0/1 VUs, 34 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m      [36;2m✗ 0[0m    
     data_received[2m..................:[0m [36m9.2 MB[0m  [36;2m305 kB/s[0m
     data_sent[2m......................:[0m [36m3.2 MB[0m  [36;2m105 kB/s[0m
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     group_duration[2m.................:[0m avg=[36m905.32µs[0m min=[36m445.8µs[0m  med=[36m688.12µs[0m max=[36m7.06ms[0m   p(90)=[36m1.55ms[0m   p(95)=[36m1.74ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m2.94µs[0m   min=[36m1.42µs[0m   med=[36m2.63µs[0m   max=[36m313.44µs[0m p(90)=[36m3.56µs[0m   p(95)=[36m3.99µs[0m  
     http_req_connecting[2m............:[0m avg=[36m20ns[0m     min=[36m0s[0m       med=[36m0s[0m       max=[36m149.5µs[0m  p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     http_req_receiving[2m.............:[0m avg=[36m32.11µs[0m  min=[36m13.31µs[0m  med=[36m29.17µs[0m  max=[36m674.98µs[0m p(90)=[36m42.84µs[0m  p(95)=[36m47.86µs[0m 
     http_req_sending[2m...............:[0m avg=[36m10.44µs[0m  min=[36m4.3µs[0m    med=[36m8.3µs[0m    max=[36m1.15ms[0m   p(90)=[36m16.59µs[0m  p(95)=[36m19.59µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m global_success_rate[2m............:[0m [36m100.00%[0m [36;2m✓ 453[0m       [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.28ms[0m   min=[36m937.72µs[0m med=[36m1.24ms[0m   max=[36m2.22ms[0m   p(90)=[36m1.47ms[0m   p(95)=[36m1.73ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m4.78µs[0m   min=[36m1.86µs[0m   med=[36m3.2µs[0m    max=[36m266.12µs[0m p(90)=[36m5.67µs[0m   p(95)=[36m6.87µs[0m  
     http_req_connecting[2m............:[0m avg=[36m458ns[0m    min=[36m0s[0m       med=[36m0s[0m       max=[36m104.28µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 454[0m
     http_req_receiving[2m.............:[0m avg=[36m46.06µs[0m  min=[36m26.38µs[0m  med=[36m42.16µs[0m  max=[36m258.12µs[0m p(90)=[36m62.81µs[0m  p(95)=[36m69.14µs[0m 
     http_req_sending[2m...............:[0m avg=[36m15.02µs[0m  min=[36m5.55µs[0m   med=[36m11.42µs[0m  max=[36m110.01µs[0m p(90)=[36m28.94µs[0m  p(95)=[36m30.7µs[0m  
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     svc_analytics_success[2m..........:[0m [36m100.00%[0m [36;2m✓ 453[0m       [36;2m✗ 0[0m  
   [32m✓[0m svc_blockchain_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_charging_success[2m...........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_iotai_success[2m..............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_pvessc_success[2m.............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_settlement_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
running (0m30.1s), 0/1 VUs, 151 complete and 0 interrupted iterations
--
     api_success_rate[2m...............:[0m [36m100.00%[0m [36;2m✓ 22[0m       [36;2m✗ 0[0m  
     auth_success_rate[2m..............:[0m [36m100.00%[0m [36;2m✓ 1[0m        [36;2m✗ 0[0m  
     charging_api_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 22[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 46[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m15 kB[0m   [36;2m476 B/s[0m
     data_sent[2m......................:[0m [36m5.1 kB[0m  [36;2m163 B/s[0m
     group_duration[2m.................:[0m avg=[36m1s[0m       min=[36m1s[0m       med=[36m1s[0m       max=[36m1s[0m       p(90)=[36m1s[0m       p(95)=[36m1s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 23[0m 
     http_req_receiving[2m.............:[0m avg=[36m72.49µs[0m  min=[36m46.27µs[0m  med=[36m70.41µs[0m  max=[36m148.44µs[0m p(90)=[36m90.3µs[0m   p(95)=[36m97.29µs[0m 
     http_req_sending[2m...............:[0m avg=[36m35.21µs[0m  min=[36m23.68µs[0m  med=[36m33.1µs[0m   max=[36m88.56µs[0m  p(90)=[36m43.82µs[0m  p(95)=[36m61.49µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m carbontrade_success[2m............:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 134[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m88 kB[0m   [36;2m2.9 kB/s[0m
     data_sent[2m......................:[0m [36m28 kB[0m   [36;2m915 B/s[0m
   [32m✓[0m demandresp_event_success[2m.......:[0m [36m100.00%[0m [36;2m✓ 8[0m        [36;2m✗ 0[0m  
   [32m✓[0m deviceops_workorder_success[2m....:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m electrade_spot_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.18ms[0m   min=[36m424.51µs[0m med=[36m1.22ms[0m   max=[36m2.26ms[0m   p(90)=[36m1.56ms[0m   p(95)=[36m1.87ms[0m   p(99)=[36m2.14ms[0m   count=[36m53[0m 
     http_req_blocked[2m...............:[0m avg=[36m7.49µs[0m   min=[36m1.97µs[0m   med=[36m3.84µs[0m   max=[36m300.98µs[0m p(90)=[36m6.77µs[0m   p(95)=[36m7.36µs[0m   p(99)=[36m107.13µs[0m count=[36m135[0m
     http_req_connecting[2m............:[0m avg=[36m1.7µs[0m    min=[36m0s[0m       med=[36m0s[0m       max=[36m123.13µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m70.98µs[0m  count=[36m135[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 135[0m
     http_req_receiving[2m.............:[0m avg=[36m46.42µs[0m  min=[36m22.4µs[0m   med=[36m44.16µs[0m  max=[36m80.87µs[0m  p(90)=[36m64.57µs[0m  p(95)=[36m69.73µs[0m  p(99)=[36m79.84µs[0m  count=[36m135[0m
     http_req_sending[2m...............:[0m avg=[36m15.81µs[0m  min=[36m5.8µs[0m    med=[36m12.18µs[0m  max=[36m75.93µs[0m  p(90)=[36m25.7µs[0m   p(95)=[36m30.55µs[0m  p(99)=[36m48.62µs[0m  count=[36m135[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m135[0m
--
   [32m✓[0m microgrid_protection_success[2m...:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m overall_phase2_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 53[0m       [36;2m✗ 0[0m  
     phase2_api_latency[2m.............:[0m avg=[36m0.37486[0m  min=[36m0.185086[0m med=[36m0.301341[0m max=[36m0.937115[0m p(90)=[36m0.557722[0m p(95)=[36m0.710862[0m p(99)=[36m0.881611[0m count=[36m134[0m
     phase2_total_requests[2m..........:[0m [36m53[0m      [36;2m1.761286/s[0m
   [32m✓[0m vpp_enhanced_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.1s), 0/1 VUs, 53 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 60[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m15 kB[0m   [36;2m453 B/s[0m
     data_sent[2m......................:[0m [36m5.4 kB[0m  [36;2m170 B/s[0m
     group_duration[2m.................:[0m avg=[36m900.48µs[0m min=[36m664.17µs[0m med=[36m854.96µs[0m max=[36m1.17ms[0m   p(90)=[36m1.13ms[0m   p(95)=[36m1.16ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 28[0m 
     http_req_receiving[2m.............:[0m avg=[36m63.99µs[0m  min=[36m41.76µs[0m  med=[36m60.45µs[0m  max=[36m152.26µs[0m p(90)=[36m73.95µs[0m  p(95)=[36m75.32µs[0m 
     http_req_sending[2m...............:[0m avg=[36m32.54µs[0m  min=[36m16.29µs[0m  med=[36m30.98µs[0m  max=[36m59.19µs[0m  p(90)=[36m45.05µs[0m  p(95)=[36m53.21µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m32.0s), 0/1 VUs, 4 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 2[0m        [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m92 kB[0m   [36;2m3.0 kB/s[0m
     data_sent[2m......................:[0m [36m30 kB[0m   [36;2m999 B/s[0m
     error_rate[2m.....................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 145[0m
     http_req_blocked[2m...............:[0m avg=[36m7.85µs[0m   min=[36m2.72µs[0m   med=[36m5.02µs[0m   max=[36m278.2µs[0m  p(90)=[36m6.98µs[0m   p(95)=[36m10.76µs[0m 
     http_req_connecting[2m............:[0m avg=[36m1.49µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m118.58µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [32m✓[0m http_req_duration[2m..............:[0m avg=[36m465.95µs[0m min=[36m298.63µs[0m med=[36m453.5µs[0m  max=[36m950.34µs[0m p(90)=[36m612.37µs[0m p(95)=[36m737.96µs[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 146[0m
     http_req_receiving[2m.............:[0m avg=[36m52.03µs[0m  min=[36m31.21µs[0m  med=[36m51.89µs[0m  max=[36m138.64µs[0m p(90)=[36m65.04µs[0m  p(95)=[36m73.34µs[0m 
     http_req_sending[2m...............:[0m avg=[36m23.5µs[0m   min=[36m12.94µs[0m  med=[36m21.58µs[0m  max=[36m89.93µs[0m  p(90)=[36m31.35µs[0m  p(95)=[36m38.1µs[0m  
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     success_rate[2m...................:[0m [36m100.00%[0m [36;2m✓ 145[0m      [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.3s), 0/1 VUs, 31 complete and 0 interrupted iterations
--
    ✗ [S02] X-Content-Type-Options 存在
      ↳  0% — ✓ 0 / ✗ 60
    ✗ [S03] 未认证返回 401/403
      ↳  0% — ✓ 0 / ✗ 60
    ✓ [S04] Server 头不含 Kestrel

    CUSTOM
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 33[0m       [36;2m✗ 0[0m  
   [32m✓[0m dashboard_latency_ms[2m...........:[0m avg=[36m0.352203[0m min=[36m0.24083[0m  med=[36m0.281081[0m max=[36m0.828149[0m p(90)=[36m0.493713[0m p(95)=[36m0.660931[0m
     data_received[2m..................:[0m [36m29 kB[0m   [36;2m920 B/s[0m
     data_sent[2m......................:[0m [36m9.9 kB[0m  [36;2m315 B/s[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 50[0m 
     http_req_receiving[2m.............:[0m avg=[36m50.55µs[0m  min=[36m26.12µs[0m  med=[36m47.45µs[0m  max=[36m176.84µs[0m p(90)=[36m65.11µs[0m  p(95)=[36m80.46µs[0m 
     http_req_sending[2m...............:[0m avg=[36m23.5µs[0m   min=[36m9.54µs[0m   med=[36m20.48µs[0m  max=[36m75.53µs[0m  p(90)=[36m37.9µs[0m   p(95)=[36m43.3µs[0m  
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m operations_api_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 17[0m       [36;2m✗ 0[0m  
     total_api_requests[2m.............:[0m [36m25[0m      [36;2m0.793072/s[0m
   [32m✓[0m trading_api_success[2m............:[0m [36m100.00%[0m [36;2m✓ 8[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0mtime="2026-03-25T08:20:15Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/v320-operations-trading-results.json': open results/v320-operations-trading-results.json: no such file or directory"
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
