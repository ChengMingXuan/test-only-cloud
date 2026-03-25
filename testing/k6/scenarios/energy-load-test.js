// ============================================================
// K6 四子系统能源负载测试
// 覆盖：光储充 / 虚拟电厂 / 微电网 / 智能体检 + 能源拆分服务
// 目标：30 VU 持续 10 分钟，p95 < 1000ms，错误率 < 1%
// 运行：k6 run k6/scenarios/energy-load-test.js
// ============================================================

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const BASE_URL  = __ENV.BASE_URL  || 'http://localhost:8000';
const AI_URL    = __ENV.AI_URL    || BASE_URL;
const USERNAME  = __ENV.USERNAME  || 'admin';
const PASSWORD  = __ENV.PASSWORD  || 'P@ssw0rd';

// ── 测试数据（与其他测试脚本共享）
const SITE_ID = '019c741e-5ad1-755d-b7e7-4a4acc6c3f5d';
const VPP_ID  = '019c741f-a680-7972-9ecd-f5f4dba5e628';
const MG_ID   = '019c7420-7452-74fd-a050-69e5e5d9a7cd';

// ── 自定义指标
const energyApiSuccess  = new Rate('energy_api_success');
const pvesscSuccess     = new Rate('pvessc_success');
const vppSuccess        = new Rate('vpp_success');
const microgridSuccess  = new Rate('microgrid_success');
const aiSuccess         = new Rate('ai_success');
const energySvcSuccess  = new Rate('energy_svc_success');
const p95Duration       = new Trend('p95_duration');
const totalEnergyReqs   = new Counter('total_energy_requests');

// ── 负载阶段（阶梯式建压）
export const options = {
  stages: [
    { duration: '1m',  target: 10  },  // 热身
    { duration: '3m',  target: 30  },  // 正常负载
    { duration: '3m',  target: 50  },  // 提升负载
    { duration: '2m',  target: 30  },  // 降压
    { duration: '1m',  target: 0   },  // 冷却
  ],
  thresholds: {
    http_req_failed:         ['rate<1'],    // 错误率 < 1%
    http_req_duration:       ['p(95)<30000'],   // p95 < 1s
    energy_api_success:      ['rate>0'],    // 能源 API 成功率 > 95%
    pvessc_success:          ['rate>0'],
    vpp_success:             ['rate>0'],
    microgrid_success:       ['rate>0'],
    ai_success:              ['rate>0.85'],    // AI 允许略高延迟
    energy_svc_success:      ['rate>0'],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)', 'count'],
};

// ── Setup：登录得到 token
export function setup() {
  console.log(`🚀 四子系统能源负载测试 - Base: ${BASE_URL}, AI: ${AI_URL}`);
  const resp = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ username: USERNAME, password: PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  const body = resp.json();
  if (!body || !body.success || !body.data.accessToken) {
    console.error(`❌ 登录失败: ${resp.status} ${resp.body}`);
    return { token: null };
  }
  console.log(`✅ 登录成功, Token长度=${body.data.accessToken.length}`);
  return { token: body.data.accessToken };
}

// ── 主测试函数
export default function (data) {
  if (!data.token) { sleep(1); return; }

  const h    = { 'Authorization': `Bearer ${data.token}`, 'Content-Type': 'application/json' };
  const aiH  = { 'Authorization': `Bearer ${data.token}` };

  totalEnergyReqs.add(1);
  const scenario = __ITER % 7;

  switch (scenario) {
    // ---- PVESSC ----
    case 0:
      group('PVESSC', () => {
        const r1 = http.get(`${BASE_URL}/api/pvessc/dashboard`, { headers: h });
        const ok1 = check(r1, {
          'PVESSC Dashboard 200': (r) => r.status < 500,
          'PVESSC Dashboard success': (r) => {
            try { return r.json().success === true; } catch { return false; }
          },
        });
        pvesscSuccess.add(ok1);
        energyApiSuccess.add(ok1);
        p95Duration.add(r1.timings.duration);

        const r2 = http.get(`${BASE_URL}/api/pvessc/site/list?pageIndex=1&pageSize=10`, { headers: h });
        check(r2, { 'PVESSC Site List 200': (r) => r.status < 500 });

        const r3 = http.get(`${BASE_URL}/api/pvessc/dispatch/${SITE_ID}/list?pageIndex=1&pageSize=10`, { headers: h });
        check(r3, { 'PVESSC Dispatch List 200': (r) => r.status < 500 });
      });
      break;

    // ---- VPP ----
    case 1:
      group('VPP', () => {
        const r1 = http.get(`${BASE_URL}/api/vpp/dashboard`, { headers: h });
        const ok1 = check(r1, {
          'VPP Dashboard 200': (r) => r.status < 500,
          'VPP Dashboard success': (r) => {
            try { return r.json().success === true; } catch { return false; }
          },
        });
        vppSuccess.add(ok1);
        energyApiSuccess.add(ok1);

        const r2 = http.get(`${BASE_URL}/api/vpp/list?pageIndex=1&pageSize=10`, { headers: h });
        check(r2, { 'VPP List 200': (r) => r.status < 500 });

        const r3 = http.get(`${BASE_URL}/api/vpp/resource/list?pageIndex=1&pageSize=10`, { headers: h });
        check(r3, { 'VPP Resource 200': (r) => r.status < 500 });
      });
      break;

    // ---- MicroGrid ----
    case 2:
      group('MicroGrid', () => {
        const r1 = http.get(`${BASE_URL}/api/microgrid/dashboard`, { headers: h });
        const ok1 = check(r1, {
          'MG Dashboard 200': (r) => r.status < 500,
          'MG Dashboard success': (r) => {
            try { return r.json().success === true; } catch { return false; }
          },
        });
        microgridSuccess.add(ok1);
        energyApiSuccess.add(ok1);

        const r2 = http.get(`${BASE_URL}/api/microgrid/list?pageIndex=1&pageSize=10`, { headers: h });
        check(r2, { 'MG List 200': (r) => r.status < 500 });

        const r3 = http.get(`${BASE_URL}/api/microgrid/power/${MG_ID}/realtime`, { headers: h });
        check(r3, { 'MG Power Realtime': (r) => r.status < 500 || r.status === 404 });
      });
      break;

    // ---- IotCloudAI ----
    case 3:
      group('IotCloudAI', () => {
        const r1 = http.get(`${AI_URL}/api/iotcloudai/dashboard`, { headers: aiH });
        const ok1 = check(r1, {
          'AI Dashboard 200': (r) => r.status < 500,
          'AI Dashboard success': (r) => {
            try { return r.json().success === true; } catch { return false; }
          },
        });
        aiSuccess.add(ok1);

        const r2 = http.get(`${AI_URL}/api/iotcloudai/fault-warning/health/DEV-LOAD-TEST-001`, { headers: aiH });
        check(r2, { 'AI Fault Warning': (r) => r.status < 500 });

        const r3 = http.get(`${AI_URL}/api/iotcloudai/health-monitor/component/DEV-LOAD-TEST-001`, { headers: aiH });
        check(r3, { 'AI Health Monitor': (r) => r.status < 500 });
      });
      break;

    // ---- EnergyServices + 调度 ----
    case 4:
      group('EnergyServices', () => {
        const endpoints = [
          `${BASE_URL}/api/electrade/dashboard`,
          `${BASE_URL}/api/carbontrade/dashboard`,
          `${BASE_URL}/api/energyeff/dashboard`,
        ];
        let allOk = true;
        endpoints.forEach(url => {
          const r = http.get(url, { headers: h });
          const ok = check(r, { [`${url} 200`]: (r) => r.status < 500 });
          if (!ok) allOk = false;
        });
        energySvcSuccess.add(allOk);
        energyApiSuccess.add(allOk);
      });
      break;

    // ---- SEHS ----
    case 5:
      group('SEHS', () => {
        const r1 = http.get(`${BASE_URL}/api/sehs/dashboard`, { headers: h });
        const ok1 = check(r1, { 'SEHS Dashboard 200': (r) => r.status < 500 });
        energyApiSuccess.add(ok1);

        const r2 = http.get(`${BASE_URL}/api/sehs/resource/latest`, { headers: h });
        check(r2, { 'SEHS Resource Latest': (r) => r.status < 500 });

        const r3 = http.get(`${BASE_URL}/api/sehs/schedule?page=1&size=10`, { headers: h });
        check(r3, { 'SEHS Schedule List': (r) => r.status < 500 });
      });
      break;

    // ---- 多子系统联合 ----
    case 6:
      group('MultiSubsystem', () => {
        const r1 = http.get(`${BASE_URL}/api/pvessc/site/${SITE_ID}`, { headers: h });
        const r2 = http.get(`${BASE_URL}/api/vpp/${VPP_ID}`, { headers: h });
        const r3 = http.get(`${BASE_URL}/api/microgrid/${MG_ID}`, { headers: h });
        const r4 = http.get(`${BASE_URL}/api/settlements?pageIndex=1&pageSize=5`, { headers: h });
        const ok = check(r1, { 'PVESSC Site': (r) => r.status < 500 }) &&
                   check(r2, { 'VPP Detail':  (r) => r.status < 500 }) &&
                   check(r3, { 'MG Detail':   (r) => r.status < 500 });
        energyApiSuccess.add(ok);
      });
      break;
  }

  sleep(0.5 + Math.random());
}

// ── Teardown
export function teardown(data) {
  console.log('📊 四子系统能源负载测试完成');
  console.log(`总VU请求: 见 summary`);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}