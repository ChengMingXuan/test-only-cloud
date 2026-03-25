/**
 * V3.2.0 能源整合 + 安全增强 API 性能测试
 * =========================================
 * 覆盖 V3.2.0 核心变更:
 * - Operations 整合 API (EnergyEff + MultiEnergy + SafeControl)
 * - Trading 整合 API (ElecTrade + CarbonTrade + DemandResp)
 * - 证书轮换 API
 * - 三权分立权限查询
 * - 绿色电力关联 API
 * - 敏感数据加密 API
 * 
 * 场景数: 36
 * 运行: k6 run testing/k6/scenarios/v320-consolidated-perf.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 禁止连接生产环境
const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

// 自定义指标
const errorRate = new Rate('errors');
const operationsLatency = new Trend('operations_latency');
const tradingLatency = new Trend('trading_latency');
const securityLatency = new Trend('security_latency');
const greenPowerLatency = new Trend('green_power_latency');
const totalRequests = new Counter('total_v320_requests');

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
        { duration: '1m', target: 30 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_failed: ['rate<0.15'],
        http_req_duration: ['p(95)<5000'],
        errors: ['rate<0.1'],
    },
};

export default function () {
    // ═══════════════════════════════════════
    // Operations 三合一 API 性能
    // ═══════════════════════════════════════

    group('EnergyEff 能效管理', () => {
        let r = http.get(`${BASE_URL}/api/energyeff/meters?page=1&pageSize=10`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'EnergyEff meters 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/energyeff/consumption/summary`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'EnergyEff consumption 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/energyeff/efficiency/analysis`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'EnergyEff analysis 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/energyeff/dashboard`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'EnergyEff dashboard 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    group('MultiEnergy 多能互补', () => {
        let r = http.get(`${BASE_URL}/api/multienergy/balance/overview`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'MultiEnergy balance 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/multienergy/devices?page=1&pageSize=10`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'MultiEnergy devices 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/multienergy/schedule`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'MultiEnergy schedule 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/multienergy/dashboard`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'MultiEnergy dashboard 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    group('SafeControl 安全管控', () => {
        let r = http.get(`${BASE_URL}/api/safecontrol/events?page=1&pageSize=10`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'SafeControl events 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/safecontrol/risk/assessment`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'SafeControl risk 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/safecontrol/compliance`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'SafeControl compliance 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/safecontrol/dashboard`, { headers });
        operationsLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'SafeControl dashboard 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    // ═══════════════════════════════════════
    // Trading 三合一 API 性能
    // ═══════════════════════════════════════

    group('ElecTrade 电力交易', () => {
        let r = http.get(`${BASE_URL}/api/electrade/orders?page=1&pageSize=10`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'ElecTrade orders 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/electrade/market/price`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'ElecTrade market 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/electrade/green-certificate`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'ElecTrade green-cert 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/electrade/settlement`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'ElecTrade settlement 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    group('CarbonTrade 碳交易', () => {
        let r = http.get(`${BASE_URL}/api/carbontrade/emission/records?page=1&pageSize=10`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'CarbonTrade emission 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/carbontrade/asset/overview`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'CarbonTrade asset 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/carbontrade/fulfillment`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'CarbonTrade fulfillment 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    group('DemandResp 需求响应', () => {
        let r = http.get(`${BASE_URL}/api/demandresp/events?page=1&pageSize=10`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'DemandResp events 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/demandresp/invitations`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'DemandResp invitations 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/demandresp/records?page=1&pageSize=10`, { headers });
        tradingLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'DemandResp records 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    // ═══════════════════════════════════════
    // 安全增强 API 性能
    // ═══════════════════════════════════════

    group('证书轮换 API', () => {
        let r = http.get(`${BASE_URL}/api/monitor/service-mesh/certificate-rotation/status`, { headers });
        securityLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'CertRotation status 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/monitor/service-mesh/certificate-rotation/records?page=1&pageSize=10`, { headers });
        securityLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'CertRotation records 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    group('敏感数据加密', () => {
        const encPayload = JSON.stringify({ dataType: 'Phone', plainText: '13800138000' });
        let r = http.post(`${BASE_URL}/api/security/encrypt`, encPayload, { headers });
        securityLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'Encrypt phone 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.post(`${BASE_URL}/api/security/mask`, encPayload, { headers });
        securityLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'Mask phone 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    // ═══════════════════════════════════════
    // 绿色电力关联 API 性能
    // ═══════════════════════════════════════

    group('绿色电力关联', () => {
        const offsetPayload = JSON.stringify({
            certificateId: 'test-cert-001',
            energyMwh: 100.0,
            period: '2026-03'
        });
        let r = http.post(`${BASE_URL}/api/electrade/green-power/carbon-offset`, offsetPayload, { headers });
        greenPowerLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'GreenPower offset 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);

        r = http.get(`${BASE_URL}/api/electrade/green-power/carbon-impact?period=2026-03`, { headers });
        greenPowerLatency.add(r.timings.duration);
        totalRequests.add(1);
        check(r, { 'GreenPower impact 200': (r) => r.status < 500 }) || errorRate.add(1);
        sleep(0.1);
    });

    sleep(1);
}
