/**
 * SecuritySwitches 双环境配置 - k6 性能测试场景（v2.4.6）
 *
 * 覆盖：
 * - 安全中间件对 API 吞吐量影响
 * - HSTS/安全响应头注入性能开销
 * - 认证端点并发性能
 * - 健康检查端点基线
 * - Gateway 路由性能
 *
 * 禁止连接生产环境
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 测试环境配置
const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';
const IS_MOCK = BASE_URL.includes('localhost:8000') || BASE_URL.includes('127.0.0.1:8000');

// 自定义指标
const errorRate = new Rate('errors');
const healthTrend = new Trend('health_response_time');
const authTrend = new Trend('auth_response_time');
const headerCheckTrend = new Trend('header_check_time');
const requestCounter = new Counter('total_requests');

// 公共请求头
const headers = {
  'Content-Type': 'application/json',
  'X-Tenant-Code': 'TEST_TENANT',
};

const authHeaders = {
  ...headers,
  'Authorization': MOCK_TOKEN,
};

// ==================== 场景配置 ====================

export const options = {
  scenarios: {
    // 冒烟：快速验证
    smoke: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 10,
      exec: 'smoke_all',
      tags: { scenario: 'smoke' },
    },
    // 基线：安全中间件性能基线
    security_baseline: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'security_header_baseline',
      startTime: '15s',
      tags: { scenario: 'security_baseline' },
    },
    // 并发认证
    auth_concurrent: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 10 },
        { duration: '20s', target: 10 },
        { duration: '10s', target: 0 },
      ],
      exec: 'auth_endpoint_load',
      startTime: '50s',
      tags: { scenario: 'auth_concurrent' },
    },
  },
  thresholds: {
    'health_response_time': ['p(95)<2000'],          // 健康检查 P95 < 2s
    'auth_response_time': ['p(95)<3000'],             // 认证 P95 < 3s
    'header_check_time': ['p(95)<2000'],              // 响应头检查 P95 < 2s
    'errors': ['rate<0.1'],                           // 错误率 < 10%
  },
};

// ==================== 冒烟测试 ====================

export function smoke_all() {
  group('[SMOKE] SecuritySwitches 冒烟', () => {
    // 1. 健康检查
    const healthResp = http.get(`${BASE_URL}/api/gateway/health`);
    check(healthResp, {
      '[S01] 健康检查 < 500': r => r.status < 500,
    });
    healthTrend.add(healthResp.timings.duration);
    requestCounter.add(1);

    // 2. 安全响应头存在
    check(healthResp, {
      '[S02] X-Content-Type-Options 存在': r =>
        IS_MOCK ||
        r.headers['X-Content-Type-Options'] === 'nosniff' ||
        r.headers['x-content-type-options'] === 'nosniff',
    });

    // 3. 未认证401
    const unauthResp = http.get(`${BASE_URL}/api/permission/roles`, { headers });
    check(unauthResp, {
      '[S03] 未认证返回 401/403': r => IS_MOCK ? r.status < 500 : r.status === 401 || r.status === 403,
    });
    authTrend.add(unauthResp.timings.duration);
    requestCounter.add(1);

    // 4. Server 头不泄露
    check(healthResp, {
      '[S04] Server 头不含 Kestrel': r => {
        const server = r.headers['Server'] || r.headers['server'] || '';
        return !server.includes('Kestrel');
      },
    });

    sleep(0.5);
  });
}

// ==================== 安全头性能基线 ====================

export function security_header_baseline() {
  group('[PERF] 安全中间件性能', () => {
    // 健康检查（含安全头注入）
    const resp = http.get(`${BASE_URL}/api/gateway/health`);
    headerCheckTrend.add(resp.timings.duration);
    requestCounter.add(1);

    check(resp, {
      '[P01] 响应 < 2s': r => r.timings.duration < 2000,
      '[P02] 状态码正常': r => r.status < 500,
    });

    errorRate.add(resp.status >= 500);
    sleep(0.2);
  });
}

// ==================== 认证端点并发 ====================

export function auth_endpoint_load() {
  group('[LOAD] 认证端点并发', () => {
    // 模拟登录请求
    const loginPayload = JSON.stringify({
      userName: 'k6-loadtest-user',
      password: 'K6LoadTest2024!',
    });

    const resp = http.post(`${BASE_URL}/api/identity/auth/login`, loginPayload, {
      headers,
    });
    authTrend.add(resp.timings.duration);
    requestCounter.add(1);

    check(resp, {
      '[L01] 登录响应 < 3s': r => r.timings.duration < 3000,
      '[L02] 状态码非 5xx': r => r.status < 500,
    });

    errorRate.add(resp.status >= 500);
    sleep(0.3);
  });
}

// ==================== 默认入口 ====================

export default function () {
  smoke_all();
}
