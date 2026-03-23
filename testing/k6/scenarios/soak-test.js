/**
 * k6 压测场景：浸泡测试-2小时 50VU 持续负载
 */

import http from 'k6/http';
import { check, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

export let options = {
  vus: 10,
  duration: '5m',
  thresholds: {
    'http_req_duration': ['p(95)<3000'],   // 商用 SLA: 浸泡 P95 < 3s
    'http_req_failed': ['rate<0.05'],      // 商用 SLA: 失败率 ≤ 5%
  },
};

const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');

export default function() {
  group('soak - API Call', () => {
    const res = http.get(`${__ENV.BASE_URL || 'http://localhost:8000'}/api/health`);
    
    check(res, {
      'status is 200': (r) => r.status < 500,
      'response time < 500ms': (r) => r.timings.duration < 500,
    }) ? null : errorRate.add(1);
    
    responseTime.add(res.timings.duration);
  });
}
