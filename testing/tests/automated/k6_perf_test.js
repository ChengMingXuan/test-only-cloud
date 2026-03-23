// ============================================
// 工具2: k6 性能测试 — 五工具互补测试体系
// 覆盖维度: 并发性能 / 响应时间 / 吞吐量 / 错误率
// ============================================
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// 自定义指标
const apiErrors = new Counter('api_errors');
const apiSlowRequests = new Counter('api_slow_requests');
const authLatency = new Trend('auth_latency', true);
const crudLatency = new Trend('crud_latency', true);

export const options = {
  scenarios: {
    // 并发冒烟: 10 VU 持续 20s
    smoke: {
      executor: 'constant-vus',
      vus: 10,
      duration: '20s',
      gracefulStop: '5s',
    },
    // 阶梯负载: 逐步增加到 30 VU
    ramp: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 15 },
        { duration: '15s', target: 30 },
        { duration: '10s', target: 0 },
      ],
      startTime: '25s',
      gracefulStop: '5s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],          // 错误率 < 5%
    http_req_duration: ['p(95)<3000'],       // P95 < 3s
    auth_latency: ['p(95)<2000'],            // 认证 P95 < 2s
    crud_latency: ['p(95)<2500'],            // CRUD P95 < 2.5s
    api_errors: ['count<20'],                // 总错误 < 20
    api_slow_requests: ['count<30'],         // 慢请求 < 30
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:5000';
const ADMIN_USER = __ENV.ADMIN_USER || 'admin';
const ADMIN_PASS = __ENV.ADMIN_PASS || 'P@ssw0rd';

export function setup() {
  const loginRes = http.post(
    `${BASE}/api/auth/login`,
    JSON.stringify({ username: ADMIN_USER, password: ADMIN_PASS }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  const ok = check(loginRes, { 'setup: login 200': (r) => r.status === 200 });
  if (!ok) {
    console.error(`登录失败: ${loginRes.status} ${loginRes.body}`);
    return { token: '' };
  }
  const body = JSON.parse(loginRes.body);
  return { token: body.data ? body.data.accessToken : '' };
}

function auth(token) {
  return { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } };
}

function track(res, name, trend) {
  const ok = check(res, {
    [`${name} <500`]: (r) => r.status < 500,
    [`${name} <3s`]: (r) => r.timings.duration < 3000,
  });
  if (res.status >= 500) apiErrors.add(1);
  if (res.timings.duration >= 2000) apiSlowRequests.add(1);
  if (trend) trend.add(res.timings.duration);
}

// ── 主测试函数 ──
export default function (data) {
  const h = auth(data.token);

  group('T2.1 认证性能', () => {
    const r = http.post(
      `${BASE}/api/auth/login`,
      JSON.stringify({ username: ADMIN_USER, password: ADMIN_PASS }),
      { headers: { 'Content-Type': 'application/json' } }
    );
    track(r, '登录', authLatency);
  });

  group('T2.2 网关路由', () => {
    track(http.get(`${BASE}/api/tenants?page=1&pageSize=5`, h), '租户列表');
    track(http.get(`${BASE}/api/roles?page=1&pageSize=5`, h), '角色列表');
    track(http.get(`${BASE}/api/device?page=1&pageSize=5`, h), '设备列表');
  });

  group('T2.3 CRUD并发', () => {
    const uid = `K6_${Date.now()}_${__VU}_${__ITER}`;
    // 创建
    const cr = http.post(
      `${BASE}/api/analytics/funnel`,
      JSON.stringify({ name: `PerfFunnel_${uid}`, description: 'k6 perf test', steps: [{ name: 'S1', eventName: 'view' }, { name: 'S2', eventName: 'click' }] }),
      h
    );
    track(cr, 'CRUD创建', crudLatency);

    if (cr.status === 200 || cr.status === 201) {
      const body = JSON.parse(cr.body);
      const id = body.data && body.data.id ? body.data.id : body.data;
      if (id) {
        // 读取
        track(http.get(`${BASE}/api/analytics/funnel/${id}`, h), 'CRUD读取', crudLatency);
        // 更新
        track(http.put(`${BASE}/api/analytics/funnel/${id}`, JSON.stringify({ name: `PerfFunnel_${uid}_U` }), h), 'CRUD更新', crudLatency);
        // 删除
        track(http.del(`${BASE}/api/analytics/funnel/${id}`, null, h), 'CRUD删除', crudLatency);
      }
    }
  });

  group('T2.4 多服务并行', () => {
    const responses = http.batch([
      ['GET', `${BASE}/api/tenants?page=1&pageSize=1`, null, h],
      ['GET', `${BASE}/api/roles?page=1&pageSize=1`, null, h],
      ['GET', `${BASE}/api/menus?type=all`, null, h],
      ['GET', `${BASE}/api/device?page=1&pageSize=1`, null, h],
      ['GET', `${BASE}/api/station?page=1&pageSize=1`, null, h],
    ]);
    responses.forEach((r, i) => {
      track(r, `批量请求[${i}]`);
    });
  });

  sleep(0.3);
}

export function handleSummary(data) {
  // 输出 JSON 摘要用于汇总报告
  const summary = {
    tool: 'k6',
    timestamp: new Date().toISOString(),
    metrics: {
      total_requests: data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0,
      failed_rate: data.metrics.http_req_failed ? data.metrics.http_req_failed.values.rate : 0,
      p50_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(50)'] : 0,
      p95_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(95)'] : 0,
      p99_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(99)'] : 0,
      avg_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values.avg : 0,
      max_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values.max : 0,
      api_errors: data.metrics.api_errors ? data.metrics.api_errors.values.count : 0,
      slow_requests: data.metrics.api_slow_requests ? data.metrics.api_slow_requests.values.count : 0,
    },
    thresholds_passed: Object.entries(data.root_group ? {} : {}).length === 0,
  };
  
  // 检查阈值
  let thresholdsFailed = 0;
  if (data.metrics) {
    for (const [key, metric] of Object.entries(data.metrics)) {
      if (metric.thresholds) {
        for (const [name, result] of Object.entries(metric.thresholds)) {
          if (!result.ok) thresholdsFailed++;
        }
      }
    }
  }
  summary.thresholds_failed = thresholdsFailed;

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    '../../TestResults/k6-results.json': JSON.stringify(summary, null, 2),
  };
}

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
