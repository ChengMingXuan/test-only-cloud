# ⚡ k6 性能测试错误报告

- **执行时间**: 2026-03-23 19:32:09 UTC
- **Git Commit**: 07dd7c36283b798d148c935a0fcc5bd1e47debf3
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

     api_response_time[2m..............:[0m avg=[36m0.435524[0m min=[36m0.197677[0m med=[36m0.436126[0m max=[36m1.972341[0m p(90)=[36m0.56403[0m  p(95)=[36m0.650788[0m
     checks[2m.........................:[0m [36m100.00%[0m [36;2m✓ 3495[0m     [36;2m✗ 0[0m   
     data_received[2m..................:[0m [36m846 kB[0m  [36;2m3.5 kB/s[0m
     data_sent[2m......................:[0m [36m316 kB[0m  [36;2m1.3 kB/s[0m
     group_duration[2m.................:[0m avg=[36m608.09µs[0m min=[36m263.79µs[0m med=[36m604.19µs[0m max=[36m2.33ms[0m   p(90)=[36m796.49µs[0m p(95)=[36m861.03µs[0m
     http_req_blocked[2m...............:[0m avg=[36m7µs[0m      min=[36m1.97µs[0m   med=[36m5.08µs[0m   max=[36m428.42µs[0m p(90)=[36m6.53µs[0m   p(95)=[36m7.21µs[0m  
     http_req_connecting[2m............:[0m avg=[36m1.14µs[0m   min=[36m0s[0m       med=[36m0s[0m       max=[36m212.51µs[0m p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [32m✓[0m http_req_duration[2m..............:[0m avg=[36m434.12µs[0m min=[36m197.67µs[0m med=[36m432.01µs[0m max=[36m1.97ms[0m   p(90)=[36m563.91µs[0m p(95)=[36m668.93µs[0m
       { expected_response:true }[2m...:[0m avg=[36m434.12µs[0m min=[36m197.67µs[0m med=[36m432.01µs[0m max=[36m1.97ms[0m   p(90)=[36m563.91µs[0m p(95)=[36m668.93µs[0m
   [32m✓[0m http_req_failed[2m................:[0m [36m0.00%[0m   [36;2m✓ 0[0m        [36;2m✗ 1631[0m
     http_req_receiving[2m.............:[0m avg=[36m53.18µs[0m  min=[36m19.28µs[0m  med=[36m53.04µs[0m  max=[36m113.61µs[0m p(90)=[36m72.43µs[0m  p(95)=[36m77.78µs[0m 
     http_req_sending[2m...............:[0m avg=[36m25.4µs[0m   min=[36m6.71µs[0m   med=[36m23.31µs[0m  max=[36m1.48ms[0m   p(90)=[36m35.33µs[0m  p(95)=[36m40.28µs[0m 
     http_req_tls_handshaking[2m.......:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m       p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_req_waiting[2m...............:[0m avg=[36m355.52µs[0m min=[36m153.69µs[0m med=[36m349.95µs[0m max=[36m1.78ms[0m   p(90)=[36m466.41µs[0m p(95)=[36m565.93µs[0m
     http_reqs[2m......................:[0m [36m1631[0m    [36;2m6.78861/s[0m
     iteration_duration[2m.............:[0m avg=[36m8s[0m       min=[36m8s[0m       med=[36m8s[0m       max=[36m8.01s[0m    p(90)=[36m8.01s[0m    p(95)=[36m8.01s[0m   
     iterations[2m.....................:[0m [36m233[0m     [36;2m0.969801/s[0m
     login_success_rate[2m.............:[0m [36m100.00%[0m [36;2m✓ 233[0m      [36;2m✗ 0[0m   
     vus[2m............................:[0m [36m1[0m       [36;2mmin=1[0m      [36;2mmax=10[0m
     vus_max[2m........................:[0m [36m10[0m      [36;2mmin=10[0m     [36;2mmax=10[0mtime="2026-03-23T19:32:08Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/smoke-results.json': open results/smoke-results.json: no such file or directory"

running (4m00.3s), 00/10 VUs, 233 complete and 0 interrupted iterations
default ✓ [ 100% ] 00/10 VUs  4m0s
```
