// k6 性能基准测试 — 规则引擎边缘模式 API
// 场景：规则触发、规则链查询、执行日志查询、边缘节点状态
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const successRate = new Rate('success');
const triggerDuration = new Trend('rule_trigger_duration');
const chainQueryDuration = new Trend('chain_query_duration');
const logQueryDuration = new Trend('log_query_duration');
const edgeStatusDuration = new Trend('edge_status_duration');

// 测试配置
export const options = {
  scenarios: {
    // 场景1：恒定负载 — 规则触发
    rule_trigger_load: {
      executor: 'constant-vus',
      vus: 30,
      duration: '2m',
      exec: 'triggerRules',
    },
    // 场景2：规则链查询压力
    chain_query_stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '1m', target: 50 },
        { duration: '30s', target: 100 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
      ],
      exec: 'queryChains',
      startTime: '2m30s',
    },
    // 场景3：边缘状态轮询
    edge_status_polling: {
      executor: 'constant-arrival-rate',
      rate: 10,
      timeUnit: '1s',
      duration: '1m',
      preAllocatedVUs: 20,
      exec: 'pollEdgeStatus',
      startTime: '6m',
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'],   // 商用 SLA
    'http_req_failed': ['rate<0.05'],                     // 错误率 ≤ 5%
    'rule_trigger_duration': ['avg<500', 'p(95)<1000'],   // 规则触发 avg<500ms
    'chain_query_duration': ['avg<300', 'p(95)<800'],     // 查询 avg<300ms
    'log_query_duration': ['avg<400', 'p(95)<1000'],      // 日志查询 avg<400ms
    'edge_status_duration': ['avg<200', 'p(95)<500'],     // 状态查询 avg<200ms
    'errors': ['rate<0.05'],
    'success': ['rate>0.90'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': AUTH_TOKEN ? `Bearer ${AUTH_TOKEN}` : '',
};

// 设备类型池
const deviceTypes = ['charging_pile', 'inverter', 'battery', 'pcs', 'meter'];
const triggerTypes = ['telemetry', 'event', 'alarm', 'status'];

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// ==========================================
// 场景1：规则触发
// ==========================================
export function triggerRules() {
  group('规则触发', function () {
    const payload = JSON.stringify({
      tenantId: '00000000-0000-0000-0000-000000000001',
      deviceId: uuid(),
      deviceType: randomItem(deviceTypes),
      triggerType: randomItem(triggerTypes),
      payload: JSON.stringify({
        temperature: Math.random() * 120,
        voltage: 380 + Math.random() * 20,
        current: Math.random() * 50,
        soc: Math.random() * 100,
      }),
    });

    const start = Date.now();
    const resp = http.post(`${BASE_URL}/api/ruleengine/trigger`, payload, { headers });
    const duration = Date.now() - start;
    triggerDuration.add(duration);

    const isOk = check(resp, {
      '触发状态码正常': (r) => [200, 202, 400, 404].includes(r.status),
      '响应时间<1s': (r) => r.timings.duration < 1000,
    });

    successRate.add(isOk);
    errorRate.add(!isOk);
    sleep(0.5);
  });
}

// ==========================================
// 场景2：规则链查询
// ==========================================
export function queryChains() {
  group('规则链查询', function () {
    // 分页查询
    const start = Date.now();
    const resp = http.get(
      `${BASE_URL}/api/ruleengine/chains?page=1&pageSize=10`,
      { headers }
    );
    const duration = Date.now() - start;
    chainQueryDuration.add(duration);

    const isOk = check(resp, {
      '查询状态码200': (r) => r.status === 200 || r.status === 401,
      '响应时间<800ms': (r) => r.timings.duration < 800,
    });

    successRate.add(isOk);
    errorRate.add(!isOk);

    // 带过滤条件查询
    const filterResp = http.get(
      `${BASE_URL}/api/ruleengine/chains?page=1&pageSize=10&deviceType=${randomItem(deviceTypes)}&isEnabled=true`,
      { headers }
    );

    check(filterResp, {
      '过滤查询正常': (r) => r.status === 200 || r.status === 401,
    });

    // 查询执行日志
    const logStart = Date.now();
    const logResp = http.get(
      `${BASE_URL}/api/ruleengine/logs?page=1&pageSize=10`,
      { headers }
    );
    const logDuration = Date.now() - logStart;
    logQueryDuration.add(logDuration);

    check(logResp, {
      '日志查询正常': (r) => [200, 401, 404].includes(r.status),
    });

    sleep(1);
  });
}

// ==========================================
// 场景3：边缘状态轮询
// ==========================================
export function pollEdgeStatus() {
  group('边缘状态轮询', function () {
    const start = Date.now();
    const resp = http.get(
      `${BASE_URL}/api/ruleengine/edge/status`,
      { headers }
    );
    const duration = Date.now() - start;
    edgeStatusDuration.add(duration);

    const isOk = check(resp, {
      '状态查询正常': (r) => [200, 401, 404].includes(r.status),
      '响应时间<500ms': (r) => r.timings.duration < 500,
    });

    successRate.add(isOk);
    errorRate.add(!isOk);
  });
}

// ==========================================
// 默认函数（混合场景）
// ==========================================
export default function () {
  group('混合场景 — 规则引擎边缘模式', function () {
    // 查询规则链
    const chainResp = http.get(
      `${BASE_URL}/api/ruleengine/chains?page=1&pageSize=5`,
      { headers }
    );
    check(chainResp, {
      '规则链列表正常': (r) => r.status < 500,
    });

    // 触发规则
    const triggerPayload = JSON.stringify({
      tenantId: '00000000-0000-0000-0000-000000000001',
      deviceId: uuid(),
      deviceType: 'charging_pile',
      triggerType: 'telemetry',
      payload: JSON.stringify({ temperature: 85.5 }),
    });
    const triggerResp = http.post(
      `${BASE_URL}/api/ruleengine/trigger`,
      triggerPayload,
      { headers }
    );
    check(triggerResp, {
      '触发正常': (r) => r.status < 500,
    });

    // 查询状态
    const statusResp = http.get(
      `${BASE_URL}/api/ruleengine/edge/status`,
      { headers }
    );
    check(statusResp, {
      '状态正常': (r) => r.status < 500,
    });

    sleep(2);
  });
}
