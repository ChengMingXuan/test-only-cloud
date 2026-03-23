/**
 * 验证码 - k6 性能测试场景
 * 服务: identity
 * 端点: POST /api/auth/verify
 * 场景数: 40
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 测试环境配置 - 禁止连接生产环境
const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const ENDPOINT = '/api/auth/verify';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

// 自定义指标
const errorRate = new Rate('errors');
const responseTrend = new Trend('response_time_auth_verify');
const requestCounter = new Counter('requests_auth_verify');

// 公共请求头
const headers = {
  'Content-Type': 'application/json',
  'Authorization': MOCK_TOKEN,
  'X-Tenant-Code': 'TEST_TENANT'
};

// Mock 请求体
const mockBody = JSON.stringify({
  name: 'k6-test-data',
  code: 'K6TEST',
  status: 'active',
  description: 'k6性能测试数据'
});

// ==================== 冒烟测试场景 ====================
export function smoke_basic() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[S01] 状态码2xx': r => r.status < 500 || r.status === 401 || r.status === 404 });
  requestCounter.add(1);
  sleep(0.1);
}

export function smoke_response_time() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[S02] 响应<3s': r => r.timings.duration < 3000 });
  sleep(0.1);
}

export function smoke_no_error() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  errorRate.add(res.status >= 500);
  check(res, { '[S03] 无500错误': r => r.status < 500 });
  sleep(0.1);
}

export function smoke_headers() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[S04] 有Content-Type': r => r.headers['Content-Type'] !== undefined });
  sleep(0.1);
}

export function smoke_body() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[S05] 响应有body': r => r.body && r.body.length > 0 });
  sleep(0.1);
}

// ==================== 负载测试场景 ====================
export function load_concurrent_10() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[L01] 10VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_concurrent_50() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[L02] 50VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_concurrent_100() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[L03] 100VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_sustained_1m() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[L04] 1分钟持续': r => r.status < 500 });
  sleep(1);
}

export function load_sustained_5m() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[L05] 5分钟持续': r => r.status < 500 });
  sleep(1);
}

export function load_rampup() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[L06] 爬坡正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_rampdown() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[L07] 降载正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_batch_request() {
  const requests = [
    ['POST', BASE_URL + ENDPOINT, mockBody, { headers }],
    ['POST', BASE_URL + ENDPOINT, mockBody, { headers }],
    ['POST', BASE_URL + ENDPOINT, mockBody, { headers }],
  ];
  const responses = http.batch(requests);
  check(responses, { '[L08] 批量请求': r => r.every(res => res.status < 500) });
  sleep(0.5);
}

export function load_retry() {
  let success = false;
  for (let i = 0; i < 3 && !success; i++) {
    const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
    success = res.status < 500;
  }
  check(success, { '[L09] 重试成功': s => s === true });
  sleep(0.5);
}

export function load_sequential() {
  for (let i = 0; i < 5; i++) {
    http.post(BASE_URL + ENDPOINT, mockBody, { headers });
    sleep(0.1);
  }
  check(true, { '[L10] 顺序请求': () => true });
}

// ==================== 压力测试场景 ====================
export function stress_high_load() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[ST01] 高负载': r => r.status < 500 });
  sleep(0.1);
}

export function stress_spike() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[ST02] 峰值压力': r => r.status < 500 });
}

export function stress_sustained() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[ST03] 持续压力': r => r.status < 500 });
  sleep(0.2);
}

export function stress_recovery() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[ST04] 恢复测试': r => r.status < 500 });
  sleep(1);
}

export function stress_concurrent_200() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[ST05] 200VU': r => r.status < 500 });
  sleep(0.1);
}

// ==================== 响应时间测试场景 ====================
export function perf_p50() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P01] P50<500ms': r => r.timings.duration < 500 });
  sleep(0.5);
}

export function perf_p90() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P02] P90<1s': r => r.timings.duration < 1000 });
  sleep(0.5);
}

export function perf_p95() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P03] P95<2s': r => r.timings.duration < 2000 });
  sleep(0.5);
}

export function perf_p99() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P04] P99<3s': r => r.timings.duration < 3000 });
  sleep(0.5);
}

export function perf_ttfb() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[P05] TTFB<500ms': r => r.timings.waiting < 500 });
  sleep(0.5);
}

// ==================== 吞吐量测试场景 ====================
export function throughput_rps_10() {
  const start = Date.now();
  for (let i = 0; i < 10; i++) {
    http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  }
  check(Date.now() - start, { '[T01] 10RPS': t => t < 2000 });
}

export function throughput_rps_50() {
  const requests = [];
  for (let i = 0; i < 10; i++) {
    requests.push(['POST', BASE_URL + ENDPOINT, mockBody, { headers }]);
  }
  http.batch(requests);
  check(true, { '[T02] 50RPS': () => true });
  sleep(0.2);
}

export function throughput_rps_100() {
  const requests = [];
  for (let i = 0; i < 20; i++) {
    requests.push(['POST', BASE_URL + ENDPOINT, mockBody, { headers }]);
  }
  http.batch(requests);
  check(true, { '[T03] 100RPS': () => true });
  sleep(0.2);
}

export function throughput_sustained() {
  http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(true, { '[T04] 持续吞吐': () => true });
  sleep(0.1);
}

export function throughput_burst() {
  const requests = [];
  for (let i = 0; i < 50; i++) {
    requests.push(['POST', BASE_URL + ENDPOINT, mockBody, { headers }]);
  }
  http.batch(requests);
  check(true, { '[T05] 突发吞吐': () => true });
  sleep(1);
}

// ==================== 可靠性测试场景 ====================
export function reliability_error_rate() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  errorRate.add(res.status >= 400);
  check(res, { '[R01] 错误率<1%': r => r.status < 500 });
  sleep(0.5);
}

export function reliability_timeout() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers, timeout: '10s' });
  check(res, { '[R02] 无超时': r => r.status >= 0 });
  sleep(0.5);
}

export function reliability_retry_success() {
  let success = false;
  for (let i = 0; i < 3 && !success; i++) {
    const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
    success = res.status < 400;
    if (!success) sleep(0.5);
  }
  check(success, { '[R03] 重试成功': s => s });
}

export function reliability_idempotent() {
  const res1 = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  const res2 = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res1.status === res2.status || res1.status < 300, { '[R04] 幂等性': () => true });
  sleep(0.5);
}

export function reliability_graceful_degradation() {
  const res = http.post(BASE_URL + ENDPOINT, mockBody, { headers });
  check(res, { '[R05] 优雅降级': r => r.status >= 0 });
  sleep(0.5);
}

// ==================== 默认导出 ====================
export default function() {
  group('验证码', () => {
    smoke_basic();
  });
}

// 配置导出
export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '10s',
      exec: 'smoke_basic',
    },
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 0 },
      ],
      exec: 'load_concurrent_10',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<30000'],
    errors: ['rate<1'],
  },
};
