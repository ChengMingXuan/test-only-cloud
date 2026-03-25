# ⚡ k6（性能压测） 测试报告

> **报告版本**：独立工具报告 v1.0  
> **生成时间**：2026-03-25 07:47:34 UTC  
> **数据来源**：GitHub Actions CI（full）  
> **覆盖基准**：147 文件 × ~24.8 检查点/文件（check() 调用）

---

## 📊 执行摘要

| 指标             | 数值               |
|------------------|--------------------|
| 标准用例数（基准）| 3651 |
| 实际执行检查点数 | 1427790 |
| 通过用例数       | 1427670 ✅ |
| 失败用例数       | 120 ❌ |
| 跳过用例数       | 0 ⏭️ |
| 通过率           | 99.99% |
| 执行总耗时       | 0s |
| 最后执行时间     | 2026-03-25T07:47:34 |
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
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 102[0m      [36;2m✗ 0[0m  
   [32m✓[0m concurrency_conflict_rate[2m......:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 101[0m
     data_received[2m..................:[0m [36m66 kB[0m   [36;2m2.2 kB/s[0m
     data_sent[2m......................:[0m [36m36 kB[0m   [36;2m1.2 kB/s[0m
     group_duration[2m.................:[0m avg=[36m802.74µs[0m min=[36m504.44µs[0m med=[36m765.83µs[0m max=[36m1.55ms[0m   p(90)=[36m1.02ms[0m   p(95)=[36m1.09ms[0m  
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 102[0m
     http_req_receiving[2m.............:[0m avg=[36m56.69µs[0m  min=[36m33.72µs[0m  med=[36m55.1µs[0m   max=[36m199.65µs[0m p(90)=[36m68.32µs[0m  p(95)=[36m72.79µs[0m 
     http_req_sending[2m...............:[0m avg=[36m33.74µs[0m  min=[36m15.79µs[0m  med=[36m34.24µs[0m  max=[36m107.23µs[0m p(90)=[36m40.85µs[0m  p(95)=[36m44.84µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
  - Error Rate: 0.00%

🎯 Service Latency (P95)
  - Gateway: 0.00ms
--
   [32m✓[0m ai_success[2m.....................:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 108[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m61 kB[0m   [36;2m2.0 kB/s[0m
     data_sent[2m......................:[0m [36m18 kB[0m   [36;2m580 B/s[0m
   [32m✓[0m energy_api_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 26[0m       [36;2m✗ 0[0m  
   [32m✓[0m energy_svc_success[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.55ms[0m   min=[36m1.17ms[0m   med=[36m1.43ms[0m   max=[36m2.59ms[0m   p(90)=[36m2.01ms[0m   p(95)=[36m2.23ms[0m   p(99)=[36m2.51ms[0m   count=[36m30[0m
     http_req_blocked[2m...............:[0m avg=[36m9.4µs[0m    min=[36m1.86µs[0m   med=[36m3.32µs[0m   max=[36m349.25µs[0m p(90)=[36m7.11µs[0m   p(95)=[36m7.94µs[0m   p(99)=[36m172.48µs[0m count=[36m95[0m
     http_req_connecting[2m............:[0m avg=[36m2.26µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m125.27µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m92.28µs[0m  count=[36m95[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 95[0m 
     http_req_receiving[2m.............:[0m avg=[36m49.34µs[0m  min=[36m21.76µs[0m  med=[36m45.94µs[0m  max=[36m254.1µs[0m  p(90)=[36m69.51µs[0m  p(95)=[36m73.7µs[0m   p(99)=[36m96.69µs[0m  count=[36m95[0m
     http_req_sending[2m...............:[0m avg=[36m15.13µs[0m  min=[36m5.87µs[0m   med=[36m10.35µs[0m  max=[36m61.26µs[0m  p(90)=[36m29.54µs[0m  p(95)=[36m35.96µs[0m  p(99)=[36m58.52µs[0m  count=[36m95[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m95[0m
--
   [32m✓[0m microgrid_success[2m..............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     p95_duration[2m...................:[0m avg=[36m0.61117[0m  min=[36m0.475045[0m med=[36m0.563488[0m max=[36m0.872786[0m p(90)=[36m0.761441[0m p(95)=[36m0.817114[0m p(99)=[36m0.861652[0m count=[36m5[0m 
   [32m✓[0m pvessc_success[2m.................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     total_energy_requests[2m..........:[0m [36m30[0m      [36;2m0.968473/s[0m
   [32m✓[0m vpp_success[2m....................:[0m [36m100.00%[0m [36;2m✓ 5[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m31.0s), 0/1 VUs, 30 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 43056[0m      [36;2m✗ 0[0m    
     data_received[2m..................:[0m [36m9.2 MB[0m  [36;2m305 kB/s[0m
     data_sent[2m......................:[0m [36m3.2 MB[0m  [36;2m105 kB/s[0m
   [32m✓[0m errors[2m.........................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     group_duration[2m.................:[0m avg=[36m889.11µs[0m min=[36m413.87µs[0m med=[36m680.13µs[0m max=[36m6.8ms[0m    p(90)=[36m1.51ms[0m   p(95)=[36m1.71ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m2.88µs[0m   min=[36m1.37µs[0m   med=[36m2.55µs[0m   max=[36m386.08µs[0m p(90)=[36m3.43µs[0m   p(95)=[36m3.98µs[0m  
     http_req_connecting[2m............:[0m avg=[36m26ns[0m     min=[36m0s[0m       med=[36m0s[0m       max=[36m213.46µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m          [36;2m✗ 14352[0m
     http_req_receiving[2m.............:[0m avg=[36m31.62µs[0m  min=[36m11.41µs[0m  med=[36m28.94µs[0m  max=[36m542.45µs[0m p(90)=[36m42.49µs[0m  p(95)=[36m46.89µs[0m 
     http_req_sending[2m...............:[0m avg=[36m10.2µs[0m   min=[36m4.25µs[0m   med=[36m8.12µs[0m   max=[36m876.01µs[0m p(90)=[36m17.21µs[0m  p(95)=[36m19.39µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m global_success_rate[2m............:[0m [36m100.00%[0m [36;2m✓ 405[0m       [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.26ms[0m   min=[36m991.39µs[0m med=[36m1.23ms[0m   max=[36m2.21ms[0m   p(90)=[36m1.4ms[0m    p(95)=[36m1.52ms[0m  
     http_req_blocked[2m...............:[0m avg=[36m4.93µs[0m   min=[36m1.88µs[0m   med=[36m3.19µs[0m   max=[36m244.57µs[0m p(90)=[36m5.82µs[0m   p(95)=[36m6.42µs[0m  
     http_req_connecting[2m............:[0m avg=[36m476ns[0m    min=[36m0s[0m       med=[36m0s[0m       max=[36m101.1µs[0m  p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 406[0m
     http_req_receiving[2m.............:[0m avg=[36m43.83µs[0m  min=[36m22.97µs[0m  med=[36m40.96µs[0m  max=[36m106.3µs[0m  p(90)=[36m64.7µs[0m   p(95)=[36m68.91µs[0m 
     http_req_sending[2m...............:[0m avg=[36m14.56µs[0m  min=[36m5.45µs[0m   med=[36m10.04µs[0m  max=[36m72.78µs[0m  p(90)=[36m26.26µs[0m  p(95)=[36m28.64µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     svc_analytics_success[2m..........:[0m [36m100.00%[0m [36;2m✓ 405[0m       [36;2m✗ 0[0m  
   [32m✓[0m svc_blockchain_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_charging_success[2m...........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_iotai_success[2m..............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_pvessc_success[2m.............:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
   [32m✓[0m svc_settlement_success[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m         [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m       [36;2mmax=1[0m
running (0m30.2s), 0/1 VUs, 135 complete and 0 interrupted iterations
--
     api_success_rate[2m...............:[0m [36m100.00%[0m [36;2m✓ 19[0m       [36;2m✗ 0[0m  
     auth_success_rate[2m..............:[0m [36m100.00%[0m [36;2m✓ 1[0m        [36;2m✗ 0[0m  
     charging_api_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 19[0m       [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 40[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m13 kB[0m   [36;2m427 B/s[0m
     data_sent[2m......................:[0m [36m4.4 kB[0m  [36;2m146 B/s[0m
     group_duration[2m.................:[0m avg=[36m1s[0m       min=[36m1s[0m       med=[36m1s[0m       max=[36m1s[0m       p(90)=[36m1s[0m       p(95)=[36m1s[0m      
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 20[0m 
     http_req_receiving[2m.............:[0m avg=[36m56.89µs[0m  min=[36m37.15µs[0m  med=[36m53.98µs[0m  max=[36m98.36µs[0m  p(90)=[36m73.14µs[0m  p(95)=[36m88.46µs[0m 
     http_req_sending[2m...............:[0m avg=[36m27.45µs[0m  min=[36m9.47µs[0m   med=[36m22.26µs[0m  max=[36m80.59µs[0m  p(90)=[36m39.16µs[0m  p(95)=[36m48.47µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m carbontrade_success[2m............:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 135[0m      [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m88 kB[0m   [36;2m2.9 kB/s[0m
     data_sent[2m......................:[0m [36m28 kB[0m   [36;2m918 B/s[0m
   [32m✓[0m demandresp_event_success[2m.......:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m deviceops_workorder_success[2m....:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m electrade_spot_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     group_duration[2m.................:[0m avg=[36m1.14ms[0m   min=[36m547.75µs[0m med=[36m1.12ms[0m   max=[36m2.44ms[0m   p(90)=[36m1.58ms[0m   p(95)=[36m1.83ms[0m   p(99)=[36m2.37ms[0m   count=[36m54[0m 
     http_req_blocked[2m...............:[0m avg=[36m7.42µs[0m   min=[36m1.44µs[0m   med=[36m3.61µs[0m   max=[36m291.74µs[0m p(90)=[36m6.58µs[0m   p(95)=[36m8.75µs[0m   p(99)=[36m104.65µs[0m count=[36m136[0m
     http_req_connecting[2m............:[0m avg=[36m1.35µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m100.71µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m53.96µs[0m  count=[36m136[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 136[0m
     http_req_receiving[2m.............:[0m avg=[36m45.84µs[0m  min=[36m15.37µs[0m  med=[36m43.16µs[0m  max=[36m175.1µs[0m  p(90)=[36m66.42µs[0m  p(95)=[36m71.54µs[0m  p(99)=[36m81.73µs[0m  count=[36m136[0m
     http_req_sending[2m...............:[0m avg=[36m15.99µs[0m  min=[36m4.8µs[0m    med=[36m13.89µs[0m  max=[36m117.03µs[0m p(90)=[36m23.08µs[0m  p(95)=[36m30.62µs[0m  p(99)=[36m59.59µs[0m  count=[36m136[0m
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m       p(99)=[36m0s[0m       count=[36m136[0m
--
   [32m✓[0m microgrid_protection_success[2m...:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
   [32m✓[0m overall_phase2_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 54[0m       [36;2m✗ 0[0m  
     phase2_api_latency[2m.............:[0m avg=[36m0.357564[0m min=[36m0.141349[0m med=[36m0.258648[0m max=[36m1.367046[0m p(90)=[36m0.503541[0m p(95)=[36m0.717641[0m p(99)=[36m1.130996[0m count=[36m135[0m
     phase2_total_requests[2m..........:[0m [36m54[0m      [36;2m1.786608/s[0m
   [32m✓[0m vpp_enhanced_success[2m...........:[0m [36m100.00%[0m [36;2m✓ 9[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.2s), 0/1 VUs, 54 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 60[0m       [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m15 kB[0m   [36;2m453 B/s[0m
     data_sent[2m......................:[0m [36m5.4 kB[0m  [36;2m170 B/s[0m
     group_duration[2m.................:[0m avg=[36m633.38µs[0m min=[36m419.62µs[0m med=[36m580.24µs[0m max=[36m1.29ms[0m   p(90)=[36m854.61µs[0m p(95)=[36m888.63µs[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 28[0m 
     http_req_receiving[2m.............:[0m avg=[36m50.13µs[0m  min=[36m28.91µs[0m  med=[36m51.31µs[0m  max=[36m79.75µs[0m  p(90)=[36m65.8µs[0m   p(95)=[36m70.69µs[0m 
     http_req_sending[2m...............:[0m avg=[36m23.12µs[0m  min=[36m7.74µs[0m   med=[36m21.53µs[0m  max=[36m51.67µs[0m  p(90)=[36m32.67µs[0m  p(95)=[36m33.78µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 4[0m        [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m32.0s), 0/1 VUs, 4 complete and 0 interrupted iterations
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 2[0m        [36;2m✗ 0[0m  
     data_received[2m..................:[0m [36m97 kB[0m   [36;2m3.2 kB/s[0m
     data_sent[2m......................:[0m [36m32 kB[0m   [36;2m1.1 kB/s[0m
     error_rate[2m.....................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 153[0m
     http_req_blocked[2m...............:[0m avg=[36m8.58µs[0m   min=[36m2.76µs[0m   med=[36m5.41µs[0m   max=[36m258.26µs[0m p(90)=[36m6.92µs[0m   p(95)=[36m9.34µs[0m  
     http_req_connecting[2m............:[0m avg=[36m1.41µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m121.18µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [32m✓[0m http_req_duration[2m..............:[0m avg=[36m489.37µs[0m min=[36m302.44µs[0m med=[36m484.87µs[0m max=[36m862.6µs[0m  p(90)=[36m602.52µs[0m p(95)=[36m702.72µs[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 154[0m
     http_req_receiving[2m.............:[0m avg=[36m55.94µs[0m  min=[36m26.99µs[0m  med=[36m53.15µs[0m  max=[36m282.7µs[0m  p(90)=[36m67.37µs[0m  p(95)=[36m78.12µs[0m 
     http_req_sending[2m...............:[0m avg=[36m25.02µs[0m  min=[36m14.11µs[0m  med=[36m23.62µs[0m  max=[36m72.52µs[0m  p(90)=[36m31.74µs[0m  p(95)=[36m41.33µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
     success_rate[2m...................:[0m [36m100.00%[0m [36;2m✓ 153[0m      [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
running (0m30.5s), 0/1 VUs, 32 complete and 0 interrupted iterations
--
    ✗ [S02] X-Content-Type-Options 存在
      ↳  0% — ✓ 0 / ✗ 60
    ✗ [S03] 未认证返回 401/403
      ↳  0% — ✓ 0 / ✗ 60
    ✓ [S04] Server 头不含 Kestrel

    CUSTOM
--
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 34[0m       [36;2m✗ 0[0m  
   [32m✓[0m dashboard_latency_ms[2m...........:[0m avg=[36m0.327409[0m min=[36m0.234381[0m med=[36m0.283428[0m max=[36m0.504042[0m p(90)=[36m0.435108[0m p(95)=[36m0.469575[0m
     data_received[2m..................:[0m [36m29 kB[0m   [36;2m955 B/s[0m
     data_sent[2m......................:[0m [36m9.9 kB[0m  [36;2m327 B/s[0m
--
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 50[0m 
     http_req_receiving[2m.............:[0m avg=[36m50.01µs[0m  min=[36m27.41µs[0m  med=[36m49.37µs[0m  max=[36m83.02µs[0m  p(90)=[36m65.82µs[0m  p(95)=[36m68.9µs[0m  
     http_req_sending[2m...............:[0m avg=[36m24.45µs[0m  min=[36m9.27µs[0m   med=[36m21.94µs[0m  max=[36m67.07µs[0m  p(90)=[36m40.58µs[0m  p(95)=[36m43.63µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
--
   [32m✓[0m operations_api_success[2m.........:[0m [36m100.00%[0m [36;2m✓ 11[0m       [36;2m✗ 0[0m  
     total_api_requests[2m.............:[0m [36m25[0m      [36;2m0.827979/s[0m
   [32m✓[0m trading_api_success[2m............:[0m [36m100.00%[0m [36;2m✓ 14[0m       [36;2m✗ 0[0m  
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0m
     vus_max[2m........................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=1[0mtime="2026-03-25T07:47:10Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/v320-operations-trading-results.json': open results/v320-operations-trading-results.json: no such file or directory"
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
