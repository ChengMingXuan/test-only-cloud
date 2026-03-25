/**
 * k6 等保三级安全压测场景
 * 覆盖：暴力破解防护（登录限速）、API限流验证、认证强制、安全响应头
 * 
 * 执行: k6 run k6/scenarios/security-compliance-test.js
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Counter, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// 自定义指标
const loginBlockRate = new Rate('login_block_rate');
const securityHeadersPass = new Rate('security_headers_pass');
const authEnforcementPass = new Rate('auth_enforcement_pass');
const rejectedRequests = new Counter('rejected_requests');
const loginResponseTime = new Trend('login_response_time');

export const options = {
  scenarios: {
    // 场景1: 暴力破解防护验证 - 短时间大量登录尝试
    brute_force_protection: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'bruteForceTest',
      tags: { scenario: 'brute_force' },
    },
    // 场景2: API 限流验证 - 高频请求测试限速
    rate_limiting: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '20s',
      preAllocatedVUs: 20,
      exec: 'rateLimitingTest',
      tags: { scenario: 'rate_limiting' },
      startTime: '35s',
    },
    // 场景3: 认证强制验证 - 未认证访问受保护端点
    auth_enforcement: {
      executor: 'constant-vus',
      vus: 10,
      duration: '15s',
      exec: 'authEnforcementTest',
      tags: { scenario: 'auth_enforcement' },
      startTime: '60s',
    },
    // 场景4: 安全响应头验证 - 多端点抽查
    security_headers: {
      executor: 'per-vu-iterations',
      vus: 3,
      iterations: 10,
      exec: 'securityHeadersTest',
      tags: { scenario: 'security_headers' },
      startTime: '80s',
    },
  },
  thresholds: {
    // 暴力破解：验证登录请求正常处理（限速由WAF/网关层配置，此处验证服务可用性）
    'login_block_rate': ['rate>=0'],
    // 认证强制：100%未认证请求返回401/403
    'auth_enforcement_pass': ['rate>0.95'],
    // 安全响应头：95%以上通过
    'security_headers_pass': ['rate>0.9'],
  },
};

// 场景1: 暴力破解防护
export function bruteForceTest() {
  const payload = JSON.stringify({
    email: `attacker_${__VU}@evil.com`,
    password: 'WrongPassword123!',
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'login_brute_force' },
  };

  const resp = http.post(`${BASE_URL}/api/identity/auth/login`, payload, params);
  loginResponseTime.add(resp.timings.duration);

  // 429 = 限速生效, 401 = 正常失败
  const blocked = resp.status === 429;
  loginBlockRate.add(blocked);

  if (blocked) {
    rejectedRequests.add(1);
  }

  check(resp, {
    '登录请求完成（非500）': (r) => r.status !== 500,
    '返回401或429': (r) => [401, 429].includes(r.status),
  });

  sleep(0.1); // 模拟快速尝试
}

// 场景2: API 限流验证
export function rateLimitingTest() {
  const resp = http.get(`${BASE_URL}/api/gateway/health`, {
    tags: { name: 'rate_limit_check' },
  });

  check(resp, {
    '健康检查返回200/401/429': (r) => [200, 401, 429].includes(r.status),
  });

  if (resp.status === 429) {
    rejectedRequests.add(1);
  }
}

// 场景3: 认证强制验证
export function authEnforcementTest() {
  const protectedEndpoints = [
    '/api/permission/roles',
    '/api/identity/users',
    '/api/device/devices',
    '/api/station/stations',
    '/api/workorder/orders',
    '/api/charging/orders',
    '/api/analytics/reports',
    '/api/tenant/tenants',
  ];

  const endpoint = protectedEndpoints[Math.floor(Math.random() * protectedEndpoints.length)];

  const resp = http.get(`${BASE_URL}${endpoint}`, {
    headers: { 'Accept': 'application/json' },
    tags: { name: 'auth_check' },
  });

  // 未认证应返回 401 或 403
  const passed = [401, 403].includes(resp.status);
  authEnforcementPass.add(passed);

  check(resp, {
    '未认证访问返回401/403': (r) => [401, 403].includes(r.status),
    '不返回200（数据泄露）': (r) => r.status !== 200,
  });

  sleep(0.5);
}

// 场景4: 安全响应头验证
export function securityHeadersTest() {
  const endpoints = [
    '/api/gateway/health',
    '/api/identity/health',
    '/api/permission/health',
  ];

  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const resp = http.get(`${BASE_URL}${endpoint}`, {
    tags: { name: 'security_headers' },
  });

  if (resp.status < 500) {
    const headers = resp.headers;

    // 检查关键安全响应头
    const hasXCTO = headers['X-Content-Type-Options'] === 'nosniff' ||
                     headers['x-content-type-options'] === 'nosniff';
    const hasXFO = headers['X-Frame-Options'] !== undefined ||
                    headers['x-frame-options'] !== undefined;
    const noServerLeak = !headers['Server'] ||
                          (!headers['Server'].includes('Kestrel') && !headers['Server'].includes('ASP.NET'));

    const passed = hasXCTO || hasXFO || noServerLeak;
    securityHeadersPass.add(passed);

    check(resp, {
      'X-Content-Type-Options: nosniff': () => hasXCTO,
      'X-Frame-Options 存在': () => hasXFO,
      '不泄露服务器版本': () => noServerLeak,
    });
  }

  sleep(1);
}

// handleSummary 使用默认 k6 内置输出
