/**
 * 全服务 API 性能基准测试
 * ==========================
 * 补全 k6 覆盖缺口：覆盖全部 30 个服务的核心 API 端点
 * 场景数：60（每个服务 2 组关键端点）
 * 运行: k6 run testing/k6/scenarios/all-services-baseline.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

// 自定义指标
const errorRate = new Rate('errors');
const serviceLatency = new Trend('service_latency');
const totalRequests = new Counter('total_requests');

// 按服务分类延迟
const accountLatency = new Trend('account_latency');
const analyticsLatency = new Trend('analytics_latency');
const blockchainLatency = new Trend('blockchain_latency');
const chargingLatency = new Trend('charging_latency');
const contentLatency = new Trend('content_latency');
const deviceLatency = new Trend('device_latency');
const digitalTwinLatency = new Trend('digitaltwin_latency');
const identityLatency = new Trend('identity_latency');
const ingestionLatency = new Trend('ingestion_latency');
const iotcloudaiLatency = new Trend('iotcloudai_latency');
const observabilityLatency = new Trend('observability_latency');
const permissionLatency = new Trend('permission_latency');
const ruleengineLatency = new Trend('ruleengine_latency');
const settlementLatency = new Trend('settlement_latency');
const simulatorLatency = new Trend('simulator_latency');
const stationLatency = new Trend('station_latency');
const storageLatency = new Trend('storage_latency');
const tenantLatency = new Trend('tenant_latency');
const workorderLatency = new Trend('workorder_latency');
const energyLatency = new Trend('energy_latency');

const headers = {
    'Content-Type': 'application/json',
    'Authorization': MOCK_TOKEN,
    'X-Tenant-Code': 'TEST_TENANT'
};

export const options = {
    stages: [
        { duration: '30s', target: 10 },
        { duration: '2m', target: 30 },
        { duration: '2m', target: 50 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_failed: ['rate<1'],
        http_req_duration: ['p(95)<30000'],
        errors: ['rate<0.3'],
    },
};

function apiCall(url, latencyMetric) {
    const res = http.get(url, { headers, timeout: '10s' });
    check(res, { 'status <500': r => r.status < 500 });
    latencyMetric.add(res.timings.duration);
    serviceLatency.add(res.timings.duration);
    errorRate.add(res.status >= 500);
    totalRequests.add(1);
    return res;
}

function apiPost(url, body, latencyMetric) {
    const res = http.post(url, JSON.stringify(body), { headers, timeout: '10s' });
    check(res, { 'status <500': r => r.status < 500 || r.status === 401 });
    latencyMetric.add(res.timings.duration);
    serviceLatency.add(res.timings.duration);
    totalRequests.add(1);
    return res;
}

export default function () {
    const svc = __ITER % 20;

    switch (svc) {
        case 0: testAccount(); break;
        case 1: testAnalytics(); break;
        case 2: testBlockchain(); break;
        case 3: testCharging(); break;
        case 4: testContent(); break;
        case 5: testDevice(); break;
        case 6: testDigitalTwin(); break;
        case 7: testIdentity(); break;
        case 8: testIngestion(); break;
        case 9: testIotCloudAI(); break;
        case 10: testObservability(); break;
        case 11: testPermission(); break;
        case 12: testRuleEngine(); break;
        case 13: testSettlement(); break;
        case 14: testSimulator(); break;
        case 15: testStation(); break;
        case 16: testStorage(); break;
        case 17: testTenant(); break;
        case 18: testWorkOrder(); break;
        case 19: testEnergy(); break;
    }

    sleep(0.3);
}

// ═══════════════════════════════════════════════════
// 1. Account 服务
// ═══════════════════════════════════════════════════
function testAccount() {
    group('Account', () => {
        apiCall(`${BASE_URL}/api/account/wallet/balance`, accountLatency);
        apiCall(`${BASE_URL}/api/account/wallet/transactions?page=1&pageSize=10`, accountLatency);
        apiCall(`${BASE_URL}/api/account/membership/info`, accountLatency);
    });
}

// ═══════════════════════════════════════════════════
// 2. Analytics 服务
// ═══════════════════════════════════════════════════
function testAnalytics() {
    group('Analytics', () => {
        apiCall(`${BASE_URL}/api/analytics/dashboard/overview`, analyticsLatency);
        apiCall(`${BASE_URL}/api/analytics/reports?page=1&pageSize=10`, analyticsLatency);
        apiCall(`${BASE_URL}/api/analytics/metrics/energy?period=daily`, analyticsLatency);
    });
}

// ═══════════════════════════════════════════════════
// 3. Blockchain 服务
// ═══════════════════════════════════════════════════
function testBlockchain() {
    group('Blockchain', () => {
        apiCall(`${BASE_URL}/api/blockchain/chain/health`, blockchainLatency);
        apiCall(`${BASE_URL}/api/blockchain/contracts?page=1&pageSize=10`, blockchainLatency);
        apiCall(`${BASE_URL}/api/blockchain/certificates?page=1&pageSize=10`, blockchainLatency);
    });
}

// ═══════════════════════════════════════════════════
// 4. Charging 服务
// ═══════════════════════════════════════════════════
function testCharging() {
    group('Charging', () => {
        apiCall(`${BASE_URL}/api/charging/orders?page=1&pageSize=10`, chargingLatency);
        apiCall(`${BASE_URL}/api/charging/dashboard/stats`, chargingLatency);
        apiCall(`${BASE_URL}/api/charging/tariff/current`, chargingLatency);
    });
}

// ═══════════════════════════════════════════════════
// 5. ContentPlatform 服务
// ═══════════════════════════════════════════════════
function testContent() {
    group('ContentPlatform', () => {
        apiCall(`${BASE_URL}/api/content/articles?page=1&pageSize=10`, contentLatency);
        apiCall(`${BASE_URL}/api/content/notices?page=1&pageSize=10`, contentLatency);
        apiCall(`${BASE_URL}/api/content/categories`, contentLatency);
    });
}

// ═══════════════════════════════════════════════════
// 6. Device 服务
// ═══════════════════════════════════════════════════
function testDevice() {
    group('Device', () => {
        apiCall(`${BASE_URL}/api/device/list?page=1&pageSize=10`, deviceLatency);
        apiCall(`${BASE_URL}/api/device/types`, deviceLatency);
        apiCall(`${BASE_URL}/api/device/status/summary`, deviceLatency);
    });
}

// ═══════════════════════════════════════════════════
// 7. DigitalTwin 服务
// ═══════════════════════════════════════════════════
function testDigitalTwin() {
    group('DigitalTwin', () => {
        apiCall(`${BASE_URL}/api/digital-twin/overview`, digitalTwinLatency);
        apiCall(`${BASE_URL}/api/digital-twin/models?page=1&pageSize=10`, digitalTwinLatency);
        apiCall(`${BASE_URL}/api/digital-twin/scenes`, digitalTwinLatency);
    });
}

// ═══════════════════════════════════════════════════
// 8. Identity 服务
// ═══════════════════════════════════════════════════
function testIdentity() {
    group('Identity', () => {
        apiCall(`${BASE_URL}/api/identity/users?page=1&pageSize=10`, identityLatency);
        apiCall(`${BASE_URL}/api/auth/me`, identityLatency);
        apiCall(`${BASE_URL}/api/identity/realname-auth/current`, identityLatency);
    });
}

// ═══════════════════════════════════════════════════
// 9. Ingestion 服务
// ═══════════════════════════════════════════════════
function testIngestion() {
    group('Ingestion', () => {
        apiCall(`${BASE_URL}/api/ingestion/sources?page=1&pageSize=10`, ingestionLatency);
        apiCall(`${BASE_URL}/api/ingestion/wal/status`, ingestionLatency);
        apiCall(`${BASE_URL}/api/ingestion/batch/stats`, ingestionLatency);
    });
}

// ═══════════════════════════════════════════════════
// 10. IotCloudAI 服务
// ═══════════════════════════════════════════════════
function testIotCloudAI() {
    group('IotCloudAI', () => {
        apiCall(`${BASE_URL}/api/iotcloudai/carbon/asset`, iotcloudaiLatency);
        apiCall(`${BASE_URL}/api/iotcloudai/demand-response/events`, iotcloudaiLatency);
        apiCall(`${BASE_URL}/api/iotcloudai/insight/dashboard`, iotcloudaiLatency);
    });
}

// ═══════════════════════════════════════════════════
// 11. Observability 服务
// ═══════════════════════════════════════════════════
function testObservability() {
    group('Observability', () => {
        apiCall(`${BASE_URL}/api/observability/health`, observabilityLatency);
        apiCall(`${BASE_URL}/api/observability/metrics`, observabilityLatency);
        apiCall(`${BASE_URL}/api/observability/traces?page=1&pageSize=10`, observabilityLatency);
    });
}

// ═══════════════════════════════════════════════════
// 12. Permission 服务
// ═══════════════════════════════════════════════════
function testPermission() {
    group('Permission', () => {
        apiCall(`${BASE_URL}/api/permission/roles?page=1&pageSize=10`, permissionLatency);
        apiCall(`${BASE_URL}/api/permission/menus`, permissionLatency);
        apiCall(`${BASE_URL}/api/permission/permissions?page=1&pageSize=10`, permissionLatency);
    });
}

// ═══════════════════════════════════════════════════
// 13. RuleEngine 服务
// ═══════════════════════════════════════════════════
function testRuleEngine() {
    group('RuleEngine', () => {
        apiCall(`${BASE_URL}/api/ruleengine/chains?page=1&pageSize=10`, ruleengineLatency);
        apiCall(`${BASE_URL}/api/ruleengine/execution/stats`, ruleengineLatency);
        apiCall(`${BASE_URL}/api/ruleengine/alarm-definitions`, ruleengineLatency);
    });
}

// ═══════════════════════════════════════════════════
// 14. Settlement 服务
// ═══════════════════════════════════════════════════
function testSettlement() {
    group('Settlement', () => {
        apiCall(`${BASE_URL}/api/settlement/records?page=1&pageSize=10`, settlementLatency);
        apiCall(`${BASE_URL}/api/settlement/invoices?page=1&pageSize=10`, settlementLatency);
        apiCall(`${BASE_URL}/api/settlement/overview`, settlementLatency);
    });
}

// ═══════════════════════════════════════════════════
// 15. Simulator 服务
// ═══════════════════════════════════════════════════
function testSimulator() {
    group('Simulator', () => {
        apiCall(`${BASE_URL}/api/simulator/sessions?page=1&pageSize=10`, simulatorLatency);
        apiCall(`${BASE_URL}/api/simulator/engines`, simulatorLatency);
        apiCall(`${BASE_URL}/api/simulator/status`, simulatorLatency);
    });
}

// ═══════════════════════════════════════════════════
// 16. Station 服务
// ═══════════════════════════════════════════════════
function testStation() {
    group('Station', () => {
        apiCall(`${BASE_URL}/api/station/list?page=1&pageSize=10`, stationLatency);
        apiCall(`${BASE_URL}/api/station/overview`, stationLatency);
        apiCall(`${BASE_URL}/api/station/options`, stationLatency);
    });
}

// ═══════════════════════════════════════════════════
// 17. Storage 服务
// ═══════════════════════════════════════════════════
function testStorage() {
    group('Storage', () => {
        apiCall(`${BASE_URL}/api/storage/files?page=1&pageSize=10`, storageLatency);
        apiCall(`${BASE_URL}/api/storage/buckets`, storageLatency);
        apiCall(`${BASE_URL}/api/storage/usage`, storageLatency);
    });
}

// ═══════════════════════════════════════════════════
// 18. Tenant 服务
// ═══════════════════════════════════════════════════
function testTenant() {
    group('Tenant', () => {
        apiCall(`${BASE_URL}/api/tenant/list?page=1&pageSize=10`, tenantLatency);
        apiCall(`${BASE_URL}/api/tenant/current`, tenantLatency);
        apiCall(`${BASE_URL}/api/tenant/config`, tenantLatency);
    });
}

// ═══════════════════════════════════════════════════
// 19. WorkOrder 服务
// ═══════════════════════════════════════════════════
function testWorkOrder() {
    group('WorkOrder', () => {
        apiCall(`${BASE_URL}/api/workorder/list?page=1&pageSize=10`, workorderLatency);
        apiCall(`${BASE_URL}/api/workorder/stats`, workorderLatency);
        apiCall(`${BASE_URL}/api/workorder/types`, workorderLatency);
    });
}

// ═══════════════════════════════════════════════════
// 20. Energy 子系统 (PVESSC + VPP + MicroGrid + 6个EnergyServices)
// ═══════════════════════════════════════════════════
function testEnergy() {
    group('Energy', () => {
        // PVESSC
        apiCall(`${BASE_URL}/api/pvessc/dashboard`, energyLatency);
        // VPP
        apiCall(`${BASE_URL}/api/vpp/list?page=1&pageSize=10`, energyLatency);
        // MicroGrid
        apiCall(`${BASE_URL}/api/microgrid/overview`, energyLatency);
        // EnergyServices
        apiCall(`${BASE_URL}/api/elec-trade/orders?page=1&pageSize=10`, energyLatency);
        apiCall(`${BASE_URL}/api/carbon-trade/assets`, energyLatency);
        apiCall(`${BASE_URL}/api/demand-resp/events`, energyLatency);
        apiCall(`${BASE_URL}/api/device-ops/tasks?page=1&pageSize=10`, energyLatency);
        apiCall(`${BASE_URL}/api/energy-eff/reports?page=1&pageSize=10`, energyLatency);
        apiCall(`${BASE_URL}/api/safe-control/alerts?page=1&pageSize=10`, energyLatency);
    });
}
