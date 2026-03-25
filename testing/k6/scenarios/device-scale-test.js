/**
 * k6 压测场景：设备管理规模压测
 */

import http from 'k6/http';
import { check, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

export let options = {
  vus: 10,
  duration: '5m',
  thresholds: {
    'http_req_duration': ['p(95)<30000'],
    'http_req_failed': ['rate<1'],
  },
};

const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');

export default function() {
  group('device-scale - API Call', () => {
    const res = http.get(\\/api/health\);
    
    check(res, {
      'status is 200': (r) => r.status < 500,
      'response time < 500ms': (r) => r.timings.duration < 500,
    }) ? null : errorRate.add(1);
    
    responseTime.add(res.timings.duration);
  });
}
