# ⚡ k6（性能压测） 测试报告

> **报告版本**：独立工具报告 v1.0  
> **生成时间**：2026-03-25 07:38:37 UTC  
> **数据来源**：GitHub Actions CI（full）  
> **覆盖基准**：147 文件 × ~24.8 检查点/文件（check() 调用）

---

## 📊 执行摘要

| 指标             | 数值               |
|------------------|--------------------|
| 标准用例数（基准）| 3651 |
| 实际执行检查点数 | 1399532 |
| 通过用例数       | 1399412 ✅ |
| 失败用例数       | 120 ❌ |
| 跳过用例数       | 0 ⏭️ |
| 通过率           | 99.99% |
| 执行总耗时       | 0s |
| 最后执行时间     | 2026-03-25T07:38:37 |
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
     group_duration[2m.................:[0m avg=[36m811.61µs[0m min=[36m632.3µs[0m  med=[36m764.77µs[0m max=[36m1.64ms[0m   p(90)=[36m999.16µs[0m p(95)=[36m1.09ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 99[0m 
     http_req_receiving[2m.............:[0m avg=[36m59.16µs[0m  min=[36m37.15µs[0m  med=[36m56.85µs[0m  max=[36m101.07µs[0m p(90)=[36m77.15µs[0m  p(95)=[36m79.85µs[0m 
     http_req_sending[2m...............:[0m avg=[36m32.48µs[0m  min=[36m25.02µs[0m  med=[36m32.36µs[0m  max=[36m89.7µs[0m   p(90)=[36m39µs[0m     p(95)=[36m42.78µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
  - Error Rate: 0.00%

🎯 Service Latency (P95)
  - Gateway: 0.49ms
--
   [32m✓[0m ai_success[2m.....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 104[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m59 kB[0m   [36;2m1.9 kB/s[0m
     data_sent[2m......................:[0m [36m17 kB[0m   [36;2m566 B/s[0m
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.57ms[0m   min=[36m1.2ms[0m    med=[36m1.48ms[0m   max=[36m2.99ms[0m   p(90)=[36m2.06ms[0m   p(95)=[36m2.15ms[0m   p(99)=[36m2.77ms[0m   count=[36m29[0m
     http_req_blocked[2m...............:[0m avg=[36m9.22µs[0m   min=[36m1.64µs[0m   med=[36m3.36µs[0m   max=[36m317.47µs[0m p(90)=[36m6.65µs[0m   p(95)=[36m9.48µs[0m   p(99)=[36m179.17µs[0m count=[36m92[0m
     http_req_connecting[2m............:[0m avg=[36m2.79µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m148.9µs[0m  p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m111.7µs[0m  count=[36m92[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 92[0m 
     http_req_receiving[2m.............:[0m avg=[36m47.86µs[0m  min=[36m22.46µs[0m  med=[36m45.53µs[0m  max=[36m110.92µs[0m p(90)=[36m69.52µs[0m  p(95)=[36m80.5µs[0m   p(99)=[36m101.18µs[0m count=[36m92[0m
     http_req_sending[2m...............:[0m avg=[36m15.57µs[0m  min=[36m5.27µs[0m   med=[36m10.05µs[0m  max=[36m90.02µs[0m  p(90)=[36m30.48µs[0m  p(95)=[36m31.64µs[0m  p(99)=[36m47.16µs[0m  count=[36m92[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m92[0m
--
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     p95_duration[2m...................:[0m avg=[36m0.564648[0m min=[36m0.456556[0m med=[36m0.547904[0m max=[36m0.744511[0m p(90)=[36m0.683185[0m p(95)=[36m0.713848[0m p(99)=[36m0.738378[0m count=[36m5[0m 
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     total_energy_requests[2m..........:[0m [36m29[0m      [36;2m0.943169/s[0m
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.7s), 0/1 VUs, 29 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m     [36;2m✗ 0[0m    
     data_received[2m..................:[0m [36m9.2 MB[0m  [36;2m306 kB/s[0m
     data_sent[2m......................:[0m [36m3.2 MB[0m  [36;2m105 kB/s[0m
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
     group_duration[2m.................:[0m avg=[36m868.08µs[0m min=[36m398.09µs[0m med=[36m666.6µs[0m  max=[36m6.68ms[0m   p(90)=[36m1.44ms[0m   p(95)=[36m1.6ms[0m   
     http_req_blocked[2m...............:[0m avg=[36m2.79µs[0m   min=[36m1.36µs[0m   med=[36m2.49µs[0m   max=[36m261.52µs[0m p(90)=[36m3.3µs[0m    p(95)=[36m3.61µs[0m  
     http_req_connecting[2m............:[0m avg=[36m15ns[0m     min=[36m0s[0m       med=[36m0s[0m       max=[36m116.6µs[0m  p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 14352[0m
     http_req_receiving[2m.............:[0m avg=[36m31.15µs[0m  min=[36m11.84µs[0m  med=[36m28.51µs[0m  max=[36m767.82µs[0m p(90)=[36m41.71µs[0m  p(95)=[36m45.48µs[0m 
     http_req_sending[2m...............:[0m avg=[36m9.81µs[0m   min=[36m3.9µs[0m    med=[36m7.89µs[0m   max=[36m1.08ms[0m   p(90)=[36m16.5µs[0m   p(95)=[36m18.92µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m global_success_rate[2m............:[0m [36m100.00%[0m [36;2m✓ 441[0m       [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.28ms[0m   min=[36m896.56µs[0m med=[36m1.25ms[0m   max=[36m2.46ms[0m   p(90)=[36m1.49ms[0m   p(95)=[36m1.75ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m4.75µs[0m   min=[36m1.67µs[0m   med=[36m3.17µs[0m   max=[36m233.25µs[0m p(90)=[36m5.88µs[0m   p(95)=[36m6.85µs[0m  
     http_req_connecting[2m............:[0m avg=[36m452ns[0m    min=[36m0s[0m       med=[36m0s[0m       max=[36m104.21µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 442[0m
     http_req_receiving[2m.............:[0m avg=[36m44.44µs[0m  min=[36m20.92µs[0m  med=[36m41.3µs[0m   max=[36m388.53µs[0m p(90)=[36m61.69µs[0m  p(95)=[36m68.02µs[0m 
     http_req_sending[2m...............:[0m avg=[36m14.35µs[0m  min=[36m4.76µs[0m   med=[36m9.67µs[0m   max=[36m88.42µs[0m  p(90)=[36m27.21µs[0m  p(95)=[36m29.64µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     svc_analytics_success[2m..........:[0m [36m100.00%[0m [36;2m✓ 441[0m       [36;2m✗ 0[0m  
   [32m✓[0m svc_blockchain_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_charging_success[2m...........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_iotai_success[2m..............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_pvessc_success[2m.............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_settlement_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
running (0m30.1s), 0/1 VUs, 147 complete and 0 interrupted iterations
--
     api_success_rate[2m...............:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
     auth_success_rate[2m..............:[0m [36m100.00%[0m [36;2m✓ 1[0m        [36;2m✗ 0[0m  
     charging_api_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 25[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 52[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m17 kB[0m   [36;2m557 B/s[0m
     data_sent[2m......................:[0m [36m5.7 kB[0m  [36;2m189 B/s[0m
     group_duration[2m.................:[0m avg=[36m1s[0m       min=[36m1s[0m       med=[36m1s[0m       max=[36m1s[0m       p(90)=[36m1s[0m       p(95)=[36m1s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 26[0m 
     http_req_receiving[2m.............:[0m avg=[36m60.63µs[0m  min=[36m39.87µs[0m  med=[36m59.01µs[0m  max=[36m95.91µs[0m  p(90)=[36m86.22µs[0m  p(95)=[36m90.38µs[0m 
     http_req_sending[2m...............:[0m avg=[36m29.02µs[0m  min=[36m20.77µs[0m  med=[36m25.76µs[0m  max=[36m92.11µs[0m  p(90)=[36m35.1µs[0m   p(95)=[36m40.07µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m carbontrade_success[2m............:[0m [36m100.00%[0m [36;2m✓ 10[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 141[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m92 kB[0m   [36;2m3.0 kB/s[0m
     data_sent[2m......................:[0m [36m29 kB[0m   [36;2m951 B/s[0m
   [32m✓[0m demandresp_event_success[2m.......:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m deviceops_workorder_success[2m....:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m electrade_spot_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.25ms[0m   min=[36m599.94µs[0m med=[36m1.26ms[0m   max=[36m2.29ms[0m   p(90)=[36m1.65ms[0m   p(95)=[36m1.96ms[0m   p(99)=[36m2.2ms[0m    count=[36m56[0m 
     http_req_blocked[2m...............:[0m avg=[36m8.26µs[0m   min=[36m1.9µs[0m    med=[36m4.11µs[0m   max=[36m314.95µs[0m p(90)=[36m7.05µs[0m   p(95)=[36m7.89µs[0m   p(99)=[36m132.42µs[0m count=[36m142[0m
     http_req_connecting[2m............:[0m avg=[36m1.74µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m135.8µs[0m  p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m65.87µs[0m  count=[36m142[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 142[0m
     http_req_receiving[2m.............:[0m avg=[36m48.04µs[0m  min=[36m22.07µs[0m  med=[36m46.31µs[0m  max=[36m93.84µs[0m  p(90)=[36m69.39µs[0m  p(95)=[36m73.77µs[0m  p(99)=[36m82.53µs[0m  count=[36m142[0m
     http_req_sending[2m...............:[0m avg=[36m16.82µs[0m  min=[36m5.49µs[0m   med=[36m13.07µs[0m  max=[36m61.64µs[0m  p(90)=[36m28.11µs[0m  p(95)=[36m35.95µs[0m  p(99)=[36m57.02µs[0m  count=[36m142[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m142[0m
--
   [32m✓[0m microgrid_protection_success[2m...:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m overall_phase2_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 56[0m       [36;2m✗ 0[0m  
     phase2_api_latency[2m.............:[0m avg=[36m0.395691[0m min=[36m0.180837[0m med=[36m0.326664[0m max=[36m1.005675[0m p(90)=[36m0.585506[0m p(95)=[36m0.728672[0m p(99)=[36m0.921496[0m count=[36m141[0m
     phase2_total_requests[2m..........:[0m [36m56[0m      [36;2m1.837769/s[0m
   [32m✓[0m vpp_enhanced_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 10[0m       [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0mtime="2026-03-25T07:35:55Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/phase2-energy-baseline-results.json': open results/phase2-energy-baseline-results.json: no such file or directory"

--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 60[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m15 kB[0m   [36;2m453 B/s[0m
     data_sent[2m......................:[0m [36m5.4 kB[0m  [36;2m170 B/s[0m
     group_duration[2m.................:[0m avg=[36m914.37µs[0m min=[36m631.96µs[0m med=[36m873.35µs[0m max=[36m1.66ms[0m   p(90)=[36m1.19ms[0m   p(95)=[36m1.41ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 28[0m 
     http_req_receiving[2m.............:[0m avg=[36m63.28µs[0m  min=[36m38.34µs[0m  med=[36m66.21µs[0m  max=[36m82.64µs[0m  p(90)=[36m78.87µs[0m  p(95)=[36m81.16µs[0m 
     http_req_sending[2m...............:[0m avg=[36m31.47µs[0m  min=[36m20.05µs[0m  med=[36m26.16µs[0m  max=[36m66.87µs[0m  p(90)=[36m49.48µs[0m  p(95)=[36m62.27µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0mtime="2026-03-25T07:37:02Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/smoke-results.json': open results/smoke-results.json: no such file or directory"

--
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
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
time="2026-03-25T07:36:33Z" level=error msg="TypeError: Value is not an object: null\n\tat default (file:///home/runner/work/test-only-cloud/test-only-cloud/testing/k6/scenarios/stress-test.js:49:28(20))\n" executor=constant-vus scenario=default source=stacktrace
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
