/**
 * k6 — DAG 工作流性能压测 (v3.1 增量)
 * 覆盖: 工作流列表 / 执行 / 历史查询 / 详情查询
 * 指标: 吞吐量、延迟、错误率
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ━━━━━━━━━━━━━━━━ 自定义指标 ━━━━━━━━━━━━━━━━
const dagListSuccess = new Rate('dag_list_success');
const dagListDuration = new Trend('dag_list_duration', true);
const dagExecuteSuccess = new Rate('dag_execute_success');
const dagExecuteDuration = new Trend('dag_execute_duration', true);
const dagHistorySuccess = new Rate('dag_history_success');
const dagHistoryDuration = new Trend('dag_history_duration', true);
const dagDetailSuccess = new Rate('dag_detail_success');
const dagDetailDuration = new Trend('dag_detail_duration', true);
const totalErrors = new Counter('dag_total_errors');

// ━━━━━━━━━━━━━━━━ 配置 ━━━━━━━━━━━━━━━━
const BASE_URL = __ENV.API_URL || 'http://localhost:5062';
const TOKEN = __ENV.AUTH_TOKEN || '';

const HEADERS = {
  'Content-Type': 'application/json',
  Authorization: TOKEN ? `Bearer ${TOKEN}` : '',
};

// ━━━━━━━━━━━━━━━━ 场景配置 ━━━━━━━━━━━━━━━━
export const options = {
  scenarios: {
    // 场景 1: 工作流列表 (轻量查询)
    dag_list: {
      executor: 'constant-arrival-rate',
      rate: 20,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 10,
      maxVUs: 30,
      exec: 'listWorkflows',
    },
    // 场景 2: 执行工作流 (中量写入)
    dag_execute: {
      executor: 'ramping-arrival-rate',
      startRate: 2,
      timeUnit: '1s',
      stages: [
        { duration: '10s', target: 5 },
        { duration: '20s', target: 10 },
        { duration: '10s', target: 2 },
      ],
      preAllocatedVUs: 10,
      maxVUs: 30,
      exec: 'executeWorkflow',
    },
    // 场景 3: 执行历史分页 (轻量查询)
    dag_history: {
      executor: 'constant-arrival-rate',
      rate: 15,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 8,
      maxVUs: 20,
      exec: 'queryHistory',
    },
    // 场景 4: 执行详情 (中量查询)
    dag_detail: {
      executor: 'constant-arrival-rate',
      rate: 10,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 5,
      maxVUs: 15,
      exec: 'queryDetail',
    },
  },
  thresholds: {
    dag_list_success: ['rate>0.95'],
    dag_list_duration: ['p(95)<500', 'p(99)<1000'],
    dag_execute_success: ['rate>0.90'],
    dag_execute_duration: ['p(95)<5000', 'p(99)<10000'],
    dag_history_success: ['rate>0.95'],
    dag_history_duration: ['p(95)<800', 'p(99)<1500'],
    dag_detail_success: ['rate>0.95'],
    dag_detail_duration: ['p(95)<600', 'p(99)<1200'],
    dag_total_errors: ['count<50'],
  },
};

// ━━━━━━━━━━━━━━━━ 场景函数 ━━━━━━━━━━━━━━━━

/** 场景 1: 查询工作流列表 */
export function listWorkflows() {
  const res = http.get(`${BASE_URL}/api/iotcloudai/dag/workflows`, { headers: HEADERS, tags: { name: 'DAG_ListWorkflows' } });
  const ok = check(res, {
    'list: status 200': (r) => r.status === 200,
    'list: has data': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.code === 200 && Array.isArray(body.data);
      } catch {
        return false;
      }
    },
    'list: < 500ms': (r) => r.timings.duration < 500,
  });
  dagListSuccess.add(ok);
  dagListDuration.add(res.timings.duration);
  if (!ok) totalErrors.add(1);
  sleep(0.1);
}

/** 场景 2: 执行 DAG 工作流 */
export function executeWorkflow() {
  const workflows = ['device-diagnosis', 'energy-optimization', 'anomaly-detection'];
  const wfId = workflows[Math.floor(Math.random() * workflows.length)];
  const payload = JSON.stringify({
    input: `k6 性能测试 - 设备 PCS-${String(Math.floor(Math.random() * 999)).padStart(3, '0')} 状态异常`,
    parameters: { severity: 'high', source: 'k6-test' },
  });

  const res = http.post(`${BASE_URL}/api/iotcloudai/dag/workflows/${wfId}/execute`, payload, {
    headers: HEADERS,
    tags: { name: 'DAG_Execute' },
    timeout: '15s',
  });

  const ok = check(res, {
    'exec: status 200': (r) => r.status === 200,
    'exec: has result': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.code === 200 && body.data && body.data.finalAnswer;
      } catch {
        return false;
      }
    },
    'exec: has fusedConfidence': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.data && body.data.fusedConfidence !== undefined;
      } catch {
        return false;
      }
    },
    'exec: < 5s': (r) => r.timings.duration < 5000,
  });
  dagExecuteSuccess.add(ok);
  dagExecuteDuration.add(res.timings.duration);
  if (!ok) totalErrors.add(1);
  sleep(0.5);
}

/** 场景 3: 查询执行历史列表 */
export function queryHistory() {
  const page = Math.floor(Math.random() * 5) + 1;
  const res = http.get(`${BASE_URL}/api/iotcloudai/dag/executions?page=${page}&pageSize=20`, {
    headers: HEADERS,
    tags: { name: 'DAG_History' },
  });

  const ok = check(res, {
    'history: status 200': (r) => r.status === 200,
    'history: has items': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.code === 200 && body.data;
      } catch {
        return false;
      }
    },
    'history: < 800ms': (r) => r.timings.duration < 800,
  });
  dagHistorySuccess.add(ok);
  dagHistoryDuration.add(res.timings.duration);
  if (!ok) totalErrors.add(1);
  sleep(0.1);
}

/** 场景 4: 查询执行详情 */
export function queryDetail() {
  // 使用固定的示例 ID 或从历史中获取
  const executionId = '11111111-1111-1111-1111-111111111111';
  const res = http.get(`${BASE_URL}/api/iotcloudai/dag/executions/${executionId}`, {
    headers: HEADERS,
    tags: { name: 'DAG_Detail' },
  });

  const ok = check(res, {
    'detail: status 200 or 404': (r) => r.status === 200 || r.status === 404,
    'detail: < 600ms': (r) => r.timings.duration < 600,
  });
  dagDetailSuccess.add(ok);
  dagDetailDuration.add(res.timings.duration);
  if (!ok) totalErrors.add(1);
  sleep(0.1);
}

// ━━━━━━━━━━━━━━━━ 生命周期钩子 ━━━━━━━━━━━━━━━━
export function handleSummary(data) {
  const now = new Date().toISOString().replace(/[:.]/g, '-');
  return {
    [`TestResults/k6/dag-workflow-${now}.json`]: JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, opts) {
  const lines = ['═══════════════ DAG 工作流性能测试摘要 ═══════════════'];
  if (data.metrics) {
    for (const [name, metric] of Object.entries(data.metrics)) {
      if (name.startsWith('dag_')) {
        lines.push(`  ${name}: ${JSON.stringify(metric.values)}`);
      }
    }
  }
  return lines.join('\n') + '\n';
}
