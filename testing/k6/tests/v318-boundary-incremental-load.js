/**
 * v3.18 六边界域架构增量测试 - k6性能测试
 * 覆盖范围：
 * 1. 碳认证API性能测试
 * 2. 有序充电API性能测试
 * 3. 微电网能耗报表API性能测试
 * 4. CIM协议API性能测试
 * 5. 组串监控API性能测试
 * 6. 备件核销API性能测试
 * 7. 六边界域服务监控API性能测试
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const carbonApiTrend = new Trend('carbon_api_duration');
const orderlyApiTrend = new Trend('orderly_api_duration');
const energyApiTrend = new Trend('energy_api_duration');
const cimApiTrend = new Trend('cim_api_duration');
const stringApiTrend = new Trend('string_api_duration');
const writeoffApiTrend = new Trend('writeoff_api_duration');
const serviceopsApiTrend = new Trend('serviceops_api_duration');

// 配置
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test_token';

export const options = {
  scenarios: {
    // 场景1: 碳认证API负载测试
    carbon_api: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
      exec: 'testCarbonApi',
    },
    // 场景2: 有序充电API负载测试
    orderly_api: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 15 },
        { duration: '1m', target: 30 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
      exec: 'testOrderlyApi',
    },
    // 场景3: 能耗报表API负载测试
    energy_api: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
      exec: 'testEnergyApi',
    },
    // 场景4: CIM协议API负载测试
    cim_api: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
      exec: 'testCimApi',
    },
    // 场景5: 组串监控API负载测试
    string_api: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
      exec: 'testStringApi',
    },
    // 场景6: 备件核销API负载测试
    writeoff_api: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
      exec: 'testWriteoffApi',
    },
    // 场景7: 服务监控API负载测试
    serviceops_api: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
      exec: 'testServiceOpsApi',
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<500'], // 95%请求响应时间<500ms
    'errors': ['rate<0.1'], // 错误率<10%
    'carbon_api_duration': ['p(95)<300'],
    'orderly_api_duration': ['p(95)<300'],
    'energy_api_duration': ['p(95)<400'],
    'cim_api_duration': ['p(95)<300'],
    'string_api_duration': ['p(95)<300'],
    'writeoff_api_duration': ['p(95)<300'],
    'serviceops_api_duration': ['p(95)<200'],
  },
};

const headers = {
  'Authorization': `Bearer ${AUTH_TOKEN}`,
  'Content-Type': 'application/json',
};

function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// ==================== 碳认证API性能测试 ====================
export function testCarbonApi() {
  group('碳认证API性能测试', function() {
    // I-REC证书列表
    let res = http.get(`${BASE_URL}/api/carbon/irec/certificates?page=1&pageSize=20`, { headers });
    carbonApiTrend.add(res.timings.duration);
    check(res, {
      'I-REC列表状态200': (r) => r.status === 200,
      'I-REC列表响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // CCER项目列表
    res = http.get(`${BASE_URL}/api/carbon/ccer/projects?page=1&pageSize=20`, { headers });
    carbonApiTrend.add(res.timings.duration);
    check(res, {
      'CCER列表状态200': (r) => r.status === 200,
      'CCER列表响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // I-REC设备注册 (模拟写入)
    const registerPayload = JSON.stringify({
      deviceName: `光伏电站-${uuid().substring(0, 8)}`,
      capacity: 10.5,
      location: '浙江省杭州市',
      commissionDate: '2024-01-15'
    });
    res = http.post(`${BASE_URL}/api/carbon/irec/register`, registerPayload, { headers });
    carbonApiTrend.add(res.timings.duration);
    check(res, {
      'I-REC注册状态200': (r) => r.status === 200,
      'I-REC注册响应<500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);

    sleep(1);
  });
}

// ==================== 有序充电API性能测试 ====================
export function testOrderlyApi() {
  group('有序充电API性能测试', function() {
    const stationId = uuid();
    
    // 获取排队列表
    let res = http.get(`${BASE_URL}/api/charging/orderly/${stationId}/queue`, { headers });
    orderlyApiTrend.add(res.timings.duration);
    check(res, {
      '排队列表状态200': (r) => r.status === 200,
      '排队列表响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // 获取充电桩负荷状态
    res = http.get(`${BASE_URL}/api/charging/orderly/${stationId}/pile-load`, { headers });
    orderlyApiTrend.add(res.timings.duration);
    check(res, {
      '负荷状态200': (r) => r.status === 200,
      '负荷响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // 提交排队请求
    const enqueuePayload = JSON.stringify({
      vehicleId: uuid(),
      stationId: stationId,
      soc: 25.5,
      targetSoc: 80.0,
      estimatedDuration: 60
    });
    res = http.post(`${BASE_URL}/api/charging/orderly/enqueue`, enqueuePayload, { headers });
    orderlyApiTrend.add(res.timings.duration);
    check(res, {
      '排队提交状态200': (r) => r.status === 200,
      '排队提交响应<500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);

    sleep(1);
  });
}

// ==================== 能耗报表API性能测试 ====================
export function testEnergyApi() {
  group('能耗报表API性能测试', function() {
    const gridId = uuid();
    const now = new Date();
    const startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString();
    const endDate = now.toISOString();
    
    // 获取能耗概览
    let res = http.get(`${BASE_URL}/api/microgrid/energy/overview?startDate=${startDate}&endDate=${endDate}`, { headers });
    energyApiTrend.add(res.timings.duration);
    check(res, {
      '能耗概览状态200': (r) => r.status === 200,
      '能耗概览响应<400ms': (r) => r.timings.duration < 400,
    }) || errorRate.add(1);

    sleep(0.5);

    // 获取日报表
    res = http.get(`${BASE_URL}/api/microgrid/energy/${gridId}/daily?date=${now.toISOString().split('T')[0]}`, { headers });
    energyApiTrend.add(res.timings.duration);
    check(res, {
      '日报表状态200': (r) => r.status === 200,
      '日报表响应<400ms': (r) => r.timings.duration < 400,
    }) || errorRate.add(1);

    sleep(0.5);

    // 获取月报表
    res = http.get(`${BASE_URL}/api/microgrid/energy/${gridId}/monthly?year=2026&month=3`, { headers });
    energyApiTrend.add(res.timings.duration);
    check(res, {
      '月报表状态200': (r) => r.status === 200,
      '月报表响应<400ms': (r) => r.timings.duration < 400,
    }) || errorRate.add(1);

    sleep(1);
  });
}

// ==================== CIM协议API性能测试 ====================
export function testCimApi() {
  group('CIM协议API性能测试', function() {
    // 获取CIM配置
    let res = http.get(`${BASE_URL}/api/orchestrator/cim/config`, { headers });
    cimApiTrend.add(res.timings.duration);
    check(res, {
      'CIM配置状态200': (r) => r.status === 200,
      'CIM配置响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // 获取调度记录
    res = http.get(`${BASE_URL}/api/orchestrator/cim/dispatch/records?page=1&pageSize=20`, { headers });
    cimApiTrend.add(res.timings.duration);
    check(res, {
      '调度记录状态200': (r) => r.status === 200,
      '调度记录响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // 接收调度指令 (模拟写入)
    const dispatchPayload = JSON.stringify({
      commandId: uuid(),
      type: 'EndDeviceControl',
      targetPower: 5000,
      duration: 3600
    });
    res = http.post(`${BASE_URL}/api/orchestrator/cim/dispatch/receive`, dispatchPayload, { headers });
    cimApiTrend.add(res.timings.duration);
    check(res, {
      '接收调度状态200': (r) => r.status === 200,
      '接收调度响应<500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);

    sleep(1);
  });
}

// ==================== 组串监控API性能测试 ====================
export function testStringApi() {
  group('组串监控API性能测试', function() {
    const inverterId = uuid();
    
    // 获取组串状态
    let res = http.get(`${BASE_URL}/api/pvessc/string/${inverterId}/strings`, { headers });
    stringApiTrend.add(res.timings.duration);
    check(res, {
      '组串状态200': (r) => r.status === 200,
      '组串状态响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // 获取组串异常
    res = http.get(`${BASE_URL}/api/pvessc/string/${inverterId}/anomalies`, { headers });
    stringApiTrend.add(res.timings.duration);
    check(res, {
      '组串异常状态200': (r) => r.status === 200,
      '组串异常响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // 记录组串数据 (模拟写入)
    const dataPayload = JSON.stringify({
      inverterId: inverterId,
      stringId: 'S001',
      timestamp: new Date().toISOString(),
      current: 8.5,
      voltage: 650,
      power: 5525
    });
    res = http.post(`${BASE_URL}/api/pvessc/string/data`, dataPayload, { headers });
    stringApiTrend.add(res.timings.duration);
    check(res, {
      '记录数据状态200': (r) => r.status === 200,
      '记录数据响应<500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);

    sleep(1);
  });
}

// ==================== 备件核销API性能测试 ====================
export function testWriteoffApi() {
  group('备件核销API性能测试', function() {
    // 获取核销单列表
    let res = http.get(`${BASE_URL}/api/workorder/sparepart/writeoff?page=1&pageSize=20`, { headers });
    writeoffApiTrend.add(res.timings.duration);
    check(res, {
      '核销单列表状态200': (r) => r.status === 200,
      '核销单列表响应<300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);

    sleep(0.5);

    // 创建核销单 (模拟写入)
    const writeoffPayload = JSON.stringify({
      workOrderId: uuid(),
      items: [
        { partId: uuid(), quantity: 2, reason: '更换损坏配件' }
      ]
    });
    res = http.post(`${BASE_URL}/api/workorder/sparepart/writeoff`, writeoffPayload, { headers });
    writeoffApiTrend.add(res.timings.duration);
    check(res, {
      '创建核销单状态200': (r) => r.status === 200,
      '创建核销单响应<500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);

    sleep(1);
  });
}

// ==================== 服务监控API性能测试 ====================
export function testServiceOpsApi() {
  group('服务监控API性能测试', function() {
    // 获取服务列表
    let res = http.get(`${BASE_URL}/api/serviceops/services`, { headers });
    serviceopsApiTrend.add(res.timings.duration);
    check(res, {
      '服务列表状态200': (r) => r.status === 200,
      '服务列表响应<200ms': (r) => r.timings.duration < 200,
    }) || errorRate.add(1);

    sleep(0.5);

    // 获取边界域分组
    res = http.get(`${BASE_URL}/api/serviceops/groups`, { headers });
    serviceopsApiTrend.add(res.timings.duration);
    check(res, {
      '边界域分组状态200': (r) => r.status === 200,
      '边界域分组响应<200ms': (r) => r.timings.duration < 200,
    }) || errorRate.add(1);

    sleep(0.5);

    // 按边界域筛选服务
    const groups = ['platform', 'shared', 'charging', 'energy-core', 'energy-trade', 'intelligent'];
    const randomGroup = groups[Math.floor(Math.random() * groups.length)];
    res = http.get(`${BASE_URL}/api/serviceops/groups/${randomGroup}/services`, { headers });
    serviceopsApiTrend.add(res.timings.duration);
    check(res, {
      '域服务列表状态200': (r) => r.status === 200,
      '域服务列表响应<200ms': (r) => r.timings.duration < 200,
    }) || errorRate.add(1);

    sleep(1);
  });
}

// ==================== 默认执行函数 ====================
export default function() {
  testCarbonApi();
  testOrderlyApi();
  testEnergyApi();
  testCimApi();
  testStringApi();
  testWriteoffApi();
  testServiceOpsApi();
}
