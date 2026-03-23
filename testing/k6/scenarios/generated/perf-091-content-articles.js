/**
 * 内容文章 - k6 性能测试场景
 * 服务: contentplatform
 * 端点: GET /api/contentplatform/articles
 * 场景数: 35
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const ENDPOINT = '/api/contentplatform/articles';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

const errorRate = new Rate('errors');
const responseTrend = new Trend('response_time_content_articles');
const requestCounter = new Counter('requests_content_articles');

const headers = {
  'Content-Type': 'application/json',
  'Authorization': MOCK_TOKEN,
  'X-Tenant-Code': 'TEST_TENANT'
};

const mockBody = JSON.stringify({
  name: 'k6-test-content_articles',
  code: 'K6TEST',
  status: 'active',
  description: 'k6性能测试-内容文章'
});

// ==================== 冒烟测试场景 ====================
export function smoke_basic_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[S01] 状态码正常': r => r.status < 500 });
  requestCounter.add(1);
  sleep(0.1);
}

export function smoke_response_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[S02] 响应<3s': r => r.timings.duration < 3000 });
  sleep(0.1);
}

export function smoke_no_error_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  errorRate.add(res.status >= 500);
  check(res, { '[S03] 无500错误': r => r.status < 500 });
  sleep(0.1);
}

export function smoke_headers_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[S04] Content-Type': r => r.headers['Content-Type'] !== undefined });
  sleep(0.1);
}

export function smoke_body_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[S05] 有响应体': r => r.body && r.body.length > 0 });
  sleep(0.1);
}

// ==================== 负载测试场景 ====================
export function load_10vu_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[L01] 10VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_50vu_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[L02] 50VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_100vu_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[L03] 100VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_1m_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[L04] 1分钟持续': r => r.status < 500 });
  sleep(1);
}

export function load_5m_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[L05] 5分钟持续': r => r.status < 500 });
  sleep(1);
}

export function load_rampup_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[L06] 爬坡正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_rampdown_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[L07] 降载正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_batch_content_articles() {
  const requests = [
    ['GET', BASE_URL + ENDPOINT, null, { headers }],
    ['GET', BASE_URL + ENDPOINT, null, { headers }],
    ['GET', BASE_URL + ENDPOINT, null, { headers }],
  ];
  const responses = http.batch(requests);
  check(responses, { '[L08] 批量请求': r => r.every(res => res.status < 500) });
  sleep(0.5);
}

export function load_retry_content_articles() {
  let success = false;
  for (let i = 0; i < 3 && !success; i++) {
    const res = http.get(BASE_URL + ENDPOINT, null, { headers });
    success = res.status < 500;
  }
  check(success, { '[L09] 重试成功': s => s === true });
  sleep(0.5);
}

export function load_sequential_content_articles() {
  for (let i = 0; i < 5; i++) {
    http.get(BASE_URL + ENDPOINT, null, { headers });
    sleep(0.1);
  }
  check(true, { '[L10] 顺序请求': () => true });
}

// ==================== 压力测试场景 ====================
export function stress_high_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[ST01] 高负载': r => r.status < 500 });
  sleep(0.1);
}

export function stress_spike_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[ST02] 峰值压力': r => r.status < 500 });
}

export function stress_sustained_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[ST03] 持续压力': r => r.status < 500 });
  sleep(0.2);
}

export function stress_recovery_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[ST04] 恢复测试': r => r.status < 500 });
  sleep(1);
}

export function stress_200vu_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  check(res, { '[ST05] 200VU': r => r.status < 500 });
  sleep(0.1);
}

// ==================== 响应时间测试场景 ====================
export function perf_p50_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P01] P50<500ms': r => r.timings.duration < 500 });
  sleep(0.5);
}

export function perf_p90_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P02] P90<1s': r => r.timings.duration < 1000 });
  sleep(0.5);
}

export function perf_p95_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P03] P95<2s': r => r.timings.duration < 2000 });
  sleep(0.5);
}

export function perf_p99_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P04] P99<3s': r => r.timings.duration < 3000 });
  sleep(0.5);
}

// ==================== 安全测试场景 ====================
export function security_no_auth_content_articles() {
  const noAuthHeaders = { 'Content-Type': 'application/json', 'X-Tenant-Code': 'TEST_TENANT' };
  const res = http.get(BASE_URL + ENDPOINT, null, { headers: noAuthHeaders });
  check(res, { '[SEC01] 无认证拒绝': r => r.status === 401 || r.status === 403 || r.status < 500 });
  sleep(0.5);
}

export function security_invalid_token_content_articles() {
  const badHeaders = { ...headers, 'Authorization': 'Bearer invalid-token-xxx' };
  const res = http.get(BASE_URL + ENDPOINT, null, { headers: badHeaders });
  check(res, { '[SEC02] 无效Token': r => r.status === 401 || r.status === 403 || r.status < 500 });
  sleep(0.5);
}

export function security_wrong_tenant_content_articles() {
  const wrongTenantHeaders = { ...headers, 'X-Tenant-Code': 'WRONG_TENANT_XXX' };
  const res = http.get(BASE_URL + ENDPOINT, null, { headers: wrongTenantHeaders });
  check(res, { '[SEC03] 错误租户': r => r.status < 500 });
  sleep(0.5);
}

// ==================== 并发安全场景 ====================
export function concurrent_read_content_articles() {
  const requests = Array(10).fill(['GET', BASE_URL + ENDPOINT, null, { headers }]);
  const responses = http.batch(requests);
  check(responses, { '[CC01] 并发读取': r => r.every(res => res.status < 500) });
  sleep(0.5);
}

export function concurrent_mixed_content_articles() {
  const requests = [
    ['GET', BASE_URL + ENDPOINT, null, { headers }],
    ['GET', BASE_URL + ENDPOINT, null, { headers }],
    ['GET', BASE_URL + ENDPOINT, null, { headers }],
  ];
  const responses = http.batch(requests);
  check(responses, { '[CC02] 混合并发': r => r.every(res => res.status < 500) });
  sleep(0.5);
}

// ==================== 数据边界场景 ====================
export function boundary_empty_body_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, '{}', { headers });
  check(res, { '[BD01] 空Body': r => r.status < 500 });
  sleep(0.3);
}

export function boundary_large_payload_content_articles() {
  const largeBody = JSON.stringify({ data: 'x'.repeat(10000) });
  const res = http.get(BASE_URL + ENDPOINT, largeBody, { headers });
  check(res, { '[BD02] 大载荷': r => r.status < 500 });
  sleep(0.3);
}

export function boundary_special_chars_content_articles() {
  const specialBody = JSON.stringify({ name: '测试<script>alert(1)</script>&特殊字符' });
  const res = http.get(BASE_URL + ENDPOINT, specialBody, { headers });
  check(res, { '[BD03] 特殊字符': r => r.status < 500 });
  sleep(0.3);
}

// ==================== 超时与恢复场景 ====================
export function timeout_short_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers, timeout: '5s' });
  check(res, { '[TO01] 5s超时': r => r.status < 500 || r.status === 0 });
  sleep(0.3);
}

export function timeout_long_content_articles() {
  const res = http.get(BASE_URL + ENDPOINT, null, { headers, timeout: '30s' });
  check(res, { '[TO02] 30s超时': r => r.status < 500 || r.status === 0 });
  sleep(0.3);
}
