/**
 * k6 压测场景：峰值测试-瞬间 10倍流量
 */

import http from 'k6/http';
import { check, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

export let options = {
  vus: 10,
  duration: '5m',
  thresholds: {
    'http_req_duration': ['p(95)<8000'],   // 商用 SLA: 峰值 P95 < 8s
    'http_req_failed': ['rate<0.15'],      // 商用 SLA: 失败率 ≤ 15%
  },
};

const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');

export default function() {
  group('spike - API Call', () => {
    const res = http.get(`${__ENV.BASE_URL || 'http://localhost:8000'}/api/health`);
    
    check(res, {
      'status is 200': (r) => r.status < 500,
      'response time < 500ms': (r) => r.timings.duration < 500,
    }) ? null : errorRate.add(1);
    
    responseTime.add(res.timings.duration);
  });
}
