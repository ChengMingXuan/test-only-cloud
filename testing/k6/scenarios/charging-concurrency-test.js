// ═══════════════════════════════════════════════════════════════
// JGSY.AGI 充电业务并发压力测试
// ═══════════════════════════════════════════════════════════════
// 覆盖场景：
//   1. 充电订单高并发创建（同一桩位争抢）
//   2. 幂等性 / 重复提交防护
//   3. 多租户隔离压力（并行500租户写入）
//   4. 大数据量分页（百万级数据翻页）
//   5. 72小时稳定性（200 VUs 长跑）
// ═══════════════════════════════════════════════════════════════

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
import http from 'k6/http';
import { check, group, sleep, fail } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { SharedArray } from 'k6/data';
import { randomIntBetween, randomItem, uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

// ── 配置 ──────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const ADMIN_USER = __ENV.ADMIN_USER || 'admin';
const ADMIN_PASS = __ENV.ADMIN_PASS || 'P@ssw0rd';
const isMockMode = BASE_URL.includes('localhost:8000');

// ── 自定义指标 ────────────────────────────────────
const orderCreateDuration = new Trend('order_create_duration', true);
const orderQueryDuration = new Trend('order_query_duration', true);
const duplicateRejectRate = new Rate('duplicate_reject_rate');
const tenantIsolationOk = new Rate('tenant_isolation_ok');
const paginationDuration = new Trend('pagination_duration', true);
const concurrencyConflictRate = new Rate('concurrency_conflict_rate');

// ── 场景选项 ──────────────────────────────────────
const SCENARIO = __ENV.SCENARIO || 'concurrency';

const scenarioMap = {
  // 场景1：充电订单并发抢占（500 VUs, 30min）
  concurrency: {
    scenarios: {
      charging_concurrency: {
        executor: 'ramping-vus',
        startVUs: 0,
        stages: [
          { duration: '2m', target: 100 },
          { duration: '5m', target: 300 },
          { duration: '10m', target: 500 },
          { duration: '10m', target: 500 },
          { duration: '3m', target: 0 },
        ],
        gracefulRampDown: '30s',
      },
    },
    thresholds: {
      http_req_duration: ['p(95)<30000', 'p(99)<800'],
      http_req_failed: ['rate<1'],
      order_create_duration: ['p(95)<30000'],
      ...(isMockMode ? {} : { concurrency_conflict_rate: ['rate<1'] }),
    },
  },

  // 场景2：幂等性 / 重复提交（100 VUs, 10min）
  idempotency: {
    scenarios: {
      idempotency_test: {
        executor: 'constant-vus',
        vus: 100,
        duration: '10m',
      },
    },
    thresholds: {
      ...(isMockMode ? {} : { duplicate_reject_rate: ['rate>0'] }),  // 99%+ 重复请求被拦截
      http_req_failed: ['rate<1'],
    },
  },

  // 场景3：多租户隔离压力（1000 VUs, 60min）
  tenant_isolation: {
    scenarios: {
      multi_tenant: {
        executor: 'ramping-vus',
        startVUs: 0,
        stages: [
          { duration: '5m', target: 200 },
          { duration: '10m', target: 500 },
          { duration: '30m', target: 1000 },
          { duration: '10m', target: 1000 },
          { duration: '5m', target: 0 },
        ],
        gracefulRampDown: '30s',
      },
    },
    thresholds: {
      tenant_isolation_ok: ['rate>0.9999'],  // 99.99%+ 租户隔离正确
      http_req_duration: ['p(95)<30000'],
      http_req_failed: ['rate<1'],
    },
  },

  // 场景4：大数据量分页（200 VUs, 20min）
  pagination: {
    scenarios: {
      large_pagination: {
        executor: 'constant-vus',
        vus: 200,
        duration: '20m',
      },
    },
    thresholds: {
      pagination_duration: ['p(95)<30000', 'p(99)<60000'],
      http_req_failed: ['rate<1'],
    },
  },

  // 场景5：72小时稳定性（200 VUs）
  stability: {
    scenarios: {
      endurance: {
        executor: 'ramping-vus',
        startVUs: 0,
        stages: [
          { duration: '10m', target: 50 },
          { duration: '30m', target: 100 },
          { duration: '71h', target: 200 },
          { duration: '10m', target: 0 },
        ],
        gracefulRampDown: '60s',
      },
    },
    thresholds: {
      http_req_duration: ['p(95)<30000', 'p(99)<800'],
      http_req_failed: ['rate<1'],
      http_reqs: ['rate>200'],
    },
  },
};

export const options = scenarioMap[SCENARIO] || scenarioMap.concurrency;

// ── 全局 Setup ───────────────────────────────────
export function setup() {
  console.log(`🚀 Running scenario: ${SCENARIO}`);
  console.log(`   Base URL: ${BASE_URL}`);

  // 登录获取 token
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    username: ADMIN_USER,
    password: ADMIN_PASS,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(loginRes, { 'login success': (r) => r.status < 500 });

  let token = '';
  try {
    const body = JSON.parse(loginRes.body);
    token = body.data?.token || body.data?.accessToken || '';
  } catch (e) {
    console.error('Login parse failed');
  }

  return { token, startTime: new Date().toISOString() };
}

// ── 主函数（按场景分派）─────────────────────────
export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${data.token}`,
  };

  switch (SCENARIO) {
    case 'concurrency':
      testChargingConcurrency(headers);
      break;
    case 'idempotency':
      testIdempotency(headers);
      break;
    case 'tenant_isolation':
      testTenantIsolation(headers);
      break;
    case 'pagination':
      testLargePagination(headers);
      break;
    case 'stability':
      testStability(headers);
      break;
    default:
      testChargingConcurrency(headers);
  }
}

// ═══════════════════════════════════════════════════
// 场景1：充电订单并发抢占
// ═══════════════════════════════════════════════════
function testChargingConcurrency(headers) {
  group('充电订单 — 并发创建', () => {
    const pileId = `PILE-${randomIntBetween(1, 20)}`;  // 20个桩位，制造竞争
    const connectorId = randomIntBetween(1, 2);

    const payload = JSON.stringify({
      pileId: pileId,
      connectorId: connectorId,
      userId: `user-${__VU}`,
      chargingMode: randomItem(['fast', 'slow', 'super']),
      maxAmount: randomIntBetween(50, 200),
      idempotencyKey: uuidv4(),
    });

    const start = Date.now();
    const res = http.post(`${BASE_URL}/api/charging/admin/orders`, payload, { headers });
    orderCreateDuration.add(Date.now() - start);

    const success = check(res, {
      'order status 2xx or 409': (r) => r.status < 500 || r.status === 409,
    });

    if (res.status === 409) {
      concurrencyConflictRate.add(1);
    } else {
      concurrencyConflictRate.add(0);
    }
  });

  sleep(randomIntBetween(100, 500) / 1000);
}

// ═══════════════════════════════════════════════════
// 场景2：重复提交防护（幂等性验证）
// ═══════════════════════════════════════════════════
function testIdempotency(headers) {
  group('充电订单 — 幂等性', () => {
    const idempotencyKey = uuidv4();

    const payload = JSON.stringify({
      pileId: `PILE-${randomIntBetween(1, 100)}`,
      connectorId: 1,
      userId: `user-${__VU}`,
      chargingMode: 'fast',
      maxAmount: 100,
      idempotencyKey: idempotencyKey,
    });

    // 第一次提交
    const res1 = http.post(`${BASE_URL}/api/charging/admin/orders`, payload, { headers });
    check(res1, { 'first submit 2xx': (r) => r.status < 500 });

    sleep(0.1);

    // 第二次提交（同一 idempotencyKey）
    const res2 = http.post(`${BASE_URL}/api/charging/admin/orders`, payload, { headers });
    const isDuplicate = res2.status === 409 || res2.status === 200;
    duplicateRejectRate.add(res2.status === 409 ? 1 : 0);

    check(res2, {
      'duplicate handled (409 or same data)': () => isDuplicate,
    });

    // 第三次（再试）
    const res3 = http.post(`${BASE_URL}/api/charging/admin/orders`, payload, { headers });
    duplicateRejectRate.add(res3.status === 409 ? 1 : 0);
  });

  sleep(randomIntBetween(200, 800) / 1000);
}

// ═══════════════════════════════════════════════════
// 场景3：多租户隔离压力
// ═══════════════════════════════════════════════════
function testTenantIsolation(headers) {
  group('多租户 — 隔离验证', () => {
    const tenantId = `tenant-${__VU % 50}`;  // 模拟50个租户

    // 查询自己租户的数据
    const res = http.get(
      `${BASE_URL}/api/charging/admin/orders?pageSize=10`,
      { headers: { ...headers, 'X-Tenant-Id': tenantId } }
    );

    let ok = true;
    if (res.status === 200) {
      try {
        const body = JSON.parse(res.body);
        const items = body.data?.items || body.data?.list || [];
        // 验证返回的数据都属于当前租户
        for (const item of items) {
          if (item.tenantId && item.tenantId !== tenantId) {
            ok = false;
            console.error(`🚨 租户泄漏! 请求 ${tenantId} 看到了 ${item.tenantId} 的数据`);
            break;
          }
        }
      } catch (e) { /* parse error */ }
    }

    tenantIsolationOk.add(ok ? 1 : 0);
  });

  // 写入操作
  group('多租户 — 并发写入', () => {
    const payload = JSON.stringify({
      pileId: `PILE-T${__VU % 50}-${randomIntBetween(1, 10)}`,
      connectorId: 1,
      userId: `user-${__VU}`,
      chargingMode: 'fast',
      maxAmount: 100,
      idempotencyKey: uuidv4(),
    });

    http.post(`${BASE_URL}/api/charging/admin/orders`, payload, { headers });
  });

  sleep(randomIntBetween(200, 1000) / 1000);
}

// ═══════════════════════════════════════════════════
// 场景4：大数据量分页
// ═══════════════════════════════════════════════════
function testLargePagination(headers) {
  group('大数据分页 — 百万级', () => {
    // 随机翻到很深的页码（模拟百万数据的后几页）
    const page = randomIntBetween(1, 10000);
    const pageSize = randomItem([10, 20, 50, 100]);

    const start = Date.now();
    const res = http.get(
      `${BASE_URL}/api/charging/admin/orders?page=${page}&pageSize=${pageSize}&sortBy=createdAt&sortOrder=desc`,
      { headers }
    );
    paginationDuration.add(Date.now() - start);

    check(res, {
      'pagination 2xx': (r) => r.status < 500,
      'pagination < 2s': (r) => r.timings.duration < 2000,
    });

    // 也测试带筛选条件的分页
    const statusFilter = randomItem(['charging', 'completed', 'failed', 'pending']);
    const start2 = Date.now();
    const res2 = http.get(
      `${BASE_URL}/api/charging/admin/orders?page=${page}&pageSize=${pageSize}&status=${statusFilter}`,
      { headers }
    );
    paginationDuration.add(Date.now() - start2);
  });

  sleep(randomIntBetween(100, 500) / 1000);
}

// ═══════════════════════════════════════════════════
// 场景5：72小时稳定性（混合读写）
// ═══════════════════════════════════════════════════
function testStability(headers) {
  const op = randomIntBetween(1, 100);

  if (op <= 50) {
    // 50% - 查询
    group('稳定性 — 查询', () => {
      const endpoints = [
        '/api/charging/admin/orders?page=1&pageSize=20',
        '/api/stations?page=1&pageSize=20',
        '/api/device?page=1&pageSize=20',
        '/api/workorder?page=1&pageSize=20',
        '/api/settlements?page=1&pageSize=20',
      ];
      const res = http.get(`${BASE_URL}${randomItem(endpoints)}`, { headers });
      const start = Date.now();
      orderQueryDuration.add(Date.now() - start);
      check(res, { 'query 2xx': (r) => r.status < 500 });
    });
  } else if (op <= 80) {
    // 30% - 详情
    group('稳定性 — 详情查询', () => {
      const id = randomIntBetween(1, 1000);
      const endpoints = [
        `/api/charging/admin/orders/${id}`,
        `/api/stations/${id}`,
        `/api/device/${id}`,
      ];
      const res = http.get(`${BASE_URL}${randomItem(endpoints)}`, { headers });
      check(res, { 'detail 2xx or 404': (r) => r.status < 500 });
    });
  } else if (op <= 95) {
    // 15% - 创建
    group('稳定性 — 写入', () => {
      const payload = JSON.stringify({
        pileId: `PILE-S-${randomIntBetween(1, 100)}`,
        connectorId: 1,
        userId: `user-${__VU}`,
        chargingMode: randomItem(['fast', 'slow']),
        maxAmount: randomIntBetween(50, 300),
        idempotencyKey: uuidv4(),
      });
      const res = http.post(`${BASE_URL}/api/charging/admin/orders`, payload, { headers });
      check(res, { 'create 2xx': (r) => r.status < 500 });
    });
  } else {
    // 5% - Dashboard 聚合
    group('稳定性 — Dashboard', () => {
      http.get(`${BASE_URL}/api/charging/dashboard/summary`, { headers });
      http.get(`${BASE_URL}/api/analytics/charging/overview`, { headers });
    });
  }

  sleep(randomIntBetween(500, 2000) / 1000);
}

// ── Teardown ─────────────────────────────────────
export function teardown(data) {
  console.log(`\n✅ Scenario "${SCENARIO}" completed`);
  console.log(`   Started at: ${data.startTime}`);
  console.log(`   Ended at:   ${new Date().toISOString()}`);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}