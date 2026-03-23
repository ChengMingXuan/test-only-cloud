# ⚡ k6 性能测试错误报告

- **执行时间**: 2026-03-23 17:16:51 UTC
- **Git Commit**: 6b9d56d03ad2a776e764a452a8898629462f371d
- **场景**: smoke

## 测试结果

```

running (3m57.0s), 01/10 VUs, 460 complete and 0 interrupted iterations
default   [  99% ] 01/10 VUs  3m57.0s/4m00.0s
time="2026-03-23T17:16:48Z" level=warning msg="Request Failed" error="Post \"http://localhost:8000/api/auth/login\": dial tcp 127.0.0.1:8000: connect: connection refused"

running (3m58.0s), 01/10 VUs, 460 complete and 0 interrupted iterations
default   [  99% ] 01/10 VUs  3m58.0s/4m00.0s

running (3m59.0s), 01/10 VUs, 460 complete and 0 interrupted iterations
default   [ 100% ] 01/10 VUs  3m59.0s/4m00.0s

running (4m00.0s), 01/10 VUs, 460 complete and 0 interrupted iterations
default   [ 100% ] 01/10 VUs  4m00.0s/4m00.0s
time="2026-03-23T17:16:51Z" level=info msg="✅ Smoke Test Completed!" source=console
time="2026-03-23T17:16:51Z" level=info msg="Started at: 2026-03-23T17:12:51.498Z" source=console
time="2026-03-23T17:16:51Z" level=info msg="Ended at: 2026-03-23T17:16:51.651Z" source=console
     █ Health Check

[32m       ✓ health check status is 200[0m
[32m       ✓ health check response time < 200ms[0m

     █ User Authentication

[32m       ✓ login status is 200[0m
[32m       ✓ login response has token[0m
[32m       ✓ login successful[0m

     api_response_time[2m..........:[0m avg=[36m0[0m        min=[36m0[0m        med=[36m0[0m        max=[36m0[0m      p(90)=[36m0[0m        p(95)=[36m0[0m       
     checks[2m.....................:[0m [36m100.00%[0m [36;2m✓ 2305[0m   [36;2m✗ 0[0m   
     data_received[2m..............:[0m [36m0 B[0m     [36;2m0 B/s[0m
     data_sent[2m..................:[0m [36m0 B[0m     [36;2m0 B/s[0m
     group_duration[2m.............:[0m avg=[36m342.05µs[0m min=[36m178.08µs[0m med=[36m303.78µs[0m max=[36m1.84ms[0m p(90)=[36m480.18µs[0m p(95)=[36m510.78µs[0m
     http_req_blocked[2m...........:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m     p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_req_connecting[2m........:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m     p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [32m✓[0m http_req_duration[2m..........:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m     p(90)=[36m0s[0m       p(95)=[36m0s[0m      
   [31m✗[0m http_req_failed[2m............:[0m [36m100.00%[0m [36;2m✓ 922[0m    [36;2m✗ 0[0m   
     http_req_receiving[2m.........:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m     p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_req_sending[2m...........:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m     p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_req_tls_handshaking[2m...:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m     p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_req_waiting[2m...........:[0m avg=[36m0s[0m       min=[36m0s[0m       med=[36m0s[0m       max=[36m0s[0m     p(90)=[36m0s[0m       p(95)=[36m0s[0m      
     http_reqs[2m..................:[0m [36m922[0m     [36;2m3.8392/s[0m
     iteration_duration[2m.........:[0m avg=[36m4s[0m       min=[36m4s[0m       med=[36m4s[0m       max=[36m4s[0m     p(90)=[36m4s[0m       p(95)=[36m4s[0m      
     iterations[2m.................:[0m [36m461[0m     [36;2m1.9196/s[0m
     login_success_rate[2m.........:[0m [36m0.00%[0m   [36;2m✓ 0[0m      [36;2m✗ 461[0m 
     vus[2m........................:[0m [36m1[0m       [36;2mmin=1[0m    [36;2mmax=10[0m
     vus_max[2m....................:[0m [36m10[0m      [36;2mmin=10[0m   [36;2mmax=10[0mtime="2026-03-23T17:16:51Z" level=error msg="failed to handle the end-of-test summary" error="Could not save some summary information:\n\t- could not open 'results/smoke-results.json': open results/smoke-results.json: no such file or directory"

running (4m00.2s), 00/10 VUs, 461 complete and 0 interrupted iterations
default ✓ [ 100% ] 00/10 VUs  4m0s
time="2026-03-23T17:16:51Z" level=error msg="thresholds on metrics 'http_req_failed' have been crossed"
```
