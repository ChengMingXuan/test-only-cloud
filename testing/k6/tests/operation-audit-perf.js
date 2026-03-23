// k6 性能基准测试 — 操作审计日志 API
// ======================================
// 覆盖: 分页查询 / 详情 / 统计 / 资源历史 / 回滚预检 / 回滚执行
// 5 场景: 冒烟 / 恒定负载 / 阶梯压力 / 峰值 / 回滚专项
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import exec from 'k6/execution';

// ── 自定义指标 ──────────────────────────────────────
const errorRate = new Rate('errors');
const successRate = new Rate('success');
const queryDuration = new Trend('oplog_query_duration');
const detailDuration = new Trend('oplog_detail_duration');
const statsDuration = new Trend('oplog_stats_duration');
const rollbackDuration = new Trend('oplog_rollback_duration');

// ── 配置 ────────────────────────────────────────────
export const options = {
  scenarios: {
    // 场景1：冒烟测试（快速验证）
    smoke: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
    },
    // 场景2：恒定负载
    constant_load: {
      executor: 'constant-vus',
      vus: 30,
      duration: '2m',
      startTime: '35s',
    },
    // 场景3：阶梯压力
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '2m',  target: 100 },
        { duration: '1m',  target: 150 },
        { duration: '30s', target: 0 },
      ],
      startTime: '2m40s',
    },
    // 场景4：峰值（突发并发）
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 200 },
        { duration: '30s', target: 200 },
        { duration: '10s', target: 0 },
      ],
      startTime: '7m',
    },
    // 场景5：回滚专项（低并发长时间）
    rollback_stress: {
      executor: 'constant-vus',
      vus: 10,
      duration: '1m',
      startTime: '8m',
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'],
    'http_req_failed': ['rate<0.02'],
    'oplog_query_duration': ['avg<500', 'p(95)<1500'],
    'oplog_detail_duration': ['avg<300', 'p(95)<800'],
    'oplog_stats_duration': ['avg<800', 'p(95)<2000'],
    'oplog_rollback_duration': ['avg<1000', 'p(95)<3000'],
    'errors': ['rate<0.02'],
    'success': ['rate>0.95'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const ACCESS_TOKEN = __ENV.ACCESS_TOKEN || '';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${ACCESS_TOKEN}`,
};

// ── 审计分类/操作类型随机池 ─────────────────────────
const CATEGORIES = ['permission', 'strategy', 'device_command', 'transaction', 'config', 'work_order', 'auth', 'data_export', 'rollback'];
const ACTIONS = ['Create', 'Update', 'Delete', 'Execute', 'Approve', 'Reject', 'Rollback', 'Export', 'Import', 'Login', 'Logout'];
const RISK_LEVELS = ['low', 'medium', 'high', 'critical'];
const SERVICE_NAMES = ['permission', 'account', 'device', 'charging', 'station', 'workorder', 'observability'];

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

// ── 主测试函数 ──────────────────────────────────────
export default function () {
  if (!ACCESS_TOKEN) {
    console.error('请设置 ACCESS_TOKEN 环境变量');
    return;
  }

  const scenario = __ENV.SCENARIO || (exec.scenario ? exec.scenario.name : 'smoke');

  // 回滚专项场景 → 只测回滚
  if (scenario === 'rollback_stress') {
    rollbackTest();
    return;
  }

  // 根据权重随机选择测试分支
  const rand = Math.random();
  if (rand < 0.45) {
    queryTest();
  } else if (rand < 0.65) {
    detailTest();
  } else if (rand < 0.80) {
    statisticsTest();
  } else if (rand < 0.90) {
    resourceHistoryTest();
  } else {
    rollbackCheckTest();
  }
}

// ── 分页查询测试 ────────────────────────────────────
function queryTest() {
  group('操作审计-分页查询', () => {
    const scenarios = [
      { name: '默认分页', params: `page=${Math.floor(Math.random() * 10) + 1}&pageSize=20` },
      { name: '按分类过滤', params: `page=1&pageSize=20&category=${randomItem(CATEGORIES)}` },
      { name: '按操作类型', params: `page=1&pageSize=20&action=${randomItem(ACTIONS)}` },
      { name: '按风险等级', params: `page=1&pageSize=20&riskLevel=${randomItem(RISK_LEVELS)}` },
      { name: '按服务名', params: `page=1&pageSize=20&serviceName=${randomItem(SERVICE_NAMES)}` },
      { name: '关键词搜索', params: `page=1&pageSize=20&keyword=${encodeURIComponent(['设备', '角色', '用户', '配置'][Math.floor(Math.random() * 4)])}` },
      { name: '时间范围', params: `page=1&pageSize=20&startTime=${new Date(Date.now() - 7 * 86400000).toISOString()}&endTime=${new Date().toISOString()}` },
      { name: '组合过滤', params: `page=1&pageSize=10&category=${randomItem(CATEGORIES)}&action=${randomItem(ACTIONS)}&riskLevel=${randomItem(RISK_LEVELS)}` },
    ];

    const s = randomItem(scenarios);
    const startTime = Date.now();
    const resp = http.get(`${BASE_URL}/api/monitor/operation-logs?${s.params}`, { headers });
    queryDuration.add(Date.now() - startTime);

    const ok = check(resp, {
      [`${s.name}-状态码<500`]: (r) => r.status < 500,
      [`${s.name}-响应<2s`]: (r) => r.timings.duration < 2000,
      [`${s.name}-有数据结构`]: (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.success !== undefined || body.data !== undefined;
        } catch { return false; }
      },
    });

    successRate.add(ok);
    errorRate.add(!ok);
    sleep(0.2);
  });
}

// ── 详情查询测试 ────────────────────────────────────
function detailTest() {
  group('操作审计-详情查询', () => {
    const id = randomUUID();
    const startTime = Date.now();
    const resp = http.get(`${BASE_URL}/api/monitor/operation-logs/${id}`, { headers });
    detailDuration.add(Date.now() - startTime);

    const ok = check(resp, {
      '详情-状态码<500': (r) => r.status < 500,
      '详情-响应<1s': (r) => r.timings.duration < 1000,
    });

    successRate.add(ok);
    errorRate.add(!ok);
    sleep(0.1);
  });
}

// ── 统计查询测试 ────────────────────────────────────
function statisticsTest() {
  group('操作审计-统计查询', () => {
    const params = `startTime=${new Date(Date.now() - 24 * 3600000).toISOString()}&endTime=${new Date().toISOString()}`;
    const startTime = Date.now();
    const resp = http.get(`${BASE_URL}/api/monitor/operation-logs/statistics?${params}`, { headers });
    statsDuration.add(Date.now() - startTime);

    const ok = check(resp, {
      '统计-状态码<500': (r) => r.status < 500,
      '统计-响应<3s': (r) => r.timings.duration < 3000,
      '统计-有统计数据': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.data !== undefined;
        } catch { return false; }
      },
    });

    successRate.add(ok);
    errorRate.add(!ok);
    sleep(0.3);
  });
}

// ── 资源历史测试 ────────────────────────────────────
function resourceHistoryTest() {
  group('操作审计-资源历史', () => {
    const resourceType = randomItem(['device', 'role', 'user', 'station', 'order']);
    const resourceId = randomUUID();
    const resp = http.get(
      `${BASE_URL}/api/monitor/operation-logs/resource-history?resourceType=${resourceType}&resourceId=${resourceId}`,
      { headers }
    );

    const ok = check(resp, {
      '资源历史-状态码<500': (r) => r.status < 500,
      '资源历史-响应<1.5s': (r) => r.timings.duration < 1500,
    });

    successRate.add(ok);
    errorRate.add(!ok);
    sleep(0.2);
  });
}

// ── 回滚预检测试 ────────────────────────────────────
function rollbackCheckTest() {
  group('操作审计-回滚预检', () => {
    const id = randomUUID();
    const resp = http.get(`${BASE_URL}/api/monitor/operation-logs/${id}/rollback-check`, { headers });

    const ok = check(resp, {
      '回滚预检-状态码<500': (r) => r.status < 500,
      '回滚预检-响应<1s': (r) => r.timings.duration < 1000,
    });

    successRate.add(ok);
    errorRate.add(!ok);
    sleep(0.2);
  });
}

// ── 回滚执行测试 ────────────────────────────────────
function rollbackTest() {
  group('操作审计-回滚执行', () => {
    const id = randomUUID();

    // Step1: 先预检
    const checkResp = http.get(`${BASE_URL}/api/monitor/operation-logs/${id}/rollback-check`, { headers });
    check(checkResp, {
      '回滚预检-状态码<500': (r) => r.status < 500,
    });

    // Step2: 执行回滚
    const startTime = Date.now();
    const rollbackResp = http.post(`${BASE_URL}/api/monitor/operation-logs/${id}/rollback`, null, { headers });
    rollbackDuration.add(Date.now() - startTime);

    const ok = check(rollbackResp, {
      '回滚执行-状态码<500': (r) => r.status < 500,
      '回滚执行-响应<3s': (r) => r.timings.duration < 3000,
    });

    successRate.add(ok);
    errorRate.add(!ok);
    sleep(0.5);
  });
}
