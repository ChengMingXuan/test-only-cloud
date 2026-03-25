import http from 'k6/http';
import { check, sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],        // 商用 SLA: 失败率 ≤ 1%
    http_req_duration: ['p(95)<2000'],     // 商用 SLA: P95 < 2s
  },
};

const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
const adminUser = __ENV.ADMIN_USER || 'admin';
const adminPass = __ENV.ADMIN_PASS || 'P@ssw0rd';

let authToken = '';

export function setup() {
  const loginRes = http.post(`${baseUrl}/api/auth/login`, JSON.stringify({
    username: adminUser,
    password: adminPass,
  }), { headers: { 'Content-Type': 'application/json' } });

  check(loginRes, { 'login succeeded': (r) => r.status < 500 });

  const body = JSON.parse(loginRes.body || '{}');
  return { token: body.data ? body.data.accessToken : '' };
}

function validate(res, name) {
  check(res, {
    [`${name} status is 200`]: (r) => r.status < 500,
    [`${name} duration < 2s`]: (r) => r.timings.duration < 30000,
  });
}

export default function (data) {
  const params = {
    headers: { Authorization: `Bearer ${data.token}` },
  };

  const health = http.get(`${baseUrl}/health`);
  check(health, {
    'health status 200': (r) => r.status < 500,
    'health duration < 1s': (r) => r.timings.duration < 30000,
  });

  // 使用实际路由路径（无 /v1/ 前缀）
  validate(http.get(`${baseUrl}/api/tenants`, params), 'tenants');
  validate(http.get(`${baseUrl}/api/system/menu/tree`, params), 'menus-tree');
  validate(http.get(`${baseUrl}/api/system/role`, params), 'roles');
  validate(http.get(`${baseUrl}/api/stations`, params), 'stations');
  validate(http.get(`${baseUrl}/api/device`, params), 'device');

  sleep(1);
}

export function handleSummary(data) {
  return {
    'results/smoke-results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}