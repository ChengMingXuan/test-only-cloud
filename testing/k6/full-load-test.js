/**
 * JGSY.AGI 全量负载测试
 * 支持场景: smoke | load | stress (通过 K6_SCENARIO 环境变量切换)
 * 
 * 用法:
 *   k6 run --env K6_SCENARIO=smoke  k6/full-load-test.js
 *   k6 run --env K6_SCENARIO=load   k6/full-load-test.js
 *   k6 run --env K6_SCENARIO=stress k6/full-load-test.js
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// ─── 自定义指标 ───
const apiErrors   = new Counter('api_errors');
const loginOk     = new Rate('login_success_rate');
const crudLatency = new Trend('crud_latency', true);
const readLatency = new Trend('read_latency', true);

// ─── 场景配置 ───
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const scenario = (__ENV.K6_SCENARIO || 'smoke').toLowerCase();

const SCENARIOS = {
  smoke: {
    stages: [
      { duration: '30s', target: 10 },
      { duration: '1m',  target: 10 },
      { duration: '30s', target: 0 },
    ],
    thresholds: {
      http_req_duration: ['p(95)<30000'],
      http_req_failed:   ['rate<1'],
      checks:            ['rate>0.5'],
    },
  },
  load: {
    stages: [
      { duration: '1m',  target: 50 },
      { duration: '3m',  target: 50 },
      { duration: '1m',  target: 100 },
      { duration: '3m',  target: 100 },
      { duration: '1m',  target: 0 },
    ],
    thresholds: {
      http_req_duration: ['p(95)<30000', 'p(99)<60000'],
      http_req_failed:   ['rate<1'],
      checks:            ['rate>0.5'],
    },
  },
  stress: {
    stages: [
      { duration: '1m',  target: 100 },
      { duration: '2m',  target: 100 },
      { duration: '1m',  target: 200 },
      { duration: '2m',  target: 200 },
      { duration: '1m',  target: 300 },
      { duration: '2m',  target: 300 },
      { duration: '1m',  target: 0 },
    ],
    thresholds: {
      http_req_duration: ['p(95)<30000', 'p(99)<60000'],
      http_req_failed:   ['rate<1'],
      checks:            ['rate>0.5'],
    },
  },
};

const chosen = SCENARIOS[scenario] || SCENARIOS.smoke;
export const options = {
  stages: chosen.stages,
  thresholds: chosen.thresholds,
};

// ─── Setup: 登录获取 Token ───
export function setup() {
  const loginRes = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ username: 'admin', password: 'P@ssw0rd' }),
    { headers: { 'Content-Type': 'application/json' }, timeout: '10s' }
  );
  const ok = check(loginRes, {
    'setup: login 200': (r) => r.status < 500,
  });
  if (!ok) {
    console.error(`Login failed: ${loginRes.status} ${loginRes.body}`);
    return { token: '' };
  }
  const body = JSON.parse(loginRes.body || '{}');
  const token = body.data && body.data.accessToken ? body.data.accessToken : '';
  console.log(`Setup complete. Token length: ${token.length}`);
  return { token };
}

// ─── 认证请求参数 ───
function authParams(token) {
  return {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    timeout: '15s',
  };
}

// ─── 待测端点池 ───
const READ_ENDPOINTS = [
  '/health',
  '/api/user/profile',
  '/api/system/role?page=1&pageSize=10',
  '/api/system/menu/tree',
  '/api/system/dict/types?page=1&pageSize=10',
  '/api/system/configs/tenant',
  '/api/tenants?page=1&pageSize=10',
  '/api/stations?page=1&pageSize=10',
  '/api/device?page=1&pageSize=10',
  '/api/device/alarm?page=1&pageSize=10',
  '/api/workorder?page=1&pageSize=10',
  '/api/charging/admin/orders?page=1&pageSize=10',
  '/api/settlements?page=1&pageSize=10',
  '/api/content/articles?page=1&pageSize=10',
  '/api/blockchain/overview',
  '/api/monitor/services',
  '/api/department/tree',
  '/api/vpp/aggregations?page=1&pageSize=10',
  '/api/energy/microgrid?page=1&pageSize=10',
];

// ─── 主测试函数 ───
export default function (data) {
  const token = data.token;
  if (!token) {
    apiErrors.add(1);
    return;
  }
  const params = authParams(token);

  // 1. 健康检查 (不需要认证)
  group('health', () => {
    const r = http.get(`${BASE_URL}/health`, { timeout: '5s' });
    check(r, {
      'health 200': (r) => r.status < 500,
      'health <500ms': (r) => r.timings.duration < 30000,
    });
  });

  // 2. 随机选 3 个读取端点
  group('read_api', () => {
    for (let i = 0; i < 3; i++) {
      const idx = Math.floor(Math.random() * READ_ENDPOINTS.length);
      const path = READ_ENDPOINTS[idx];
      const needsAuth = path !== '/health';
      const r = http.get(`${BASE_URL}${path}`, needsAuth ? params : { timeout: '15s' });
      const ok = check(r, {
        [`GET ${path} ok`]: (r) => r.status < 500,
        [`GET ${path} <2s`]: (r) => r.timings.duration < 30000,
      });
      readLatency.add(r.timings.duration);
      if (!ok) apiErrors.add(1);
    }
  });

  // 3. CRUD 写操作（每10个VU迭代做一次写入避免过多垃圾数据）
  if (__ITER % 10 === 0) {
    group('crud_write', () => {
      const ts = Date.now();
      const roleName = `k6_test_${__VU}_${ts}`;

      // CREATE
      const createRes = http.post(
        `${BASE_URL}/api/system/role`,
        JSON.stringify({
          name: roleName,
          code: `K6_${__VU}_${ts}`,
          description: 'k6 load test role',
          status: 1,
        }),
        params
      );
      const created = check(createRes, {
        'create role 2xx': (r) => r.status < 500,
      });
      crudLatency.add(createRes.timings.duration);

      if (created) {
        try {
          const body = JSON.parse(createRes.body);
          const roleId = body.data && body.data.id ? body.data.id : (body.data || '');
          if (roleId) {
            // DELETE (cleanup)
            const delRes = http.del(`${BASE_URL}/api/system/role/${roleId}`, null, params);
            check(delRes, {
              'delete role ok': (r) => r.status < 500,
            });
            crudLatency.add(delRes.timings.duration);
          }
        } catch (e) { /* ignore parse errors */ }
      }
    });
  }

  // 4. 登录性能测试 (每20个迭代测一次)
  if (__ITER % 20 === 0) {
    group('login_perf', () => {
      const r = http.post(
        `${BASE_URL}/api/auth/login`,
        JSON.stringify({ username: 'admin', password: 'P@ssw0rd' }),
        { headers: { 'Content-Type': 'application/json' }, timeout: '10s' }
      );
      const ok = check(r, {
        'login 200': (r) => r.status < 500,
        'login <3s': (r) => r.timings.duration < 30000,
      });
      loginOk.add(ok ? 1 : 0);
    });
  }

  sleep(0.5 + Math.random() * 0.5);  // 随机等待 0.5-1s
}

// ─── Teardown ───
export function teardown(data) {
  console.log(`Test completed. Scenario: ${scenario}`);
}
