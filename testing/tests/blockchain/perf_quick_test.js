import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },   // 预热
    { duration: '30s', target: 5 },   // 主阶段
    { duration: '10s', target: 0 },   // 冷却
  ],
  thresholds: {
    'http_req_duration': ['p(95)<1000'],
    'http_req_failed': ['rate<0.1'],
  },
};

export default function() {
  group('故障转移状态查询', () => {
    const res = http.get('http://localhost:8021/api/blockchain/failover/status');
    check(res, {
      '状态码 200': (r) => r.status === 200,
      '响应时间': (r) => r.timings.duration < 1000,
    });
  });
  
  sleep(1);
}
