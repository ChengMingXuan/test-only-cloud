/**
 * V3.2.0 增量性能测试 — Operations + Trading 统一入口负载测试
 * ===========================================================
 * k6 压测场景：覆盖 V3.2.0 运维/交易整合后的 API 端点
 * 
 * 运行方式:
 *   k6 run --env BASE_URL=http://localhost:8000 v320-operations-trading-load.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// 自定义指标
const operationsSuccess = new Rate('operations_api_success');
const tradingSuccess = new Rate('trading_api_success');
const dashboardLatency = new Trend('dashboard_latency_ms');
const listLatency = new Trend('list_latency_ms');
const createLatency = new Trend('create_latency_ms');
const totalRequests = new Counter('total_api_requests');

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// ═══════════════════════════════════════════════════
// 测试选项：3 级负载 (smoke → load → stress)
// ═══════════════════════════════════════════════════

export let options = {
    scenarios: {
        // Smoke: 基本可用性
        smoke: {
            executor: 'constant-vus',
            vus: 3,
            duration: '1m',
            startTime: '0s',
            tags: { phase: 'smoke' },
        },
        // Load: 常规负载
        load: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 20 },  // 爬升
                { duration: '3m', target: 20 },  // 稳态
                { duration: '1m', target: 0 },   // 冷却
            ],
            startTime: '1m',
            tags: { phase: 'load' },
        },
        // Stress: 高压
        stress: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 50 },
                { duration: '2m', target: 50 },
                { duration: '1m', target: 0 },
            ],
            startTime: '6m',
            tags: { phase: 'stress' },
        },
    },
    thresholds: {
        'http_req_duration': ['p(95)<5000'],        // P95 < 5s
        'http_req_failed': ['rate<0.10'],            // 失败率 < 10%
        'operations_api_success': ['rate>0.90'],     // Operations API 成功率 > 90%
        'trading_api_success': ['rate>0.90'],        // Trading API 成功率 > 90%
        'dashboard_latency_ms': ['p(95)<3000'],      // 仪表盘 P95 < 3s
        'list_latency_ms': ['p(95)<2000'],           // 列表 P95 < 2s
    },
};

// ═══════════════════════════════════════════════════
// 模拟登录获取 Token (Mock)
// ═══════════════════════════════════════════════════

function getAuthHeaders() {
    // 尝试真实登录
    const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
        username: 'admin',
        password: 'Admin@123456',
        tenantCode: 'default',
    }), { headers: { 'Content-Type': 'application/json' }, timeout: '10s' });

    if (loginRes.status === 200) {
        try {
            const body = JSON.parse(loginRes.body);
            if (body.data && body.data.accessToken) {
                return {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${body.data.accessToken}`,
                };
            }
        } catch (e) { /* fallthrough */ }
    }

    // fallback: 使用 Mock Token
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock-k6-token',
    };
}

// ═══════════════════════════════════════════════════
// Operations API 端点测试
// ═══════════════════════════════════════════════════

function testOperationsDashboard(headers) {
    group('Operations Dashboard', () => {
        const res = http.get(`${BASE_URL}/api/operations/dashboard`, { headers, timeout: '10s' });
        const ok = check(res, {
            'dashboard status < 500': (r) => r.status < 500,
            'dashboard latency < 5s': (r) => r.timings.duration < 5000,
        });
        operationsSuccess.add(ok);
        dashboardLatency.add(res.timings.duration);
        totalRequests.add(1);
    });
}

function testOperationsEnergyEff(headers) {
    group('Operations EnergyEff', () => {
        // 列表查询
        const listRes = http.get(
            `${BASE_URL}/api/operations/energyeff?page=${randomIntBetween(1, 5)}&pageSize=20`,
            { headers, timeout: '10s' }
        );
        check(listRes, { 'energyeff list < 500': (r) => r.status < 500 });
        operationsSuccess.add(listRes.status < 500);
        listLatency.add(listRes.timings.duration);
        totalRequests.add(1);

        sleep(0.3);

        // 创建（10% 概率）
        if (randomIntBetween(1, 10) === 1) {
            const createRes = http.post(`${BASE_URL}/api/operations/energyeff`, JSON.stringify({
                name: `k6-energyeff-${Date.now()}`,
                type: 'optimization',
                targetEfficiency: 0.92,
            }), { headers, timeout: '10s' });
            check(createRes, { 'energyeff create < 500': (r) => r.status < 500 });
            createLatency.add(createRes.timings.duration);
            totalRequests.add(1);
        }
    });
}

function testOperationsMultiEnergy(headers) {
    group('Operations MultiEnergy', () => {
        const res = http.get(
            `${BASE_URL}/api/operations/multienergy?page=1&pageSize=20`,
            { headers, timeout: '10s' }
        );
        check(res, { 'multienergy list < 500': (r) => r.status < 500 });
        operationsSuccess.add(res.status < 500);
        listLatency.add(res.timings.duration);
        totalRequests.add(1);
    });
}

function testOperationsSafeControl(headers) {
    group('Operations SafeControl', () => {
        const res = http.get(
            `${BASE_URL}/api/operations/safecontrol?page=1&pageSize=20`,
            { headers, timeout: '10s' }
        );
        check(res, { 'safecontrol list < 500': (r) => r.status < 500 });
        operationsSuccess.add(res.status < 500);
        listLatency.add(res.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// Trading API 端点测试
// ═══════════════════════════════════════════════════

function testTradingDashboard(headers) {
    group('Trading Dashboard', () => {
        const res = http.get(`${BASE_URL}/api/trading/dashboard`, { headers, timeout: '10s' });
        const ok = check(res, {
            'trading dashboard < 500': (r) => r.status < 500,
            'trading dashboard latency < 5s': (r) => r.timings.duration < 5000,
        });
        tradingSuccess.add(ok);
        dashboardLatency.add(res.timings.duration);
        totalRequests.add(1);
    });
}

function testTradingElecTrade(headers) {
    group('Trading ElecTrade', () => {
        const listRes = http.get(
            `${BASE_URL}/api/trading/electrade?page=${randomIntBetween(1, 5)}&pageSize=20`,
            { headers, timeout: '10s' }
        );
        check(listRes, { 'electrade list < 500': (r) => r.status < 500 });
        tradingSuccess.add(listRes.status < 500);
        listLatency.add(listRes.timings.duration);
        totalRequests.add(1);

        sleep(0.3);

        // 创建订单（5% 概率）
        if (randomIntBetween(1, 20) === 1) {
            const createRes = http.post(`${BASE_URL}/api/trading/electrade`, JSON.stringify({
                orderId: `k6-ET-${Date.now()}`,
                price: (Math.random() * 0.5 + 0.3).toFixed(4),
                volume: randomIntBetween(100, 5000),
                type: 'spot',
            }), { headers, timeout: '10s' });
            check(createRes, { 'electrade create < 500': (r) => r.status < 500 });
            createLatency.add(createRes.timings.duration);
            totalRequests.add(1);
        }
    });
}

function testTradingCarbonTrade(headers) {
    group('Trading CarbonTrade', () => {
        const res = http.get(
            `${BASE_URL}/api/trading/carbontrade?page=1&pageSize=20`,
            { headers, timeout: '10s' }
        );
        check(res, { 'carbontrade list < 500': (r) => r.status < 500 });
        tradingSuccess.add(res.status < 500);
        listLatency.add(res.timings.duration);
        totalRequests.add(1);
    });
}

function testTradingDemandResp(headers) {
    group('Trading DemandResp', () => {
        const res = http.get(
            `${BASE_URL}/api/trading/demandresp?page=1&pageSize=20`,
            { headers, timeout: '10s' }
        );
        check(res, { 'demandresp list < 500': (r) => r.status < 500 });
        tradingSuccess.add(res.status < 500);
        listLatency.add(res.timings.duration);
        totalRequests.add(1);
    });
}

function testTradingMarketPrice(headers) {
    group('Trading Market Price', () => {
        const res = http.get(
            `${BASE_URL}/api/trading/market/price?period=hourly`,
            { headers, timeout: '10s' }
        );
        check(res, { 'market price < 500': (r) => r.status < 500 });
        tradingSuccess.add(res.status < 500);
        listLatency.add(res.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 主测试函数
// ═══════════════════════════════════════════════════

export function setup() {
    console.log('🚀 V3.2.0 Operations/Trading 增量性能测试启动');
    console.log(`   BASE_URL: ${BASE_URL}`);
    return { startTime: new Date().toISOString() };
}

export default function () {
    const headers = getAuthHeaders();

    // 随机执行 Operations 或 Trading 场景
    const scenario = randomIntBetween(1, 100);

    if (scenario <= 15) {
        testOperationsDashboard(headers);
    } else if (scenario <= 30) {
        testOperationsEnergyEff(headers);
    } else if (scenario <= 38) {
        testOperationsMultiEnergy(headers);
    } else if (scenario <= 46) {
        testOperationsSafeControl(headers);
    } else if (scenario <= 60) {
        testTradingDashboard(headers);
    } else if (scenario <= 75) {
        testTradingElecTrade(headers);
    } else if (scenario <= 83) {
        testTradingCarbonTrade(headers);
    } else if (scenario <= 91) {
        testTradingDemandResp(headers);
    } else {
        testTradingMarketPrice(headers);
    }

    sleep(randomIntBetween(500, 2000) / 1000);
}

export function teardown(data) {
    console.log('✅ V3.2.0 增量性能测试完成');
    console.log(`   开始: ${data.startTime}`);
    console.log(`   结束: ${new Date().toISOString()}`);
}

export function handleSummary(data) {
    return {
        'results/v320-operations-trading-results.json': JSON.stringify(data, null, 2),
        stdout: textSummary(data, { indent: ' ', enableColors: true }),
    };
}
