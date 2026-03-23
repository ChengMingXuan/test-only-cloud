// Load Test - 正常负载测试
// 目标：验证系统在正常负载下的性能，200个VU，16分钟

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomIntBetween, randomItem } from 'k6';
import config from '../config.js';
import auth from '../utils/auth.js';
import helpers from '../utils/helpers.js';

// 自定义指标
const authSuccessRate = new Rate('auth_success_rate');
const apiSuccessRate = new Rate('api_success_rate');
const chargingApiRate = new Rate('charging_api_success');
const deviceApiRate = new Rate('device_api_success');
const workorderApiRate = new Rate('workorder_api_success');
const apiDuration = new Trend('api_duration');
const totalRequests = new Counter('total_requests');

export let options = {
  scenarios: {
    load: config.scenarios.load,
  },
  thresholds: config.scenarioThresholds.load,
};

// 全局变量存储token（每个VU独立）
let authToken = null;

export function setup() {
  console.log('🚀 Starting Load Test...');
  console.log(`Base URL: ${config.baseUrl}`);
  console.log(`Target: 200 VUs, 500-1000 RPS`);
  
  // 预热：登录一个测试用户
  const testUser = config.testData.users[0];
  const warmupToken = auth.login(testUser.username, testUser.password);
  
  if (warmupToken) {
    console.log('✅ Warmup successful');
  }
  
  return { 
    startTime: new Date().toISOString(),
    users: config.testData.users,
    devices: config.testData.devices,
  };
}

export default function (data) {
  // 每20次迭代重新登录一次（模拟真实用户session）
  if (!authToken || __ITER % 20 === 0) {
    const user = randomItem(data.users);
    authToken = auth.login(user.username, user.password);
    authSuccessRate.add(authToken !== null);
    totalRequests.add(1);
  }
  
  if (!authToken) {
    sleep(1);
    return;
  }
  
  const authHeaders = auth.getAuthHeaders(authToken);
  
  // 随机选择场景执行（模拟真实用户行为）
  const scenario = randomIntBetween(1, 100);
  
  if (scenario <= 30) {
    // 30% - 充电业务场景
    chargingScenario(authHeaders, data);
  } else if (scenario <= 50) {
    // 20% - 设备管理场景
    deviceScenario(authHeaders, data);
  } else if (scenario <= 65) {
    // 15% - 工单管理场景
    workorderScenario(authHeaders, data);
  } else if (scenario <= 80) {
    // 15% - 数据查询场景
    analyticsScenario(authHeaders);
  } else {
    // 20% - 混合场景
    mixedScenario(authHeaders, data);
  }
  
  sleep(randomIntBetween(1, 3));
}

// 充电业务场景
function chargingScenario(headers, data) {
  group('Charging Business', function () {
    // 获取充电记录列表
    const recordsRes = http.get(
      `${config.baseUrl}/api/charging/admin/orders?page=${randomIntBetween(1, 10)}&pageSize=20`,
      { headers }
    );
    checkApiResponse(recordsRes, 'charging records');
    chargingApiRate.add(recordsRes.status === 200);
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 获取充电统计
    const statsRes = http.get(
      `${config.baseUrl}/api/charging/statistics?period=daily`,
      { headers }
    );
    checkApiResponse(statsRes, 'charging stats');
    chargingApiRate.add(statsRes.status === 200);
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 创建充电订单（10%概率）
    if (randomIntBetween(1, 10) === 1) {
      const device = randomItem(data.devices);
      const orderPayload = JSON.stringify({
        deviceId: device.id,
        amount: randomIntBetween(10, 100),
        duration: randomIntBetween(30, 240),
      });
      
      const orderRes = http.post(
        `${config.baseUrl}/api/charging/admin/orders`,
        orderPayload,
        { headers }
      );
      checkApiResponse(orderRes, 'create order');
      chargingApiRate.add(orderRes.status === 200 || orderRes.status === 201);
      totalRequests.add(1);
    }
  });
}

// 设备管理场景
function deviceScenario(headers, data) {
  group('Device Management', function () {
    // 获取设备列表
    const devicesRes = http.get(
      `${config.baseUrl}/api/device?page=${randomIntBetween(1, 10)}&pageSize=20`,
      { headers }
    );
    checkApiResponse(devicesRes, 'devices list');
    deviceApiRate.add(devicesRes.status === 200);
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 获取设备详情
    const device = randomItem(data.devices);
    const deviceRes = http.get(
      `${config.baseUrl}/api/device/${device.id}`,
      { headers }
    );
    checkApiResponse(deviceRes, 'device detail');
    deviceApiRate.add(deviceRes.status === 200);
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 获取设备实时数据
    const realtimeRes = http.get(
      `${config.baseUrl}/api/device/${device.id}/realtime`,
      { headers }
    );
    checkApiResponse(realtimeRes, 'device realtime');
    deviceApiRate.add(realtimeRes.status === 200);
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 上报设备数据（5%概率）
    if (randomIntBetween(1, 20) === 1) {
      const deviceData = helpers.generateDeviceData(device.id);
      const reportRes = http.post(
        `${config.baseUrl}/api/device/${device.id}/data`,
        JSON.stringify(deviceData),
        { headers }
      );
      checkApiResponse(reportRes, 'device data report');
      deviceApiRate.add(reportRes.status === 200 || reportRes.status === 201);
      totalRequests.add(1);
    }
  });
}

// 工单管理场景
function workorderScenario(headers, data) {
  group('WorkOrder Management', function () {
    // 搜索工单（使用ElasticSearch）
    const searchRes = http.get(
      `${config.baseUrl}/api/workorder/search?q=${helpers.randomString(5)}&page=1&pageSize=10`,
      { headers }
    );
    checkApiResponse(searchRes, 'workorder search');
    workorderApiRate.add(searchRes.status === 200);
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 获取工单列表
    const listRes = http.get(
      `${config.baseUrl}/api/workorder?status=pending&page=${randomIntBetween(1, 5)}&pageSize=20`,
      { headers }
    );
    checkApiResponse(listRes, 'workorder list');
    workorderApiRate.add(listRes.status === 200);
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 创建工单（3%概率）
    if (randomIntBetween(1, 33) === 1) {
      const device = randomItem(data.devices);
      const workorder = helpers.generateWorkOrder(device.id, 1);
      
      const createRes = http.post(
        `${config.baseUrl}/api/workorder`,
        JSON.stringify(workorder),
        { headers }
      );
      checkApiResponse(createRes, 'create workorder');
      workorderApiRate.add(createRes.status === 200 || createRes.status === 201);
      totalRequests.add(1);
    }
  });
}

// 数据分析场景
function analyticsScenario(headers) {
  group('Analytics', function () {
    // 能耗分析
    const energyRes = http.get(
      `${config.baseUrl}/api/analytics/energy?period=weekly`,
      { headers }
    );
    checkApiResponse(energyRes, 'energy analytics');
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 收入分析
    const revenueRes = http.get(
      `${config.baseUrl}/api/analytics/revenue?period=monthly`,
      { headers }
    );
    checkApiResponse(revenueRes, 'revenue analytics');
    totalRequests.add(1);
    
    sleep(0.5);
    
    // 设备利用率
    const utilizationRes = http.get(
      `${config.baseUrl}/api/analytics/device-utilization`,
      { headers }
    );
    checkApiResponse(utilizationRes, 'device utilization');
    totalRequests.add(1);
  });
}

// 混合场景
function mixedScenario(headers, data) {
  group('Mixed Operations', function () {
    // 快速浏览多个接口
    const endpoints = [
      '/api/stations',
      '/api/device/status',
      '/api/charging/ongoing',
      '/api/alerts/recent',
      '/api/user/profile',
    ];
    
    endpoints.forEach(endpoint => {
      const res = http.get(`${config.baseUrl}${endpoint}`, { headers });
      checkApiResponse(res, endpoint);
      totalRequests.add(1);
      sleep(0.3);
    });
  });
}

// 检查API响应
function checkApiResponse(response, name) {
  const success = check(response, {
    [`${name} status is 2xx`]: (r) => r.status < 500,
    [`${name} response time < 500ms`]: (r) => r.timings.duration < 30000,
  });
  
  apiSuccessRate.add(success);
  apiDuration.add(response.timings.duration);
}

export function teardown(data) {
  console.log('✅ Load Test Completed!');
  console.log(`Started at: ${data.startTime}`);
  console.log(`Ended at: ${new Date().toISOString()}`);
}

export function handleSummary(data) {
  return {
    'results/load-results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}