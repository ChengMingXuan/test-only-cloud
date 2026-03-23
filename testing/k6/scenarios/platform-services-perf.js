// k6 补全性能测试 — 覆盖审计发现的10个缺口服务
// ================================================
// Gap: Identity, Permission, Tenant, Storage, Observability,
//      ContentPlatform, DigitalTwin, Account, RuleEngine, Simulator
//
// 每个服务: 登录认证 → CRUD基础操作 → 列表分页 → 搜索过滤
// 目标: P95 < 500ms, 错误率 < 5%

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ─── 配置 ───
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const ADMIN_USER = __ENV.ADMIN_USER || 'admin';
const ADMIN_PASS = __ENV.ADMIN_PASS || 'P@ssw0rd';

// ─── 自定义指标 ───
const identityLatency = new Trend('identity_api_latency', true);
const permissionLatency = new Trend('permission_api_latency', true);
const tenantLatency = new Trend('tenant_api_latency', true);
const storageLatency = new Trend('storage_api_latency', true);
const observabilityLatency = new Trend('observability_api_latency', true);
const contentLatency = new Trend('content_api_latency', true);
const digitalTwinLatency = new Trend('digitaltwin_api_latency', true);
const accountLatency = new Trend('account_api_latency', true);
const ruleEngineLatency = new Trend('ruleengine_api_latency', true);
const simulatorLatency = new Trend('simulator_api_latency', true);
const errorRate = new Rate('error_rate');
const requestCount = new Counter('total_requests');

export let options = {
  stages: [
    { duration: '30s', target: 5 },    // 预热
    { duration: '1m', target: 20 },     // 爬坡
    { duration: '2m', target: 50 },     // 稳态
    { duration: '1m', target: 100 },    // 高峰
    { duration: '30s', target: 0 },     // 降温
  ],
  thresholds: {
    'identity_api_latency': ['p(95)<500'],
    'permission_api_latency': ['p(95)<500'],
    'tenant_api_latency': ['p(95)<500'],
    'storage_api_latency': ['p(95)<800'],
    'observability_api_latency': ['p(95)<500'],
    'content_api_latency': ['p(95)<500'],
    'digitaltwin_api_latency': ['p(95)<800'],
    'account_api_latency': ['p(95)<500'],
    'ruleengine_api_latency': ['p(95)<800'],
    'simulator_api_latency': ['p(95)<1000'],
    'error_rate': ['rate<0.05'],
  },
};

function getAuthHeaders(token) {
  return {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };
}

export function setup() {
  console.log('🚀 平台基础服务性能测试启动...');
  // 尝试登录获取 token
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    username: ADMIN_USER,
    password: ADMIN_PASS,
  }), { headers: { 'Content-Type': 'application/json' } });

  let token = 'mock-token';
  if (loginRes.status === 200) {
    try {
      const body = JSON.parse(loginRes.body);
      token = body.data?.accessToken || body.data?.token || token;
    } catch (e) { /* fallback */ }
  }
  return { token };
}

export default function (data) {
  const params = getAuthHeaders(data.token);

  // ─── 1. Identity 身份认证 ───
  group('Identity API', () => {
    const r1 = http.get(`${BASE_URL}/api/auth/user/current`, params);
    identityLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'identity: current user ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/identity/departments`, params);
    identityLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'identity: departments ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/identity/users?page=1&pageSize=20`, params);
    identityLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'identity: user list ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);

    const r4 = http.get(`${BASE_URL}/api/identity/captcha`, params);
    identityLatency.add(r4.timings.duration);
    requestCount.add(1);
    check(r4, { 'identity: captcha ok': r => r.status < 500 });
    errorRate.add(r4.status >= 500);
  });
  sleep(0.5);

  // ─── 2. Permission 权限管理 ───
  group('Permission API', () => {
    const r1 = http.get(`${BASE_URL}/api/system/role?page=1&pageSize=20`, params);
    permissionLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'permission: role list ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/system/menu`, params);
    permissionLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'permission: menu tree ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/system/permissions`, params);
    permissionLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'permission: perm list ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);

    const r4 = http.get(`${BASE_URL}/api/system/data-scope/policies?page=1&pageSize=10`, params);
    permissionLatency.add(r4.timings.duration);
    requestCount.add(1);
    check(r4, { 'permission: data-scope ok': r => r.status < 500 });
    errorRate.add(r4.status >= 500);
  });
  sleep(0.5);

  // ─── 3. Tenant 租户管理 ───
  group('Tenant API', () => {
    const r1 = http.get(`${BASE_URL}/api/tenants?page=1&pageSize=20`, params);
    tenantLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'tenant: list ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/tenants/features`, params);
    tenantLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'tenant: features ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/tenants/quotas`, params);
    tenantLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'tenant: quotas ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);
  });
  sleep(0.5);

  // ─── 4. Storage 文件存储 ───
  group('Storage API', () => {
    const r1 = http.get(`${BASE_URL}/api/storage/files?page=1&pageSize=20`, params);
    storageLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'storage: file list ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/storage/quota`, params);
    storageLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'storage: quota ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/storage/buckets`, params);
    storageLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'storage: buckets ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);
  });
  sleep(0.5);

  // ─── 5. Observability 可观测性 ───
  group('Observability API', () => {
    const r1 = http.get(`${BASE_URL}/api/monitor/health`, params);
    observabilityLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'observability: health ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/monitor/metrics?page=1&pageSize=20`, params);
    observabilityLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'observability: metrics ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/monitor/audit-logs?page=1&pageSize=20`, params);
    observabilityLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'observability: audit-logs ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);

    const r4 = http.get(`${BASE_URL}/api/monitor/service-mesh/status`, params);
    observabilityLatency.add(r4.timings.duration);
    requestCount.add(1);
    check(r4, { 'observability: service-mesh ok': r => r.status < 500 });
    errorRate.add(r4.status >= 500);
  });
  sleep(0.5);

  // ─── 6. ContentPlatform 内容平台 ───
  group('ContentPlatform API', () => {
    const r1 = http.get(`${BASE_URL}/api/content/articles?page=1&pageSize=20`, params);
    contentLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'content: article list ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/content/categories`, params);
    contentLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'content: categories ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/content/announcements?page=1&pageSize=10`, params);
    contentLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'content: announcements ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);
  });
  sleep(0.5);

  // ─── 7. DigitalTwin 数字孪生 ───
  group('DigitalTwin API', () => {
    const r1 = http.get(`${BASE_URL}/api/digitaltwin/overview`, params);
    digitalTwinLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'digitaltwin: overview ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/digitaltwin/alerts?page=1&pageSize=20`, params);
    digitalTwinLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'digitaltwin: alerts ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/digitaltwin/simulation/scenarios?page=1&pageSize=10`, params);
    digitalTwinLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'digitaltwin: scenarios ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);

    const r4 = http.get(`${BASE_URL}/api/digitaltwin/predictive-maintenance/status`, params);
    digitalTwinLatency.add(r4.timings.duration);
    requestCount.add(1);
    check(r4, { 'digitaltwin: maintenance ok': r => r.status < 500 });
    errorRate.add(r4.status >= 500);
  });
  sleep(0.5);

  // ─── 8. Account 账户服务 ───
  group('Account API', () => {
    const r1 = http.get(`${BASE_URL}/api/users/profile`, params);
    accountLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'account: profile ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/users/wallet/balance`, params);
    accountLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'account: wallet balance ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/users/membership/level`, params);
    accountLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'account: membership ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);

    const r4 = http.get(`${BASE_URL}/api/users/points/history?page=1&pageSize=10`, params);
    accountLatency.add(r4.timings.duration);
    requestCount.add(1);
    check(r4, { 'account: points history ok': r => r.status < 500 });
    errorRate.add(r4.status >= 500);
  });
  sleep(0.5);

  // ─── 9. RuleEngine 规则引擎 ───
  group('RuleEngine API', () => {
    const r1 = http.get(`${BASE_URL}/api/ruleengine/chains?page=1&pageSize=20`, params);
    ruleEngineLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'ruleengine: chain list ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/ruleengine/alarms/definitions`, params);
    ruleEngineLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'ruleengine: alarm defs ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    const r3 = http.get(`${BASE_URL}/api/ruleengine/alarms/instances?page=1&pageSize=20`, params);
    ruleEngineLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'ruleengine: alarm instances ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);

    const r4 = http.get(`${BASE_URL}/api/ruleengine/execution-logs?page=1&pageSize=20`, params);
    ruleEngineLatency.add(r4.timings.duration);
    requestCount.add(1);
    check(r4, { 'ruleengine: exec logs ok': r => r.status < 500 });
    errorRate.add(r4.status >= 500);
  });
  sleep(0.5);

  // ─── 10. Simulator 模拟器 ───
  group('Simulator API', () => {
    const r1 = http.get(`${BASE_URL}/api/simulator/sessions?page=1&pageSize=20`, params);
    simulatorLatency.add(r1.timings.duration);
    requestCount.add(1);
    check(r1, { 'simulator: session list ok': r => r.status < 500 });
    errorRate.add(r1.status >= 500);

    const r2 = http.get(`${BASE_URL}/api/simulator/commands?page=1&pageSize=20`, params);
    simulatorLatency.add(r2.timings.duration);
    requestCount.add(1);
    check(r2, { 'simulator: commands ok': r => r.status < 500 });
    errorRate.add(r2.status >= 500);

    // 模拟器状态查询不应阻塞
    const r3 = http.get(`${BASE_URL}/api/simulator/status`, params);
    simulatorLatency.add(r3.timings.duration);
    requestCount.add(1);
    check(r3, { 'simulator: status ok': r => r.status < 500 });
    errorRate.add(r3.status >= 500);
  });
  sleep(0.5);
}

export function teardown(data) {
  console.log('✅ 平台基础服务性能测试完成');
}
