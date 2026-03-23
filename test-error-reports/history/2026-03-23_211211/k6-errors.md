# ⚡ k6 性能测试错误报告

- **执行时间**: 2026-03-23 21:12:11 UTC
- **Git Commit**: 982d1937eec60eb18fdd932357bc0407f837e120
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

     api_response_time[2m..............:[0m avg=[36m0.407334[0m min=[36m0.200583[0m med=[36m0.374945[0m max=[36m1.855615[0m p(90)=[36m0.554308[0m p(95)=[36m0.618035[0m
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 3495[0m     [36;2m✗ 0[0m   
     data_received[2m..................:[0m [36m846 kB[0m  [36;2m3.5 kB/s[0m
     data_sent[2m......................:[0m [36m316 kB[0m  [36;2m1.3 kB/s[0m
     group_duration[2m.................:[0m avg=[36m564.11µs[0m min=[36m260µs[0m    med=[36m529.28µs[0m max=[36m2.23ms[0m   p(90)=[36m772.16µs[0m p(95)=[36m831.01µs[0m
     http_req_blocked[2m...............:[0m avg=[36m6.34µs[0m   min=[36m2.33µs[0m   med=[36m4.49µs[0m   max=[36m318.18µs[0m p(90)=[36m6.27µs[0m   p(95)=[36m7.18µs[0m  
     http_req_connecting[2m............:[0m avg=[36m1.13µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m240.14µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [32m✓[0m http_req_duration[2m..............:[0m avg=[36m402.52µs[0m min=[36m200.58µs[0m med=[36m363.32µs[0m max=[36m1.85ms[0m   p(90)=[36m553.01µs[0m p(95)=[36m621.61µs[0m
       { expected_response:true }[2m...:[0m avg=[36m402.52µs[0m min=[36m200.58µs[0m med=[36m363.32µs[0m max=[36m1.85ms[0m   p(90)=[36m553.01µs[0m p(95)=[36m621.61µs[0m
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 1631[0m
     http_req_receiving[2m.............:[0m avg=[36m50.57µs[0m  min=[36m23.72µs[0m  med=[36m49.15µs[0m  max=[36m333.89µs[0m p(90)=[36m68.94µs[0m  p(95)=[36m74.77µs[0m 
     http_req_sending[2m...............:[0m avg=[36m23.11µs[0m  min=[36m6.74µs[0m   med=[36m22.18µs[0m  max=[36m98.41µs[0m  p(90)=[36m33.58µs[0m  p(95)=[36m38.43µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_req_waiting[2m...............:[0m avg=[36m328.84µs[0m min=[36m159.57µs[0m med=[36m287.34µs[0m max=[36m1.75ms[0m   p(90)=[36m464.73µs[0m p(95)=[36m523.56µs[0m
     http_reqs[2m......................:[0m [36m1631[0m    [36;2m6.789187/s[0m
     iteration_duration[2m.............:[0m avg=[36m8s[0m       min=[36m8s[0m       med=[36m8s[0m       max=[36m8.01s[0m    p(90)=[36m8s[0m       p(95)=[36m8.01s[0m   
     iterations[2m.....................:[0m [36m233[0m     [36;2m0.969884/s[0m
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 233[0m      [36;2m✗ 0[0m   
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=10[0m
     vus_max[2m........................:[0m [36m10[0m      [36;2mmin=10[0m     [36;2mmax=10[0mtime="2026-03-23T21:12:11Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/smoke-results.json': open results/smoke-results.json: no such file or directory"

running (4m00.2s), 00/10 VUs, 233 complete and 0 interrupted iterations
default ✓ [ 100% ] 00/10 VUs  4m0s
```
