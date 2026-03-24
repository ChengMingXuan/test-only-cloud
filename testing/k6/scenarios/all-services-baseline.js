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
import { login, getAuthHeaders } from '../utils/auth.js';

const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const TENANT_CODE = __ENV.ADMIN_TENANT_CODE || __ENV.TENANT_CODE || 'default';
const ADMIN_USERNAME = __ENV.ADMIN_USERNAME || 'admin';
const ADMIN_PASSWORD = __ENV.ADMIN_PASSWORD || 'P@ssw0rd';

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

export const options = {
    stages: [
        { duration: '30s', target: 10 },
        { duration: '2m', target: 30 },
        { duration: '2m', target: 50 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_failed: ['rate<0.05'],
        http_req_duration: ['p(95)<30000'],
        errors: ['rate<0.3'],
    },
};

export function setup() {
    const auth = login(ADMIN_USERNAME, ADMIN_PASSWORD);
    if (!auth || !auth.accessToken) {
        throw new Error(`k6 baseline login failed for ${ADMIN_USERNAME}. Check Identity login endpoint and credentials.`);
    }

    return {
        accessToken: auth.accessToken,
        refreshToken: auth.refreshToken || '',
        tenantCode: TENANT_CODE,
        tenantId: auth.tenantId || null,
    };
}

function buildHeaders(setupData) {
    return {
        ...getAuthHeaders(setupData.accessToken),
        'Content-Type': 'application/json',
        'X-Tenant-Code': setupData.tenantCode,
    };
}

function apiCall(url, latencyMetric, headers) {
    const res = http.get(url, { headers, timeout: '10s' });
    check(res, {
        'status is success': r => r.status >= 200 && r.status < 400,
    });
    latencyMetric.add(res.timings.duration);
    serviceLatency.add(res.timings.duration);
    errorRate.add(res.status >= 500);
    totalRequests.add(1);
    return res;
}

function apiPost(url, body, latencyMetric, headers) {
    const res = http.post(url, JSON.stringify(body), { headers, timeout: '10s' });
    check(res, {
        'status is success': r => r.status >= 200 && r.status < 400,
    });
    latencyMetric.add(res.timings.duration);
    serviceLatency.add(res.timings.duration);
    totalRequests.add(1);
    return res;
}

export default function (setupData) {
    const headers = buildHeaders(setupData);
    const svc = __ITER % 20;

    switch (svc) {
        case 0: testAccount(headers); break;
        case 1: testAnalytics(headers); break;
        case 2: testBlockchain(headers); break;
        case 3: testCharging(headers); break;
        case 4: testContent(headers); break;
        case 5: testDevice(headers); break;
        case 6: testDigitalTwin(headers); break;
        case 7: testIdentity(headers); break;
        case 8: testIngestion(headers); break;
        case 9: testIotCloudAI(headers); break;
        case 10: testObservability(headers); break;
        case 11: testPermission(headers); break;
        case 12: testRuleEngine(headers); break;
        case 13: testSettlement(headers); break;
        case 14: testSimulator(headers); break;
        case 15: testStation(headers); break;
        case 16: testStorage(headers); break;
        case 17: testTenant(headers); break;
        case 18: testWorkOrder(headers); break;
        case 19: testEnergy(headers); break;
    }

    sleep(0.3);
}

// ═══════════════════════════════════════════════════
// 1. Account 服务
// ═══════════════════════════════════════════════════
function testAccount(headers) {
    group('Account', () => {
        apiCall(`${BASE_URL}/api/account/wallet/balance`, accountLatency, headers);
        apiCall(`${BASE_URL}/api/account/wallet/transactions?page=1&pageSize=10`, accountLatency, headers);
        apiCall(`${BASE_URL}/api/account/membership/info`, accountLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 2. Analytics 服务
// ═══════════════════════════════════════════════════
function testAnalytics(headers) {
    group('Analytics', () => {
        apiCall(`${BASE_URL}/api/analytics/dashboard/overview`, analyticsLatency, headers);
        apiCall(`${BASE_URL}/api/analytics/reports?page=1&pageSize=10`, analyticsLatency, headers);
        apiCall(`${BASE_URL}/api/analytics/metrics/energy?period=daily`, analyticsLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 3. Blockchain 服务
// ═══════════════════════════════════════════════════
function testBlockchain(headers) {
    group('Blockchain', () => {
        apiCall(`${BASE_URL}/api/blockchain/chain/health`, blockchainLatency, headers);
        apiCall(`${BASE_URL}/api/blockchain/contracts?page=1&pageSize=10`, blockchainLatency, headers);
        apiCall(`${BASE_URL}/api/blockchain/certificates?page=1&pageSize=10`, blockchainLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 4. Charging 服务
// ═══════════════════════════════════════════════════
function testCharging(headers) {
    group('Charging', () => {
        apiCall(`${BASE_URL}/api/charging/orders?page=1&pageSize=10`, chargingLatency, headers);
        apiCall(`${BASE_URL}/api/charging/dashboard/stats`, chargingLatency, headers);
        apiCall(`${BASE_URL}/api/charging/tariff/current`, chargingLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 5. ContentPlatform 服务
// ═══════════════════════════════════════════════════
function testContent(headers) {
    group('ContentPlatform', () => {
        apiCall(`${BASE_URL}/api/content/articles?page=1&pageSize=10`, contentLatency, headers);
        apiCall(`${BASE_URL}/api/content/notices?page=1&pageSize=10`, contentLatency, headers);
        apiCall(`${BASE_URL}/api/content/categories`, contentLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 6. Device 服务
// ═══════════════════════════════════════════════════
function testDevice(headers) {
    group('Device', () => {
        apiCall(`${BASE_URL}/api/device/list?page=1&pageSize=10`, deviceLatency, headers);
        apiCall(`${BASE_URL}/api/device/types`, deviceLatency, headers);
        apiCall(`${BASE_URL}/api/device/status/summary`, deviceLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 7. DigitalTwin 服务
// ═══════════════════════════════════════════════════
function testDigitalTwin(headers) {
    group('DigitalTwin', () => {
        apiCall(`${BASE_URL}/api/digital-twin/overview`, digitalTwinLatency, headers);
        apiCall(`${BASE_URL}/api/digital-twin/models?page=1&pageSize=10`, digitalTwinLatency, headers);
        apiCall(`${BASE_URL}/api/digital-twin/scenes`, digitalTwinLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 8. Identity 服务
// ═══════════════════════════════════════════════════
function testIdentity(headers) {
    group('Identity', () => {
        apiCall(`${BASE_URL}/api/identity/users?page=1&pageSize=10`, identityLatency, headers);
        apiCall(`${BASE_URL}/api/auth/me`, identityLatency, headers);
        apiCall(`${BASE_URL}/api/identity/realname-auth/current`, identityLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 9. Ingestion 服务
// ═══════════════════════════════════════════════════
function testIngestion(headers) {
    group('Ingestion', () => {
        apiCall(`${BASE_URL}/api/ingestion/sources?page=1&pageSize=10`, ingestionLatency, headers);
        apiCall(`${BASE_URL}/api/ingestion/wal/status`, ingestionLatency, headers);
        apiCall(`${BASE_URL}/api/ingestion/batch/stats`, ingestionLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 10. IotCloudAI 服务
// ═══════════════════════════════════════════════════
function testIotCloudAI(headers) {
    group('IotCloudAI', () => {
        apiCall(`${BASE_URL}/api/iotcloudai/carbon/asset`, iotcloudaiLatency, headers);
        apiCall(`${BASE_URL}/api/iotcloudai/demand-response/events`, iotcloudaiLatency, headers);
        apiCall(`${BASE_URL}/api/iotcloudai/insight/dashboard`, iotcloudaiLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 11. Observability 服务
// ═══════════════════════════════════════════════════
function testObservability(headers) {
    group('Observability', () => {
        apiCall(`${BASE_URL}/api/observability/health`, observabilityLatency, headers);
        apiCall(`${BASE_URL}/api/observability/metrics`, observabilityLatency, headers);
        apiCall(`${BASE_URL}/api/observability/traces?page=1&pageSize=10`, observabilityLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 12. Permission 服务
// ═══════════════════════════════════════════════════
function testPermission(headers) {
    group('Permission', () => {
        apiCall(`${BASE_URL}/api/permission/roles?page=1&pageSize=10`, permissionLatency, headers);
        apiCall(`${BASE_URL}/api/permission/menus`, permissionLatency, headers);
        apiCall(`${BASE_URL}/api/permission/permissions?page=1&pageSize=10`, permissionLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 13. RuleEngine 服务
// ═══════════════════════════════════════════════════
function testRuleEngine(headers) {
    group('RuleEngine', () => {
        apiCall(`${BASE_URL}/api/ruleengine/chains?page=1&pageSize=10`, ruleengineLatency, headers);
        apiCall(`${BASE_URL}/api/ruleengine/execution/stats`, ruleengineLatency, headers);
        apiCall(`${BASE_URL}/api/ruleengine/alarm-definitions`, ruleengineLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 14. Settlement 服务
// ═══════════════════════════════════════════════════
function testSettlement(headers) {
    group('Settlement', () => {
        apiCall(`${BASE_URL}/api/settlement/records?page=1&pageSize=10`, settlementLatency, headers);
        apiCall(`${BASE_URL}/api/settlement/invoices?page=1&pageSize=10`, settlementLatency, headers);
        apiCall(`${BASE_URL}/api/settlement/overview`, settlementLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 15. Simulator 服务
// ═══════════════════════════════════════════════════
function testSimulator(headers) {
    group('Simulator', () => {
        apiCall(`${BASE_URL}/api/simulator/sessions?page=1&pageSize=10`, simulatorLatency, headers);
        apiCall(`${BASE_URL}/api/simulator/engines`, simulatorLatency, headers);
        apiCall(`${BASE_URL}/api/simulator/status`, simulatorLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 16. Station 服务
// ═══════════════════════════════════════════════════
function testStation(headers) {
    group('Station', () => {
        apiCall(`${BASE_URL}/api/station/list?page=1&pageSize=10`, stationLatency, headers);
        apiCall(`${BASE_URL}/api/station/overview`, stationLatency, headers);
        apiCall(`${BASE_URL}/api/station/options`, stationLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 17. Storage 服务
// ═══════════════════════════════════════════════════
function testStorage(headers) {
    group('Storage', () => {
        apiCall(`${BASE_URL}/api/storage/files?page=1&pageSize=10`, storageLatency, headers);
        apiCall(`${BASE_URL}/api/storage/buckets`, storageLatency, headers);
        apiCall(`${BASE_URL}/api/storage/usage`, storageLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 18. Tenant 服务
// ═══════════════════════════════════════════════════
function testTenant(headers) {
    group('Tenant', () => {
        apiCall(`${BASE_URL}/api/tenant/list?page=1&pageSize=10`, tenantLatency, headers);
        apiCall(`${BASE_URL}/api/tenant/current`, tenantLatency, headers);
        apiCall(`${BASE_URL}/api/tenant/config`, tenantLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 19. WorkOrder 服务
// ═══════════════════════════════════════════════════
function testWorkOrder(headers) {
    group('WorkOrder', () => {
        apiCall(`${BASE_URL}/api/workorder/list?page=1&pageSize=10`, workorderLatency, headers);
        apiCall(`${BASE_URL}/api/workorder/stats`, workorderLatency, headers);
        apiCall(`${BASE_URL}/api/workorder/types`, workorderLatency, headers);
    });
}

// ═══════════════════════════════════════════════════
// 20. Energy 子系统 (PVESSC + VPP + MicroGrid + 6个EnergyServices)
// ═══════════════════════════════════════════════════
function testEnergy(headers) {
    group('Energy', () => {
        // PVESSC
        apiCall(`${BASE_URL}/api/pvessc/dashboard`, energyLatency, headers);
        // VPP
        apiCall(`${BASE_URL}/api/vpp/list?page=1&pageSize=10`, energyLatency, headers);
        // MicroGrid
        apiCall(`${BASE_URL}/api/microgrid/overview`, energyLatency, headers);
        // EnergyServices
        apiCall(`${BASE_URL}/api/elec-trade/orders?page=1&pageSize=10`, energyLatency, headers);
        apiCall(`${BASE_URL}/api/carbon-trade/assets`, energyLatency, headers);
        apiCall(`${BASE_URL}/api/demand-resp/events`, energyLatency, headers);
        apiCall(`${BASE_URL}/api/device-ops/tasks?page=1&pageSize=10`, energyLatency, headers);
        apiCall(`${BASE_URL}/api/energy-eff/reports?page=1&pageSize=10`, energyLatency, headers);
        apiCall(`${BASE_URL}/api/safe-control/alerts?page=1&pageSize=10`, energyLatency, headers);
    });
}
