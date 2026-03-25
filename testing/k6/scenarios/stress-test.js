// Stress Test - 压力测试，找到系统极限
// 目标：1000个VU，10000+ RPS，23分钟

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import config from '../config.js';
import auth from '../utils/auth.js';
import helpers from '../utils/helpers.js';

const isMockMode = (__ENV.BASE_URL || '').includes('localhost:8000');

function nextRandomInt(min, max) {
  const lower = Math.ceil(min);
  const upper = Math.floor(max);
  return Math.floor(Math.random() * (upper - lower + 1)) + lower;
}

function pickRandom(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }

  return items[nextRandomInt(0, items.length - 1)];
}

// 自定义指标
const successRate = new Rate('success_rate');
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const activeConnections = new Gauge('active_connections');
const requestsPerSecond = new Counter('requests_per_second');
const timeoutErrors = new Counter('timeout_errors');
const connectionErrors = new Counter('connection_errors');

export let options = {
  scenarios: {
    stress: config.scenarios.stress,
  },
  thresholds: isMockMode
    ? {
        http_req_duration: ['p(95)<5000', 'p(99)<10000'],
        http_req_failed: ['rate<1'],
      }
    : config.scenarioThresholds.stress,
};

let authToken = null;

function getFallbackToken() {
  return {
    accessToken: __ENV.MOCK_JWT_TOKEN || 'mock-k6-jwt-token-for-testing',
  };
}

function getConfiguredUsers() {
  return Array.isArray(config.testData?.users) ? config.testData.users : [];
}

function getConfiguredDevices() {
  return Array.isArray(config.testData?.devices) ? config.testData.devices : [];
}

export function setup() {
  console.log('🚀 Starting Stress Test - Finding System Limits...');
  console.log(`Base URL: ${config.baseUrl}`);
  console.log(`Target: 1000 VUs, 10000+ RPS`);
  console.log(`⚠️  This test will push the system to its limits!`);

  const testUser = getConfiguredUsers()[0] || null;
  let token = null;

  if (testUser?.username && testUser?.password) {
    token = auth.login(testUser.username, testUser.password);
  }

  if (!token) {
    token = getFallbackToken();
  }
  
  return { 
    startTime: String(Date.now()),
    token,
    devices: getConfiguredDevices(),
  };
}

export default function (data) {
  activeConnections.add(1);

  const effectiveData = data && typeof data === 'object' ? data : {};
  const effectiveToken = effectiveData.token || getFallbackToken();

  if (!authToken) {
    authToken = effectiveToken;
  }
  
  const authHeaders = auth.getAuthHeaders(authToken);
  const scenarioData = {
    devices: Array.isArray(effectiveData.devices) ? effectiveData.devices : getConfiguredDevices(),
  };
  
  // 高并发场景：大量快速请求
  const operations = nextRandomInt(3, 8); // 每次迭代3-8个请求
  
  for (let i = 0; i < operations; i++) {
    executeRandomOperation(authHeaders, scenarioData);
    sleep(nextRandomInt(50, 200) / 1000); // 50-200ms延迟
  }
  
  activeConnections.add(-1);
  sleep(nextRandomInt(100, 500) / 1000);
}

function executeRandomOperation(headers, data) {
  const op = nextRandomInt(1, 100);
  let response;
  
  try {
    if (op <= 40) {
      // 40% - 读取操作（最常见）
      response = readOperations(headers, data);
    } else if (op <= 70) {
      // 30% - 查询操作
      response = queryOperations(headers, data);
    } else if (op <= 90) {
      // 20% - 列表操作
      response = listOperations(headers);
    } else {
      // 10% - 写入操作
      response = writeOperations(headers, data);
    }
    
    if (response) {
      requestsPerSecond.add(1);
      responseTime.add(response.timings.duration);
      
      const success = response.status >= 200 && response.status < 300;
      successRate.add(success);
      errorRate.add(!success);
      
      // 检查超时
      if (response.timings.duration > 5000) {
        timeoutErrors.add(1);
      }
      
      // 详细错误检查
      if (!success) {
        if (response.status === 0) {
          connectionErrors.add(1);
        }
      }
    }
  } catch (error) {
    errorRate.add(1);
    connectionErrors.add(1);
  }
}

function readOperations(headers, data) {
  const device = data.devices?.[0] || pickRandom(data.devices) || { id: 1 };
  const endpoints = [
    () => http.get(`${config.baseUrl}/api/device/${device.id}`, { headers }),
    () => http.get(`${config.baseUrl}/api/stations/${nextRandomInt(1, 100)}`, { headers }),
    () => http.get(`${config.baseUrl}/api/charging/admin/orders/${nextRandomInt(1, 10000)}`, { headers }),
    () => http.get(`${config.baseUrl}/api/user/profile`, { headers }),
    () => http.get(`${config.baseUrl}/api/device/${device.id}/realtime`, { headers }),
  ];
  
  const operation = pickRandom(endpoints);
  return operation();
}

function queryOperations(headers, data) {
  const queries = [
    () => http.get(
      `${config.baseUrl}/api/device?status=online&page=${nextRandomInt(1, 20)}`,
      { headers }
    ),
    () => http.get(
      `${config.baseUrl}/api/charging/admin/orders?startDate=${helpers.randomPastDate(7)}&page=1`,
      { headers }
    ),
    () => http.get(
      `${config.baseUrl}/api/workorder/search?q=fault&page=${nextRandomInt(1, 10)}`,
      { headers }
    ),
    () => http.get(
      `${config.baseUrl}/api/analytics/energy?period=daily`,
      { headers }
    ),
  ];
  
  const operation = pickRandom(queries);
  return operation();
}

function listOperations(headers) {
  const lists = [
    () => http.get(`${config.baseUrl}/api/stations?page=${nextRandomInt(1, 50)}&pageSize=20`, { headers }),
    () => http.get(`${config.baseUrl}/api/device?page=${nextRandomInt(1, 100)}&pageSize=50`, { headers }),
    () => http.get(`${config.baseUrl}/api/users?page=${nextRandomInt(1, 20)}&pageSize=20`, { headers }),
    () => http.get(`${config.baseUrl}/api/charging/admin/orders?page=${nextRandomInt(1, 200)}&pageSize=50`, { headers }),
  ];
  
  const operation = pickRandom(lists);
  return operation();
}

function writeOperations(headers, data) {
  const device = data.devices?.[0] || pickRandom(data.devices) || { id: 1 };
  const writes = [
    () => {
      const deviceData = helpers.generateDeviceData(device.id);
      return http.post(
        `${config.baseUrl}/api/device/${device.id}/data`,
        JSON.stringify(deviceData),
        { headers }
      );
    },
    () => {
      const record = helpers.generateChargingRecord(device.id, 1);
      return http.post(
        `${config.baseUrl}/api/charging/admin/orders`,
        JSON.stringify(record),
        { headers }
      );
    },
    () => {
      const workorder = helpers.generateWorkOrder(device.id, 1);
      return http.post(
        `${config.baseUrl}/api/workorder`,
        JSON.stringify(workorder),
        { headers }
      );
    },
  ];
  
  // 写入操作概率降低（避免产生太多测试数据）
  if (nextRandomInt(1, 5) === 1) {
    const operation = pickRandom(writes);
    return operation();
  }
  
  return null;
}

export function teardown(data) {
  console.log('✅ Stress Test Completed!');
  console.log(`Started at: ${data.startTime}`);
  console.log(`Ended at: ${new Date().toISOString()}`);
  console.log(`\n📊 Review metrics to identify system bottlenecks:`);
  console.log(`   - error_rate: Check for elevated error rates`);
  console.log(`   - response_time: Check P95/P99 latencies`);
  console.log(`   - timeout_errors: Check for timeout spikes`);
  console.log(`   - connection_errors: Check for connection failures`);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}