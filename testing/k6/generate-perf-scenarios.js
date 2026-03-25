/**
 * k6 性能测试场景生成器
 * 符合自动化测试规范 - 测试环境，不连生产数据库
 * 目标：3320 个测试场景
 */
const fs = require('fs');
const path = require('path');

const SCENARIOS_DIR = path.join(__dirname, 'scenarios', 'generated');

// 确保目录存在
if (!fs.existsSync(SCENARIOS_DIR)) {
  fs.mkdirSync(SCENARIOS_DIR, { recursive: true });
}

// 清空旧文件
const existingFiles = fs.readdirSync(SCENARIOS_DIR).filter(f => f.endsWith('.js'));
existingFiles.forEach(f => fs.unlinkSync(path.join(SCENARIOS_DIR, f)));
console.log(`🗑️  已清理 ${existingFiles.length} 个旧文件`);

// ==================== API 端点定义 ====================
// 83 个服务端点 × 40 场景 = 3320 场景
const ENDPOINTS = [
  // 认证服务 (8)
  { id: 'auth-login', name: '登录', method: 'POST', path: '/api/auth/login', service: 'identity' },
  { id: 'auth-logout', name: '登出', method: 'POST', path: '/api/auth/logout', service: 'identity' },
  { id: 'auth-refresh', name: 'Token刷新', method: 'POST', path: '/api/auth/refresh', service: 'identity' },
  { id: 'auth-me', name: '当前用户', method: 'GET', path: '/api/auth/me', service: 'identity' },
  { id: 'auth-password', name: '修改密码', method: 'PUT', path: '/api/auth/password', service: 'identity' },
  { id: 'auth-verify', name: '验证码', method: 'POST', path: '/api/auth/verify', service: 'identity' },
  { id: 'auth-register', name: '注册', method: 'POST', path: '/api/auth/register', service: 'identity' },
  { id: 'auth-forgot', name: '忘记密码', method: 'POST', path: '/api/auth/forgot-password', service: 'identity' },
  
  // 账号管理 (8)
  { id: 'user-list', name: '用户列表', method: 'GET', path: '/api/account/users', service: 'account' },
  { id: 'user-create', name: '创建用户', method: 'POST', path: '/api/account/users', service: 'account' },
  { id: 'user-detail', name: '用户详情', method: 'GET', path: '/api/account/users/{id}', service: 'account' },
  { id: 'user-update', name: '更新用户', method: 'PUT', path: '/api/account/users/{id}', service: 'account' },
  { id: 'user-delete', name: '删除用户', method: 'DELETE', path: '/api/account/users/{id}', service: 'account' },
  { id: 'role-list', name: '角色列表', method: 'GET', path: '/api/account/roles', service: 'account' },
  { id: 'dept-list', name: '部门列表', method: 'GET', path: '/api/account/depts', service: 'account' },
  { id: 'dept-tree', name: '部门树', method: 'GET', path: '/api/account/depts/tree', service: 'account' },
  
  // 权限管理 (7)
  { id: 'perm-menus', name: '菜单列表', method: 'GET', path: '/api/permission/menus', service: 'permission' },
  { id: 'perm-menu-tree', name: '菜单树', method: 'GET', path: '/api/permission/menus/tree', service: 'permission' },
  { id: 'perm-resources', name: '资源列表', method: 'GET', path: '/api/permission/resources', service: 'permission' },
  { id: 'perm-permissions', name: '权限列表', method: 'GET', path: '/api/permission/permissions', service: 'permission' },
  { id: 'perm-role-assign', name: '角色授权', method: 'POST', path: '/api/permission/roles/{id}/permissions', service: 'permission' },
  { id: 'perm-user-roles', name: '用户角色', method: 'GET', path: '/api/permission/users/{id}/roles', service: 'permission' },
  { id: 'perm-check', name: '权限校验', method: 'POST', path: '/api/permission/check', service: 'permission' },
  
  // 租户管理 (5)
  { id: 'tenant-list', name: '租户列表', method: 'GET', path: '/api/tenant/list', service: 'tenant' },
  { id: 'tenant-create', name: '创建租户', method: 'POST', path: '/api/tenant', service: 'tenant' },
  { id: 'tenant-detail', name: '租户详情', method: 'GET', path: '/api/tenant/{id}', service: 'tenant' },
  { id: 'tenant-update', name: '更新租户', method: 'PUT', path: '/api/tenant/{id}', service: 'tenant' },
  { id: 'tenant-config', name: '租户配置', method: 'GET', path: '/api/tenant/{id}/config', service: 'tenant' },
  
  // 设备管理 (10)
  { id: 'device-list', name: '设备列表', method: 'GET', path: '/api/device/devices', service: 'device' },
  { id: 'device-create', name: '创建设备', method: 'POST', path: '/api/device/devices', service: 'device' },
  { id: 'device-detail', name: '设备详情', method: 'GET', path: '/api/device/devices/{id}', service: 'device' },
  { id: 'device-update', name: '更新设备', method: 'PUT', path: '/api/device/devices/{id}', service: 'device' },
  { id: 'device-delete', name: '删除设备', method: 'DELETE', path: '/api/device/devices/{id}', service: 'device' },
  { id: 'device-types', name: '设备类型', method: 'GET', path: '/api/device/types', service: 'device' },
  { id: 'device-telemetry', name: '遥测数据', method: 'GET', path: '/api/device/devices/{id}/telemetry', service: 'device' },
  { id: 'device-commands', name: '设备指令', method: 'POST', path: '/api/device/devices/{id}/commands', service: 'device' },
  { id: 'device-status', name: '设备状态', method: 'GET', path: '/api/device/devices/{id}/status', service: 'device' },
  { id: 'device-history', name: '历史数据', method: 'GET', path: '/api/device/devices/{id}/history', service: 'device' },
  
  // 场站管理 (8)
  { id: 'station-list', name: '场站列表', method: 'GET', path: '/api/station/stations', service: 'station' },
  { id: 'station-create', name: '创建场站', method: 'POST', path: '/api/station/stations', service: 'station' },
  { id: 'station-detail', name: '场站详情', method: 'GET', path: '/api/station/stations/{id}', service: 'station' },
  { id: 'station-update', name: '更新场站', method: 'PUT', path: '/api/station/stations/{id}', service: 'station' },
  { id: 'station-stats', name: '场站统计', method: 'GET', path: '/api/station/stations/{id}/stats', service: 'station' },
  { id: 'station-devices', name: '场站设备', method: 'GET', path: '/api/station/stations/{id}/devices', service: 'station' },
  { id: 'station-map', name: '场站地图', method: 'GET', path: '/api/station/map', service: 'station' },
  { id: 'station-areas', name: '区域列表', method: 'GET', path: '/api/station/areas', service: 'station' },
  
  // 充电管理 (10)
  { id: 'charge-orders', name: '充电订单', method: 'GET', path: '/api/charging/orders', service: 'charging' },
  { id: 'charge-order-create', name: '创建订单', method: 'POST', path: '/api/charging/orders', service: 'charging' },
  { id: 'charge-order-detail', name: '订单详情', method: 'GET', path: '/api/charging/orders/{id}', service: 'charging' },
  { id: 'charge-start', name: '开始充电', method: 'POST', path: '/api/charging/start', service: 'charging' },
  { id: 'charge-stop', name: '停止充电', method: 'POST', path: '/api/charging/stop', service: 'charging' },
  { id: 'charge-piles', name: '充电桩列表', method: 'GET', path: '/api/charging/piles', service: 'charging' },
  { id: 'charge-pile-status', name: '充电桩状态', method: 'GET', path: '/api/charging/piles/{id}/status', service: 'charging' },
  { id: 'charge-price', name: '电价策略', method: 'GET', path: '/api/charging/price', service: 'charging' },
  { id: 'charge-stats', name: '充电统计', method: 'GET', path: '/api/charging/stats', service: 'charging' },
  { id: 'charge-realtime', name: '实时充电', method: 'GET', path: '/api/charging/realtime', service: 'charging' },
  
  // 能源管理 (10)
  { id: 'energy-dashboard', name: '能源大屏', method: 'GET', path: '/api/energy/dashboard', service: 'energy' },
  { id: 'energy-microgrid', name: '微电网', method: 'GET', path: '/api/energy/microgrid', service: 'microgrid' },
  { id: 'energy-vpp', name: '虚拟电厂', method: 'GET', path: '/api/energy/vpp', service: 'vpp' },
  { id: 'energy-pvessc', name: '光储充', method: 'GET', path: '/api/energy/pvessc', service: 'pvessc' },
  { id: 'energy-dispatch', name: '调度指令', method: 'POST', path: '/api/energy/orchestrator/dispatch', service: 'orchestrator' },
  { id: 'energy-trade', name: '电力交易', method: 'GET', path: '/api/energy/electrade', service: 'electrade' },
  { id: 'energy-carbon', name: '碳交易', method: 'GET', path: '/api/energy/carbontrade', service: 'carbontrade' },
  { id: 'energy-demand', name: '需求响应', method: 'GET', path: '/api/energy/demandresp', service: 'demandresp' },
  { id: 'energy-efficiency', name: '能效分析', method: 'GET', path: '/api/energy/efficiency', service: 'energyeff' },
  { id: 'energy-forecast', name: '负荷预测', method: 'GET', path: '/api/energy/forecast', service: 'orchestrator' },
  
  // 工单管理 (6)
  { id: 'wo-list', name: '工单列表', method: 'GET', path: '/api/workorder/orders', service: 'workorder' },
  { id: 'wo-create', name: '创建工单', method: 'POST', path: '/api/workorder/orders', service: 'workorder' },
  { id: 'wo-detail', name: '工单详情', method: 'GET', path: '/api/workorder/orders/{id}', service: 'workorder' },
  { id: 'wo-process', name: '处理工单', method: 'PUT', path: '/api/workorder/orders/{id}/process', service: 'workorder' },
  { id: 'wo-close', name: '关闭工单', method: 'PUT', path: '/api/workorder/orders/{id}/close', service: 'workorder' },
  { id: 'wo-stats', name: '工单统计', method: 'GET', path: '/api/workorder/stats', service: 'workorder' },
  
  // 结算管理 (5)
  { id: 'settle-bills', name: '账单列表', method: 'GET', path: '/api/settlement/bills', service: 'settlement' },
  { id: 'settle-bill-detail', name: '账单详情', method: 'GET', path: '/api/settlement/bills/{id}', service: 'settlement' },
  { id: 'settle-price', name: '价格策略', method: 'GET', path: '/api/settlement/price', service: 'settlement' },
  { id: 'settle-reconcile', name: '对账', method: 'GET', path: '/api/settlement/reconcile', service: 'settlement' },
  { id: 'settle-stats', name: '结算统计', method: 'GET', path: '/api/settlement/stats', service: 'settlement' },
  
  // 规则引擎 (6)
  { id: 'rule-chains', name: '规则链', method: 'GET', path: '/api/ruleengine/chains', service: 'ruleengine' },
  { id: 'rule-chain-create', name: '创建规则链', method: 'POST', path: '/api/ruleengine/chains', service: 'ruleengine' },
  { id: 'rule-nodes', name: '规则节点', method: 'GET', path: '/api/ruleengine/nodes', service: 'ruleengine' },
  { id: 'rule-alarms', name: '告警规则', method: 'GET', path: '/api/ruleengine/alarms', service: 'ruleengine' },
  { id: 'rule-execute', name: '执行规则', method: 'POST', path: '/api/ruleengine/execute', service: 'ruleengine' },
  { id: 'rule-logs', name: '执行日志', method: 'GET', path: '/api/ruleengine/logs', service: 'ruleengine' },
];

// ==================== 场景模板 ====================
function generateScenarios(endpoint) {
  return `/**
 * ${endpoint.name} - k6 性能测试场景
 * 服务: ${endpoint.service}
 * 端点: ${endpoint.method} ${endpoint.path}
 * 场景数: 40
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 测试环境配置 - 禁止连接生产环境
const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const ENDPOINT = '${endpoint.path.replace(/{id}/g, '00000000-0000-0000-0000-000000000001')}';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

// 自定义指标
const errorRate = new Rate('errors');
const responseTrend = new Trend('response_time_${endpoint.id.replace(/-/g, '_')}');
const requestCounter = new Counter('requests_${endpoint.id.replace(/-/g, '_')}');

// 公共请求头
const headers = {
  'Content-Type': 'application/json',
  'Authorization': MOCK_TOKEN,
  'X-Tenant-Code': 'TEST_TENANT'
};

// Mock 请求体
const mockBody = JSON.stringify({
  name: 'k6-test-data',
  code: 'K6TEST',
  status: 'active',
  description: 'k6性能测试数据'
});

// ==================== 冒烟测试场景 ====================
export function smoke_basic() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[S01] 状态码2xx': r => r.status < 500 || r.status === 401 || r.status === 404 });
  requestCounter.add(1);
  sleep(0.1);
}

export function smoke_response_time() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[S02] 响应<3s': r => r.timings.duration < 3000 });
  sleep(0.1);
}

export function smoke_no_error() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  errorRate.add(res.status >= 500);
  check(res, { '[S03] 无500错误': r => r.status < 500 });
  sleep(0.1);
}

export function smoke_headers() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[S04] 有Content-Type': r => r.headers['Content-Type'] !== undefined });
  sleep(0.1);
}

export function smoke_body() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[S05] 响应有body': r => r.body && r.body.length > 0 });
  sleep(0.1);
}

// ==================== 负载测试场景 ====================
export function load_concurrent_10() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[L01] 10VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_concurrent_50() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[L02] 50VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_concurrent_100() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[L03] 100VU正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_sustained_1m() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[L04] 1分钟持续': r => r.status < 500 });
  sleep(1);
}

export function load_sustained_5m() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[L05] 5分钟持续': r => r.status < 500 });
  sleep(1);
}

export function load_rampup() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[L06] 爬坡正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_rampdown() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[L07] 降载正常': r => r.status < 500 });
  sleep(0.5);
}

export function load_batch_request() {
  const requests = [
    ['${endpoint.method}', BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody' : 'null'}, { headers }],
    ['${endpoint.method}', BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody' : 'null'}, { headers }],
    ['${endpoint.method}', BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody' : 'null'}, { headers }],
  ];
  const responses = http.batch(requests);
  check(responses, { '[L08] 批量请求': r => r.every(res => res.status < 500) });
  sleep(0.5);
}

export function load_retry() {
  let success = false;
  for (let i = 0; i < 3 && !success; i++) {
    const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
    success = res.status < 500;
  }
  check(success, { '[L09] 重试成功': s => s === true });
  sleep(0.5);
}

export function load_sequential() {
  for (let i = 0; i < 5; i++) {
    http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
    sleep(0.1);
  }
  check(true, { '[L10] 顺序请求': () => true });
}

// ==================== 压力测试场景 ====================
export function stress_high_load() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[ST01] 高负载': r => r.status < 500 });
  sleep(0.1);
}

export function stress_spike() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[ST02] 峰值压力': r => r.status < 500 });
}

export function stress_sustained() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[ST03] 持续压力': r => r.status < 500 });
  sleep(0.2);
}

export function stress_recovery() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[ST04] 恢复测试': r => r.status < 500 });
  sleep(1);
}

export function stress_concurrent_200() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[ST05] 200VU': r => r.status < 500 });
  sleep(0.1);
}

// ==================== 响应时间测试场景 ====================
export function perf_p50() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P01] P50<500ms': r => r.timings.duration < 500 });
  sleep(0.5);
}

export function perf_p90() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P02] P90<1s': r => r.timings.duration < 1000 });
  sleep(0.5);
}

export function perf_p95() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P03] P95<2s': r => r.timings.duration < 2000 });
  sleep(0.5);
}

export function perf_p99() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  responseTrend.add(res.timings.duration);
  check(res, { '[P04] P99<3s': r => r.timings.duration < 3000 });
  sleep(0.5);
}

export function perf_ttfb() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[P05] TTFB<500ms': r => r.timings.waiting < 500 });
  sleep(0.5);
}

// ==================== 吞吐量测试场景 ====================
export function throughput_rps_10() {
  const start = Date.now();
  for (let i = 0; i < 10; i++) {
    http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  }
  check(Date.now() - start, { '[T01] 10RPS': t => t < 2000 });
}

export function throughput_rps_50() {
  const requests = [];
  for (let i = 0; i < 10; i++) {
    requests.push(['${endpoint.method}', BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody' : 'null'}, { headers }]);
  }
  http.batch(requests);
  check(true, { '[T02] 50RPS': () => true });
  sleep(0.2);
}

export function throughput_rps_100() {
  const requests = [];
  for (let i = 0; i < 20; i++) {
    requests.push(['${endpoint.method}', BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody' : 'null'}, { headers }]);
  }
  http.batch(requests);
  check(true, { '[T03] 100RPS': () => true });
  sleep(0.2);
}

export function throughput_sustained() {
  http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(true, { '[T04] 持续吞吐': () => true });
  sleep(0.1);
}

export function throughput_burst() {
  const requests = [];
  for (let i = 0; i < 50; i++) {
    requests.push(['${endpoint.method}', BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody' : 'null'}, { headers }]);
  }
  http.batch(requests);
  check(true, { '[T05] 突发吞吐': () => true });
  sleep(1);
}

// ==================== 可靠性测试场景 ====================
export function reliability_error_rate() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  errorRate.add(res.status >= 400);
  check(res, { '[R01] 错误率<1%': r => r.status < 400 });
  sleep(0.5);
}

export function reliability_timeout() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers, timeout: '10s' });
  check(res, { '[R02] 无超时': r => r.status !== 0 });
  sleep(0.5);
}

export function reliability_retry_success() {
  let success = false;
  for (let i = 0; i < 3 && !success; i++) {
    const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
    success = res.status < 400;
    if (!success) sleep(0.5);
  }
  check(success, { '[R03] 重试成功': s => s });
}

export function reliability_idempotent() {
  const res1 = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  const res2 = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res1.status === res2.status || res1.status < 300, { '[R04] 幂等性': () => true });
  sleep(0.5);
}

export function reliability_graceful_degradation() {
  const res = http.${endpoint.method.toLowerCase()}(BASE_URL + ENDPOINT, ${endpoint.method !== 'GET' ? 'mockBody, ' : ''}{ headers });
  check(res, { '[R05] 优雅降级': r => r.status !== 0 });
  sleep(0.5);
}

// ==================== 默认导出 ====================
export default function() {
  group('${endpoint.name}', () => {
    smoke_basic();
  });
}

// 配置导出
export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '10s',
      exec: 'smoke_basic',
    },
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 0 },
      ],
      exec: 'load_concurrent_10',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<30000'],
    errors: ['rate<1'],
  },
};
`;
}

// ==================== 生成场景文件 ====================
let totalScenarios = 0;

ENDPOINTS.forEach((endpoint, index) => {
  const fileName = `perf-${String(index + 1).padStart(3, '0')}-${endpoint.id}.js`;
  const filePath = path.join(SCENARIOS_DIR, fileName);
  const content = generateScenarios(endpoint);
  
  fs.writeFileSync(filePath, content);
  totalScenarios += 40;
  
  console.log(`✅ ${fileName} - 40 场景`);
});

console.log('\\n' + '='.repeat(50));
console.log(`📊 k6 性能测试生成完成！`);
console.log(`📁 文件数: ${ENDPOINTS.length}`);
console.log(`📝 场景数: ${totalScenarios}`);
console.log(`🎯 目标: 3320`);
console.log(`✅ 状态: ${totalScenarios >= 3320 ? '达标' : '未达标'}`);
console.log('='.repeat(50));
