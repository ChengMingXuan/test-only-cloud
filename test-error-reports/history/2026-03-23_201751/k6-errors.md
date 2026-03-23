# ⚡ k6 性能测试错误报告

- **执行时间**: 2026-03-23 20:17:51 UTC
- **Git Commit**: 345f5d337c58c67b14b138437f92a8c6f8929a2a
- **场景**: smoke

## 测试结果

```
[32m       ✓ login successful[0m

     █ Get User Profile

[32m       ✓ get profile status is 200[0m
[32m       ✓ profile has user data[0m

     █ Get Stations List

[32m       ✓ get stations status is 200[0m
[32m       ✓ stations response has data[0m

     █ Get Devices List

[32m       ✓ get devices status is 200[0m
[32m       ✓ devices response has data[0m

     █ Get Charging Records

[32m       ✓ get records status is 200[0m
[32m       ✓ records response has data[0m

     █ User Logout

[32m       ✓ logout status is 200[0m
[32m       ✓ logout successful[0m

     api_response_time[2m..............:[0m avg=[36m0.359273[0m min=[36m0.201045[0m med=[36m0.315961[0m max=[36m1.937206[0m p(90)=[36m0.537004[0m p(95)=[36m0.578798[0m
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 3495[0m     [36;2m✗ 0[0m   
     data_received[2m..................:[0m [36m846 kB[0m  [36;2m3.5 kB/s[0m
     data_sent[2m......................:[0m [36m316 kB[0m  [36;2m1.3 kB/s[0m
     group_duration[2m.................:[0m avg=[36m514.04µs[0m min=[36m277.33µs[0m med=[36m459.56µs[0m max=[36m2.41ms[0m   p(90)=[36m750.72µs[0m p(95)=[36m808.91µs[0m
     http_req_blocked[2m...............:[0m avg=[36m7.28µs[0m   min=[36m1.88µs[0m   med=[36m3.74µs[0m   max=[36m1.45ms[0m   p(90)=[36m5.83µs[0m   p(95)=[36m6.55µs[0m  
     http_req_connecting[2m............:[0m avg=[36m2.5µs[0m    min=[36m0s[0m       med=[36m0s[0m       max=[36m1.38ms[0m   p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [32m✓[0m http_req_duration[2m..............:[0m avg=[36m359.41µs[0m min=[36m201.04µs[0m med=[36m315.99µs[0m max=[36m2.25ms[0m   p(90)=[36m535.31µs[0m p(95)=[36m576.48µs[0m
       { expected_response:true }[2m...:[0m avg=[36m359.41µs[0m min=[36m201.04µs[0m med=[36m315.99µs[0m max=[36m2.25ms[0m   p(90)=[36m535.31µs[0m p(95)=[36m576.48µs[0m
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 1631[0m
     http_req_receiving[2m.............:[0m avg=[36m48.24µs[0m  min=[36m23.47µs[0m  med=[36m47.19µs[0m  max=[36m309.73µs[0m p(90)=[36m64.39µs[0m  p(95)=[36m71.23µs[0m 
     http_req_sending[2m...............:[0m avg=[36m21.37µs[0m  min=[36m6.82µs[0m   med=[36m19.92µs[0m  max=[36m124.77µs[0m p(90)=[36m30.9µs[0m   p(95)=[36m37.69µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_req_waiting[2m...............:[0m avg=[36m289.79µs[0m min=[36m151.81µs[0m med=[36m250.74µs[0m max=[36m2.1ms[0m    p(90)=[36m444.78µs[0m p(95)=[36m481.41µs[0m
     http_reqs[2m......................:[0m [36m1631[0m    [36;2m6.788843/s[0m
     iteration_duration[2m.............:[0m avg=[36m8s[0m       min=[36m8s[0m       med=[36m8s[0m       max=[36m8.01s[0m    p(90)=[36m8s[0m       p(95)=[36m8.01s[0m   
     iterations[2m.....................:[0m [36m233[0m     [36;2m0.969835/s[0m
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 233[0m      [36;2m✗ 0[0m   
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=10[0m
     vus_max[2m........................:[0m [36m10[0m      [36;2mmin=10[0m     [36;2mmax=10[0mtime="2026-03-23T20:17:51Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/smoke-results.json': open results/smoke-results.json: no such file or directory"

running (4m00.2s), 00/10 VUs, 233 complete and 0 interrupted iterations
default ✓ [ 100% ] 00/10 VUs  4m0s
```
