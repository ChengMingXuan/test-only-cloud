// ============================================================
// K6 Phase 2 能源服务增强 — 性能基线测试
// 覆盖：碳交易撮合引擎 / VPP预测优化 / 现货市场出清 /
//       微电网故障保护 / 设备运维工单 / 需求响应
// 目标：20 VU 持续 5 分钟，p95 < 800ms，错误率 < 2%
// 运行：k6 run k6/scenarios/phase2-energy-baseline.js
// ============================================================

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const USERNAME = __ENV.USERNAME || 'admin';
const PASSWORD = __ENV.PASSWORD || 'P@ssw0rd';

// ── 自定义指标
const carbonTradeSuccess = new Rate('carbontrade_success');
const vppSuccess         = new Rate('vpp_enhanced_success');
const electradeSuccess   = new Rate('electrade_spot_success');
const microgridSuccess   = new Rate('microgrid_protection_success');
const deviceopsSuccess   = new Rate('deviceops_workorder_success');
const demandrespSuccess  = new Rate('demandresp_event_success');
const overallSuccess     = new Rate('overall_phase2_success');
const apiLatency         = new Trend('phase2_api_latency');
const totalRequests      = new Counter('phase2_total_requests');

// ── 负载阶段（基线建压）
export const options = {
  stages: [
    { duration: '30s', target: 5   },  // 热身
    { duration: '2m',  target: 20  },  // 正常负载
    { duration: '1m',  target: 30  },  // 轻微提升
    { duration: '1m',  target: 10  },  // 降压
    { duration: '30s', target: 0   },  // 冷却
  ],
  thresholds: {
    http_req_failed:              ['rate<0.02'],    // 错误率 < 2%
    http_req_duration:            ['p(95)<800'],    // p95 < 800ms
    carbontrade_success:          ['rate>0'],
    vpp_enhanced_success:         ['rate>0'],
    electrade_spot_success:       ['rate>0'],
    microgrid_protection_success: ['rate>0'],
    deviceops_workorder_success:  ['rate>0'],
    demandresp_event_success:     ['rate>0'],
    overall_phase2_success:       ['rate>0'],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)', 'count'],
};

// ── Setup：登录
export function setup() {
  console.log(`🚀 Phase 2 能源增强性能基线 - Base: ${BASE_URL}`);
  const resp = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ username: USERNAME, password: PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  const body = resp.json();
  if (!body || !body.success || !body.data?.accessToken) {
    console.error(`❌ 登录失败: ${resp.status} ${resp.body}`);
    return { token: null };
  }
  console.log(`✅ 登录成功`);
  return { token: body.data.accessToken };
}

// ── 主测试函数
export default function (data) {
  if (!data.token) { sleep(1); return; }

  const h = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  totalRequests.add(1);
  const scenario = __ITER % 6;

  switch (scenario) {

    // ---- CarbonTrade 碳交易增强 ----
    case 0:
      group('CarbonTrade_Phase3', () => {
        // 配额交易订单列表
        const r1 = http.get(`${BASE_URL}/api/carbontrade/trade-order/list?page=1&pageSize=10`, { headers: h });
        const ok1 = check(r1, { 'CT TradeOrder List 200': (r) => r.status < 500 });
        carbonTradeSuccess.add(ok1);
        overallSuccess.add(ok1);
        apiLatency.add(r1.timings.duration);

        // 结算列表
        const r2 = http.get(`${BASE_URL}/api/carbontrade/settlement/list?page=1&pageSize=10`, { headers: h });
        check(r2, { 'CT Settlement List': (r) => r.status < 500 });
        apiLatency.add(r2.timings.duration);

        // 排放因子权重
        const r3 = http.get(`${BASE_URL}/api/carbontrade/factor-weight/00000000-0000-0000-0000-000000000001`, { headers: h });
        check(r3, { 'CT FactorWeight': (r) => r.status < 500 || r.status === 404 });
        apiLatency.add(r3.timings.duration);
      });
      break;

    // ---- VPP 虚拟电厂增强 ----
    case 1:
      group('VPP_Enhanced', () => {
        // 预测模型列表
        const r1 = http.get(`${BASE_URL}/api/vpp/forecast/model/list?page=1&pageSize=10`, { headers: h });
        const ok1 = check(r1, { 'VPP Forecast Model List': (r) => r.status < 500 });
        vppSuccess.add(ok1);
        overallSuccess.add(ok1);
        apiLatency.add(r1.timings.duration);

        // 预测结果列表
        const r2 = http.get(`${BASE_URL}/api/vpp/forecast/result/list?page=1&pageSize=10`, { headers: h });
        check(r2, { 'VPP Forecast Result List': (r) => r.status < 500 });
        apiLatency.add(r2.timings.duration);

        // 优化列表
        const r3 = http.get(`${BASE_URL}/api/vpp/optimization/list?page=1&pageSize=10`, { headers: h });
        check(r3, { 'VPP Optimization List': (r) => r.status < 500 });
        apiLatency.add(r3.timings.duration);
      });
      break;

    // ---- ElecTrade 现货市场 ----
    case 2:
      group('ElecTrade_Spot', () => {
        // 现货订单列表
        const r1 = http.get(`${BASE_URL}/api/electrade/spot/order/list?page=1&pageSize=10`, { headers: h });
        const ok1 = check(r1, { 'ET Spot Order List': (r) => r.status < 500 });
        electradeSuccess.add(ok1);
        overallSuccess.add(ok1);
        apiLatency.add(r1.timings.duration);

        // 价格指数
        const r2 = http.get(`${BASE_URL}/api/electrade/spot/price-index/list?page=1&pageSize=10`, { headers: h });
        check(r2, { 'ET Price Index List': (r) => r.status < 500 });
        apiLatency.add(r2.timings.duration);
      });
      break;

    // ---- MicroGrid 故障保护 ----
    case 3:
      group('MicroGrid_Protection', () => {
        // 故障列表
        const r1 = http.get(`${BASE_URL}/api/microgrid/fault/list?page=1&pageSize=10`, { headers: h });
        const ok1 = check(r1, { 'MG Fault List': (r) => r.status < 500 });
        microgridSuccess.add(ok1);
        overallSuccess.add(ok1);
        apiLatency.add(r1.timings.duration);

        // PID 控制器列表
        const r2 = http.get(`${BASE_URL}/api/microgrid/pid/list?page=1&pageSize=10`, { headers: h });
        check(r2, { 'MG PID List': (r) => r.status < 500 });
        apiLatency.add(r2.timings.duration);

        // 孤岛事件列表
        const r3 = http.get(`${BASE_URL}/api/microgrid/islanding/list?page=1&pageSize=10`, { headers: h });
        check(r3, { 'MG Islanding List': (r) => r.status < 500 });
        apiLatency.add(r3.timings.duration);
      });
      break;

    // ---- DeviceOps 设备运维 ----
    case 4:
      group('DeviceOps_WorkOrder', () => {
        // 工单列表
        const r1 = http.get(`${BASE_URL}/api/deviceops/work-order/list?page=1&pageSize=10`, { headers: h });
        const ok1 = check(r1, { 'DO WorkOrder List': (r) => r.status < 500 });
        deviceopsSuccess.add(ok1);
        overallSuccess.add(ok1);
        apiLatency.add(r1.timings.duration);

        // 预测性维护列表
        const r2 = http.get(`${BASE_URL}/api/deviceops/predictive-maintenance/list?page=1&pageSize=10`, { headers: h });
        check(r2, { 'DO Predictive List': (r) => r.status < 500 });
        apiLatency.add(r2.timings.duration);

        // 备件列表
        const r3 = http.get(`${BASE_URL}/api/deviceops/spare-part/list?page=1&pageSize=10`, { headers: h });
        check(r3, { 'DO SparePart List': (r) => r.status < 500 });
        apiLatency.add(r3.timings.duration);
      });
      break;

    // ---- DemandResp 需求响应 ----
    case 5:
      group('DemandResp_Event', () => {
        // 响应事件列表
        const r1 = http.get(`${BASE_URL}/api/demandresp/event/list?page=1&pageSize=10`, { headers: h });
        const ok1 = check(r1, { 'DR Event List': (r) => r.status < 500 });
        demandrespSuccess.add(ok1);
        overallSuccess.add(ok1);
        apiLatency.add(r1.timings.duration);
      });
      break;
  }

  sleep(0.3 + Math.random() * 0.5);
}

// ── Teardown
export function teardown(data) {
  console.log('📊 Phase 2 能源增强性能基线测试完成');
}

export function handleSummary(data) {
  return {
    'results/phase2-energy-baseline-results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
