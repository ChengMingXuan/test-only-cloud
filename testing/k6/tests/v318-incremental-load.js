/**
 * v3.18 增量功能 - k6 性能负载测试
 * ==================================
 * 测试新增 API 的性能基准：
 * - 碳认证 API 吞吐量
 * - 智能排队充电 API 响应时间
 * - 能耗报表 API 并发能力
 * - CIM调度 API 稳定性
 * - 组串监控 API 延迟
 * - AI 预测 API 性能
 * - Agent 执行 API 负载
 * - 设备健康 API 批量能力
 * - 第三方模型 API 限流
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ═══════════════════════════════════════════════════════════════════════════════
// 自定义指标
// ═══════════════════════════════════════════════════════════════════════════════

const errorRate = new Rate('errors');
const carbonApiTrend = new Trend('carbon_api_duration');
const chargingApiTrend = new Trend('charging_api_duration');
const energyApiTrend = new Trend('energy_api_duration');
const cimApiTrend = new Trend('cim_api_duration');
const stringApiTrend = new Trend('string_api_duration');
const aiPredictTrend = new Trend('ai_predict_duration');
const agentTrend = new Trend('agent_execution_duration');
const healthTrend = new Trend('health_assessment_duration');
const thirdPartyTrend = new Trend('third_party_chat_duration');
const apiCallCounter = new Counter('api_calls');

// ═══════════════════════════════════════════════════════════════════════════════
// 测试配置
// ═══════════════════════════════════════════════════════════════════════════════

export const options = {
  scenarios: {
    // 场景1: 烟雾测试 - 基础功能验证
    smoke_test: {
      executor: 'constant-vus',
      vus: 1,
      duration: '30s',
      tags: { type: 'smoke' },
    },
    // 场景2: 负载测试 - 逐步增压
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
      ],
      tags: { type: 'load' },
      startTime: '35s',
    },
    // 场景3: 压力测试 - 极限并发
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
      ],
      tags: { type: 'stress' },
      startTime: '3m',
    },
    // 场景4: 峰值测试 - 突发流量
    spike_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 100 },
        { duration: '1m', target: 100 },
        { duration: '10s', target: 0 },
      ],
      tags: { type: 'spike' },
      startTime: '6m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<3000', 'p(99)<5000'],  // 95%请求<3s, 99%<5s
    errors: ['rate<0.1'],                              // 错误率<10%
    carbon_api_duration: ['p(95)<2000'],
    charging_api_duration: ['p(95)<1500'],
    energy_api_duration: ['p(95)<2500'],
    cim_api_duration: ['p(95)<3000'],
    string_api_duration: ['p(95)<2000'],
    ai_predict_duration: ['p(95)<5000'],               // AI预测允许较长时间
    agent_execution_duration: ['p(95)<10000'],         // Agent执行时间较长
    health_assessment_duration: ['p(95)<3000'],
    third_party_chat_duration: ['p(95)<8000'],         // 第三方API可能较慢
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// 环境配置
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test_token';

const defaultHeaders = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${AUTH_TOKEN}`,
  'X-Tenant-Id': '00000000-0000-0000-0000-000000000001',
};

// ═══════════════════════════════════════════════════════════════════════════════
// 工具函数
// ═══════════════════════════════════════════════════════════════════════════════

function recordMetric(trend, response) {
  trend.add(response.timings.duration);
  apiCallCounter.add(1);
  errorRate.add(response.status >= 400);
}

function checkResponse(response, name) {
  return check(response, {
    [`${name} status is 200`]: (r) => r.status === 200,
    [`${name} response time < 3s`]: (r) => r.timings.duration < 3000,
    [`${name} has body`]: (r) => r.body && r.body.length > 0,
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 1. 碳认证 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testCarbonCertificationApi() {
  group('碳认证 API', () => {
    // 1.1 获取I-REC证书列表
    const listRes = http.get(`${BASE_URL}/api/carbon/irec/certificates?page=1&pageSize=20`, {
      headers: defaultHeaders,
    });
    recordMetric(carbonApiTrend, listRes);
    checkResponse(listRes, 'I-REC证书列表');

    // 1.2 注册设备
    const registerPayload = JSON.stringify({
      deviceCode: `PV-${Date.now()}`,
      facilityName: '测试光伏电站',
      capacityKw: 10000,
      installDate: '2025-01-01',
    });
    const registerRes = http.post(`${BASE_URL}/api/carbon/irec/register`, registerPayload, {
      headers: defaultHeaders,
    });
    recordMetric(carbonApiTrend, registerRes);
    checkResponse(registerRes, 'I-REC设备注册');

    // 1.3 获取CCER项目列表
    const ccerRes = http.get(`${BASE_URL}/api/carbon/ccer/projects?status=all`, {
      headers: defaultHeaders,
    });
    recordMetric(carbonApiTrend, ccerRes);
    checkResponse(ccerRes, 'CCER项目列表');

    sleep(0.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 2. 智能排队充电 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testOrderlyChargingApi() {
  group('智能排队充电 API', () => {
    const stationId = 'station-perf-001';

    // 2.1 提交排队
    const enqueuePayload = JSON.stringify({
      stationId: stationId,
      vehicleId: `京A${Math.floor(Math.random() * 90000) + 10000}`,
      currentSocPercent: Math.floor(Math.random() * 50) + 10,
      targetSocPercent: 90,
      estimatedKwh: 40,
    });
    const enqueueRes = http.post(`${BASE_URL}/api/charging/orderly/enqueue`, enqueuePayload, {
      headers: defaultHeaders,
    });
    recordMetric(chargingApiTrend, enqueueRes);
    checkResponse(enqueueRes, '排队提交');

    // 2.2 获取排队状态
    const queueRes = http.get(`${BASE_URL}/api/charging/orderly/${stationId}/queue`, {
      headers: defaultHeaders,
    });
    recordMetric(chargingApiTrend, queueRes);
    checkResponse(queueRes, '排队状态');

    // 2.3 执行调度
    const dispatchRes = http.post(`${BASE_URL}/api/charging/orderly/${stationId}/dispatch`, null, {
      headers: defaultHeaders,
    });
    recordMetric(chargingApiTrend, dispatchRes);
    checkResponse(dispatchRes, '调度执行');

    sleep(0.3);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 3. 能耗报表 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testEnergyReportApi() {
  group('能耗报表 API', () => {
    const gridId = 'grid-perf-001';

    // 3.1 获取概览
    const overviewRes = http.get(`${BASE_URL}/api/microgrid/energy/overview?startDate=2025-03-01&endDate=2025-03-18`, {
      headers: defaultHeaders,
    });
    recordMetric(energyApiTrend, overviewRes);
    checkResponse(overviewRes, '能耗概览');

    // 3.2 获取日报
    const dailyRes = http.get(`${BASE_URL}/api/microgrid/energy/${gridId}/daily?date=2025-03-18`, {
      headers: defaultHeaders,
    });
    recordMetric(energyApiTrend, dailyRes);
    checkResponse(dailyRes, '日报数据');

    // 3.3 获取月报
    const monthlyRes = http.get(`${BASE_URL}/api/microgrid/energy/${gridId}/monthly?year=2025&month=3`, {
      headers: defaultHeaders,
    });
    recordMetric(energyApiTrend, monthlyRes);
    checkResponse(monthlyRes, '月报数据');

    // 3.4 对比分析
    const compareRes = http.post(`${BASE_URL}/api/microgrid/energy/compare`, JSON.stringify({
      gridIds: [gridId, 'grid-perf-002'],
      startDate: '2025-03-01',
      endDate: '2025-03-18',
    }), {
      headers: defaultHeaders,
    });
    recordMetric(energyApiTrend, compareRes);
    checkResponse(compareRes, '对比分析');

    sleep(0.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 4. CIM调度 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testCimDispatchApi() {
  group('CIM调度 API', () => {
    // 4.1 获取配置
    const configRes = http.get(`${BASE_URL}/api/orchestrator/cim/config`, {
      headers: defaultHeaders,
    });
    recordMetric(cimApiTrend, configRes);
    checkResponse(configRes, 'CIM配置');

    // 4.2 获取调度记录
    const recordsRes = http.get(`${BASE_URL}/api/orchestrator/cim/dispatch/records?page=1&pageSize=20`, {
      headers: defaultHeaders,
    });
    recordMetric(cimApiTrend, recordsRes);
    checkResponse(recordsRes, '调度记录');

    // 4.3 发送调度指令
    const dispatchPayload = JSON.stringify({
      commandType: 'EndDeviceControl',
      deviceIds: ['device-001', 'device-002'],
      action: 'set_power',
      value: 50,
    });
    const dispatchRes = http.post(`${BASE_URL}/api/orchestrator/cim/dispatch`, dispatchPayload, {
      headers: defaultHeaders,
    });
    recordMetric(cimApiTrend, dispatchRes);
    checkResponse(dispatchRes, '发送调度指令');

    sleep(0.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 5. 组串监控 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testStringMonitorApi() {
  group('组串监控 API', () => {
    const siteId = 'site-perf-001';

    // 5.1 执行异常检测
    const detectRes = http.post(`${BASE_URL}/api/pvessc/string-monitor/${siteId}/detect`, null, {
      headers: defaultHeaders,
    });
    recordMetric(stringApiTrend, detectRes);
    checkResponse(detectRes, '异常检测');

    // 5.2 获取热斑分析
    const hotspotRes = http.get(`${BASE_URL}/api/pvessc/string-monitor/${siteId}/hotspot-analysis`, {
      headers: defaultHeaders,
    });
    recordMetric(stringApiTrend, hotspotRes);
    checkResponse(hotspotRes, '热斑分析');

    // 5.3 获取异常列表
    const anomaliesRes = http.get(`${BASE_URL}/api/pvessc/string-monitor/anomalies?page=1&pageSize=50`, {
      headers: defaultHeaders,
    });
    recordMetric(stringApiTrend, anomaliesRes);
    checkResponse(anomaliesRes, '异常列表');

    sleep(0.3);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 6. AI 预测 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testAiPredictApi() {
  group('AI 预测 API', () => {
    // 6.1 执行预测
    const predictPayload = JSON.stringify({
      scenarioType: 'pv_generation',
      stationId: 'station-001',
      horizon: 24,
      historicalData: Array(168).fill(0).map(() => Math.random() * 1000),
    });
    const predictRes = http.post(`${BASE_URL}/api/iotcloudai/adaptive/predict`, predictPayload, {
      headers: defaultHeaders,
    });
    recordMetric(aiPredictTrend, predictRes);
    checkResponse(predictRes, 'AI预测');

    // 6.2 获取模型列表
    const modelsRes = http.get(`${BASE_URL}/api/iotcloudai/adaptive/models?scenarioType=pv_generation`, {
      headers: defaultHeaders,
    });
    recordMetric(aiPredictTrend, modelsRes);
    checkResponse(modelsRes, '模型列表');

    // 6.3 提交性能反馈
    const feedbackPayload = JSON.stringify({
      modelId: 'lstm-v1',
      predictionId: 'pred-001',
      actualValues: [100, 150, 200],
    });
    const feedbackRes = http.post(`${BASE_URL}/api/iotcloudai/adaptive/performance`, feedbackPayload, {
      headers: defaultHeaders,
    });
    recordMetric(aiPredictTrend, feedbackRes);
    checkResponse(feedbackRes, '性能反馈');

    sleep(1);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 7. Agent 执行 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testAgentExecutionApi() {
  group('Agent 执行 API', () => {
    // 7.1 执行Agent任务
    const executePayload = JSON.stringify({
      agentId: 'daily_ops',
      goal: '分析今日充电站运营情况',
      context: { date: '2025-03-18' },
    });
    const executeRes = http.post(`${BASE_URL}/api/iotcloudai/agent/execute`, executePayload, {
      headers: defaultHeaders,
    });
    recordMetric(agentTrend, executeRes);
    checkResponse(executeRes, 'Agent执行');

    // 7.2 获取Agent列表
    const agentsRes = http.get(`${BASE_URL}/api/iotcloudai/agent/agents`, {
      headers: defaultHeaders,
    });
    recordMetric(agentTrend, agentsRes);
    checkResponse(agentsRes, 'Agent列表');

    // 7.3 获取执行历史
    const historyRes = http.get(`${BASE_URL}/api/iotcloudai/agent/history?limit=20`, {
      headers: defaultHeaders,
    });
    recordMetric(agentTrend, historyRes);
    checkResponse(historyRes, '执行历史');

    sleep(1.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 8. 设备健康 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testDeviceHealthApi() {
  group('设备健康 API', () => {
    const deviceId = 'device-perf-001';

    // 8.1 单台设备评估
    const assessPayload = JSON.stringify({
      deviceId: deviceId,
      deviceType: 'inverter',
      data: {
        temperature: 45,
        efficiency: 0.95,
        uptime: 8760,
      },
    });
    const assessRes = http.post(`${BASE_URL}/api/iotcloudai/health/assess`, assessPayload, {
      headers: defaultHeaders,
    });
    recordMetric(healthTrend, assessRes);
    checkResponse(assessRes, '单台评估');

    // 8.2 批量评估
    const batchPayload = JSON.stringify({
      devices: Array(10).fill(null).map((_, i) => ({
        deviceId: `device-batch-${i}`,
        deviceType: 'inverter',
        data: { temperature: 40 + Math.random() * 20, efficiency: 0.9 + Math.random() * 0.1 },
      })),
    });
    const batchRes = http.post(`${BASE_URL}/api/iotcloudai/health/assess/batch`, batchPayload, {
      headers: defaultHeaders,
    });
    recordMetric(healthTrend, batchRes);
    checkResponse(batchRes, '批量评估');

    // 8.3 获取健康趋势
    const trendRes = http.get(`${BASE_URL}/api/iotcloudai/health/trend/${deviceId}?days=30`, {
      headers: defaultHeaders,
    });
    recordMetric(healthTrend, trendRes);
    checkResponse(trendRes, '健康趋势');

    sleep(0.5);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 9. 第三方模型 API 性能测试
// ═══════════════════════════════════════════════════════════════════════════════

function testThirdPartyModelApi() {
  group('第三方模型 API', () => {
    // 9.1 发送对话
    const chatPayload = JSON.stringify({
      provider: 'ali',
      message: '请分析光储充一体化系统的优化策略',
      options: { temperature: 0.7, maxTokens: 1024 },
    });
    const chatRes = http.post(`${BASE_URL}/api/iotcloudai/third-party/chat`, chatPayload, {
      headers: defaultHeaders,
    });
    recordMetric(thirdPartyTrend, chatRes);
    checkResponse(chatRes, '对话请求');

    // 9.2 获取供应商列表
    const providersRes = http.get(`${BASE_URL}/api/iotcloudai/third-party/providers`, {
      headers: defaultHeaders,
    });
    recordMetric(thirdPartyTrend, providersRes);
    checkResponse(providersRes, '供应商列表');

    // 9.3 健康检查
    const healthRes = http.get(`${BASE_URL}/api/iotcloudai/third-party/health`, {
      headers: defaultHeaders,
    });
    recordMetric(thirdPartyTrend, healthRes);
    checkResponse(healthRes, '健康检查');

    sleep(2);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 主测试函数
// ═══════════════════════════════════════════════════════════════════════════════

export default function () {
  // 随机选择测试组执行，模拟真实用户行为
  const testGroups = [
    testCarbonCertificationApi,
    testOrderlyChargingApi,
    testEnergyReportApi,
    testCimDispatchApi,
    testStringMonitorApi,
    testAiPredictApi,
    testAgentExecutionApi,
    testDeviceHealthApi,
    testThirdPartyModelApi,
  ];

  // 每次迭代执行所有测试组
  testGroups.forEach(testFn => {
    try {
      testFn();
    } catch (e) {
      console.error(`Test error: ${e}`);
      errorRate.add(1);
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 测试生命周期钩子
// ═══════════════════════════════════════════════════════════════════════════════

export function setup() {
  console.log('╔══════════════════════════════════════════════════════════════════╗');
  console.log('║       v3.18 增量功能 - k6 性能负载测试                          ║');
  console.log('║       测试 9 个新增 API 模块的性能基准                          ║');
  console.log('╚══════════════════════════════════════════════════════════════════╝');
  
  // 验证服务可用
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    console.warn(`服务健康检查失败: ${healthCheck.status}`);
  }
  
  return { startTime: new Date().toISOString() };
}

export function teardown(data) {
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log(`测试结束: ${new Date().toISOString()}`);
  console.log(`开始时间: ${data.startTime}`);
  console.log('═══════════════════════════════════════════════════════════════════');
}
