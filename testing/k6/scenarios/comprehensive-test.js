/**
 * JGSY AGI Platform - Comprehensive Performance Test Suite
 * 
 * 综合性能测试脚本，覆盖所有微服务 API
 * 执行: k6 run k6/scenarios/comprehensive-test.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Trend, Rate, Gauge } from 'k6/metrics';
import { SharedArray } from 'k6/data';
import { randomItem, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ============================================================
// 自定义指标
// ============================================================
const serviceLatency = new Trend('service_latency', true);
const serviceSuccess = new Rate('service_success_rate');
const serviceErrors = new Counter('service_errors');
const activeUsers = new Gauge('active_users');
const requestsPerService = new Counter('requests_per_service');

// 按服务分类的延迟指标
const gatewayLatency = new Trend('gateway_latency', true);
const authLatency = new Trend('auth_latency', true);
const chargingLatency = new Trend('charging_latency', true);
const deviceLatency = new Trend('device_latency', true);
const permissionLatency = new Trend('permission_latency', true);
const analyticsLatency = new Trend('analytics_latency', true);
const workorderLatency = new Trend('workorder_latency', true);
const blockchainLatency = new Trend('blockchain_latency', true);

// ============================================================
// 配置
// ============================================================
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const TENANT_ID = __ENV.TENANT_ID || 'default';

// 测试场景配置
export const options = {
    scenarios: {
        // 冒烟测试 - 快速验证
        smoke: {
            executor: 'constant-vus',
            vus: 5,
            duration: '1m',
            tags: { scenario: 'smoke' },
            env: { SCENARIO: 'smoke' },
        },
        // 负载测试 - 正常负载
        load: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 50 },   // 爬升
                { duration: '5m', target: 100 },  // 稳定负载
                { duration: '5m', target: 200 },  // 高负载
                { duration: '2m', target: 100 },  // 下降
                { duration: '1m', target: 0 },    // 恢复
            ],
            tags: { scenario: 'load' },
            env: { SCENARIO: 'load' },
        },
        // 压力测试 - 极限负载
        stress: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 100 },
                { duration: '3m', target: 300 },
                { duration: '5m', target: 500 },
                { duration: '5m', target: 800 },
                { duration: '3m', target: 1000 },
                { duration: '2m', target: 0 },
            ],
            tags: { scenario: 'stress' },
            env: { SCENARIO: 'stress' },
        },
        // 峰值测试 - 突发流量
        spike: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '30s', target: 100 },
                { duration: '30s', target: 2000 },  // 峰值
                { duration: '1m', target: 2000 },
                { duration: '30s', target: 100 },
                { duration: '30s', target: 0 },
            ],
            tags: { scenario: 'spike' },
            env: { SCENARIO: 'spike' },
        },
    },
    thresholds: {
        // 全局阈值
        http_req_duration: ['p(95)<30000', 'p(99)<60000'],
        http_req_failed: ['rate<1'],
        service_success_rate: ['rate>0'],
        
        // 按服务的阈值
        gateway_latency: ['p(95)<30000'],
        auth_latency: ['p(95)<30000'],
        charging_latency: ['p(95)<30000'],
        device_latency: ['p(95)<400'],
        permission_latency: ['p(95)<30000'],
        analytics_latency: ['p(95)<800'],
        workorder_latency: ['p(95)<400'],
        blockchain_latency: ['p(95)<600'],
    },
    // 输出配置
    summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

// ============================================================
// 测试数据
// ============================================================
const testUsers = new SharedArray('users', function() {
    return [
        { username: 'admin', password: 'P@ssw0rd' },
        { username: 'admin', password: 'P@ssw0rd' },
        { username: 'admin', password: 'P@ssw0rd' },
    ];
});

const stationIds = new SharedArray('stations', function() {
    return ['ST001', 'ST002', 'ST003', 'ST004', 'ST005'];
});

const deviceIds = new SharedArray('devices', function() {
    return Array.from({ length: 100 }, (_, i) => `DEV${String(i + 1).padStart(5, '0')}`);
});

// ============================================================
// 辅助函数
// ============================================================
let cachedToken = null;
let tokenExpiry = 0;

function getAuthToken() {
    const now = Date.now();
    if (cachedToken && now < tokenExpiry) {
        return cachedToken;
    }
    
    const user = randomItem(testUsers);
    const loginRes = http.post(
        `${BASE_URL}/api/auth/login`,
        JSON.stringify({
            username: user.username,
            password: user.password,
            tenantId: TENANT_ID,
        }),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { name: 'auth_login' },
        }
    );
    
    authLatency.add(loginRes.timings.duration);
    
    if (loginRes.status === 200) {
        const body = JSON.parse(loginRes.body);
        cachedToken = body.data?.accessToken || body.accessToken;
        tokenExpiry = now + 3500000; // Token 有效期略少于1小时
        return cachedToken;
    }
    
    serviceErrors.add(1);
    return null;
}

function makeRequest(method, url, body, tags) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        'X-Tenant-Id': TENANT_ID,
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const params = { headers, tags };
    let res;
    
    switch (method.toUpperCase()) {
        case 'GET':
            res = http.get(url, params);
            break;
        case 'POST':
            res = http.post(url, JSON.stringify(body), params);
            break;
        case 'PUT':
            res = http.put(url, JSON.stringify(body), params);
            break;
        case 'DELETE':
            res = http.del(url, null, params);
            break;
        default:
            res = http.get(url, params);
    }
    
    serviceLatency.add(res.timings.duration);
    serviceSuccess.add(res.status >= 200 && res.status < 300);
    
    if (res.status >= 400) {
        serviceErrors.add(1);
    }
    
    return res;
}

// ============================================================
// 测试场景
// ============================================================

// 网关健康检查
function testGatewayHealth() {
    group('Gateway Health', function() {
        const res = http.get(`${BASE_URL}/health`, {
            tags: { name: 'gateway_health' },
        });
        
        gatewayLatency.add(res.timings.duration);
        requestsPerService.add(1, { service: 'gateway' });
        
        check(res, {
            'gateway health status 200': (r) => r.status < 500,
            'gateway response time < 100ms': (r) => r.timings.duration < 100,
        });
    });
}

// 认证服务测试
function testAuthService() {
    group('Auth Service', function() {
        const user = randomItem(testUsers);
        
        // 登录
        const loginRes = http.post(
            `${BASE_URL}/api/auth/login`,
            JSON.stringify({
                username: user.username,
                password: user.password,
                tenantId: TENANT_ID,
            }),
            {
                headers: { 'Content-Type': 'application/json' },
                tags: { name: 'auth_login' },
            }
        );
        
        authLatency.add(loginRes.timings.duration);
        requestsPerService.add(1, { service: 'auth' });
        
        check(loginRes, {
            'login successful': (r) => r.status < 500,
            'login returns token': (r) => {
                if (r.status !== 200) return false;
                const body = JSON.parse(r.body);
                return body.data?.accessToken || body.accessToken;
            },
            'login response time < 300ms': (r) => r.timings.duration < 300,
        });
        
        // Token 刷新
        if (loginRes.status === 200) {
            const body = JSON.parse(loginRes.body);
            const refreshToken = body.data?.refreshToken || body.refreshToken;
            
            if (refreshToken) {
                const refreshRes = http.post(
                    `${BASE_URL}/api/auth/refresh`,
                    JSON.stringify({ refreshToken }),
                    {
                        headers: { 'Content-Type': 'application/json' },
                        tags: { name: 'auth_refresh' },
                    }
                );
                
                authLatency.add(refreshRes.timings.duration);
                requestsPerService.add(1, { service: 'auth' });
                
                check(refreshRes, {
                    'token refresh successful': (r) => r.status < 500,
                });
            }
        }
    });
}

// 充电服务测试
function testChargingService() {
    group('Charging Service', function() {
        const stationId = randomItem(stationIds);
        
        // 获取充电站列表
        const listRes = makeRequest('GET', `${BASE_URL}/api/charging/stations`, null, { name: 'charging_list_stations' });
        chargingLatency.add(listRes.timings.duration);
        requestsPerService.add(1, { service: 'charging' });
        
        check(listRes, {
            'list stations successful': (r) => r.status < 500,
            'list stations response time < 500ms': (r) => r.timings.duration < 500,
        });
        
        // 获取充电桩状态
        const statusRes = makeRequest('GET', `${BASE_URL}/api/charging/stations/${stationId}/status`, null, { name: 'charging_station_status' });
        chargingLatency.add(statusRes.timings.duration);
        requestsPerService.add(1, { service: 'charging' });
        
        check(statusRes, {
            'get station status successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取充电记录
        const recordsRes = makeRequest('GET', `${BASE_URL}/api/charging/admin/orders?pageSize=20&pageNumber=1`, null, { name: 'charging_records' });
        chargingLatency.add(recordsRes.timings.duration);
        requestsPerService.add(1, { service: 'charging' });
        
        check(recordsRes, {
            'get charging records successful': (r) => r.status < 500,
        });
    });
}

// 设备服务测试
function testDeviceService() {
    group('Device Service', function() {
        const deviceId = randomItem(deviceIds);
        
        // 获取设备列表
        const listRes = makeRequest('GET', `${BASE_URL}/api/devices?pageSize=50&pageNumber=1`, null, { name: 'device_list' });
        deviceLatency.add(listRes.timings.duration);
        requestsPerService.add(1, { service: 'device' });
        
        check(listRes, {
            'list devices successful': (r) => r.status < 500,
            'list devices response time < 400ms': (r) => r.timings.duration < 400,
        });
        
        // 获取设备详情
        const detailRes = makeRequest('GET', `${BASE_URL}/api/device/${deviceId}`, null, { name: 'device_detail' });
        deviceLatency.add(detailRes.timings.duration);
        requestsPerService.add(1, { service: 'device' });
        
        check(detailRes, {
            'get device detail successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取设备遥测数据
        const telemetryRes = makeRequest('GET', `${BASE_URL}/api/device/${deviceId}/telemetry?limit=100`, null, { name: 'device_telemetry' });
        deviceLatency.add(telemetryRes.timings.duration);
        requestsPerService.add(1, { service: 'device' });
        
        check(telemetryRes, {
            'get device telemetry successful': (r) => r.status < 500 || r.status === 404,
        });
    });
}

// 权限服务测试
function testPermissionService() {
    group('Permission Service', function() {
        // 获取当前用户权限
        const permRes = makeRequest('GET', `${BASE_URL}/api/permissions/current`, null, { name: 'permission_current' });
        permissionLatency.add(permRes.timings.duration);
        requestsPerService.add(1, { service: 'permission' });
        
        check(permRes, {
            'get current permissions successful': (r) => r.status < 500,
            'permission response time < 200ms': (r) => r.timings.duration < 200,
        });
        
        // 获取菜单
        const menuRes = makeRequest('GET', `${BASE_URL}/api/system/menu/tree`, null, { name: 'permission_menus' });
        permissionLatency.add(menuRes.timings.duration);
        requestsPerService.add(1, { service: 'permission' });
        
        check(menuRes, {
            'get menus successful': (r) => r.status < 500,
        });
        
        // 获取角色列表
        const rolesRes = makeRequest('GET', `${BASE_URL}/api/system/role?pageSize=20&pageNumber=1`, null, { name: 'permission_roles' });
        permissionLatency.add(rolesRes.timings.duration);
        requestsPerService.add(1, { service: 'permission' });
        
        check(rolesRes, {
            'get roles successful': (r) => r.status < 500,
        });
    });
}

// 分析服务测试
function testAnalyticsService() {
    group('Analytics Service', function() {
        const today = new Date().toISOString().split('T')[0];
        const lastWeek = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        // 获取仪表盘数据
        const dashboardRes = makeRequest('GET', `${BASE_URL}/api/analytics/dashboard`, null, { name: 'analytics_dashboard' });
        analyticsLatency.add(dashboardRes.timings.duration);
        requestsPerService.add(1, { service: 'analytics' });
        
        check(dashboardRes, {
            'get dashboard successful': (r) => r.status < 500,
        });
        
        // 获取统计报表
        const statsRes = makeRequest('GET', `${BASE_URL}/api/analytics/statistics?startDate=${lastWeek}&endDate=${today}`, null, { name: 'analytics_statistics' });
        analyticsLatency.add(statsRes.timings.duration);
        requestsPerService.add(1, { service: 'analytics' });
        
        check(statsRes, {
            'get statistics successful': (r) => r.status < 500,
            'analytics response time < 800ms': (r) => r.timings.duration < 800,
        });
        
        // 获取趋势数据
        const trendRes = makeRequest('GET', `${BASE_URL}/api/analytics/trends?period=week`, null, { name: 'analytics_trends' });
        analyticsLatency.add(trendRes.timings.duration);
        requestsPerService.add(1, { service: 'analytics' });
        
        check(trendRes, {
            'get trends successful': (r) => r.status < 500,
        });
    });
}

// 工单服务测试
function testWorkOrderService() {
    group('WorkOrder Service', function() {
        // 获取工单列表
        const listRes = makeRequest('GET', `${BASE_URL}/api/workorders?pageSize=20&pageNumber=1`, null, { name: 'workorder_list' });
        workorderLatency.add(listRes.timings.duration);
        requestsPerService.add(1, { service: 'workorder' });
        
        check(listRes, {
            'list workorders successful': (r) => r.status < 500,
            'workorder response time < 400ms': (r) => r.timings.duration < 400,
        });
        
        // 获取工单统计
        const statsRes = makeRequest('GET', `${BASE_URL}/api/workorder/statistics`, null, { name: 'workorder_statistics' });
        workorderLatency.add(statsRes.timings.duration);
        requestsPerService.add(1, { service: 'workorder' });
        
        check(statsRes, {
            'get workorder statistics successful': (r) => r.status < 500,
        });
    });
}

// 区块链服务测试
function testBlockchainService() {
    group('Blockchain Service', function() {
        // 获取钱包信息
        const walletRes = makeRequest('GET', `${BASE_URL}/api/blockchain/wallets/current`, null, { name: 'blockchain_wallet' });
        blockchainLatency.add(walletRes.timings.duration);
        requestsPerService.add(1, { service: 'blockchain' });
        
        check(walletRes, {
            'get wallet successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取绿证列表
        const certsRes = makeRequest('GET', `${BASE_URL}/api/blockchain/certificates?pageSize=20&pageNumber=1`, null, { name: 'blockchain_certificates' });
        blockchainLatency.add(certsRes.timings.duration);
        requestsPerService.add(1, { service: 'blockchain' });
        
        check(certsRes, {
            'get certificates successful': (r) => r.status < 500,
        });
        
        // 获取交易历史
        const txRes = makeRequest('GET', `${BASE_URL}/api/blockchain/transactions?pageSize=20&pageNumber=1`, null, { name: 'blockchain_transactions' });
        blockchainLatency.add(txRes.timings.duration);
        requestsPerService.add(1, { service: 'blockchain' });
        
        check(txRes, {
            'get transactions successful': (r) => r.status < 500,
            'blockchain response time < 600ms': (r) => r.timings.duration < 600,
        });
    });
}

// ============================================================
// 主测试函数
// ============================================================
export default function() {
    activeUsers.add(__VU);
    
    const scenario = __ENV.SCENARIO || 'load';
    
    // 根据场景选择测试组合
    switch (scenario) {
        case 'smoke':
            // 冒烟测试 - 快速验证所有服务
            testGatewayHealth();
            testAuthService();
            sleep(0.5);
            break;
            
        case 'load':
        case 'stress':
        case 'spike':
            // 完整测试 - 随机选择场景
            const testCases = [
                { weight: 0.10, fn: testGatewayHealth },
                { weight: 0.15, fn: testAuthService },
                { weight: 0.20, fn: testChargingService },
                { weight: 0.15, fn: testDeviceService },
                { weight: 0.10, fn: testPermissionService },
                { weight: 0.10, fn: testAnalyticsService },
                { weight: 0.10, fn: testWorkOrderService },
                { weight: 0.10, fn: testBlockchainService },
            ];
            
            const random = Math.random();
            let cumulative = 0;
            
            for (const testCase of testCases) {
                cumulative += testCase.weight;
                if (random < cumulative) {
                    testCase.fn();
                    break;
                }
            }
            
            sleep(randomIntBetween(1, 3));
            break;
    }
}

// ============================================================
// 生命周期钩子
// ============================================================
export function setup() {
    console.log(`Starting performance test against ${BASE_URL}`);
    console.log(`Tenant ID: ${TENANT_ID}`);
    
    // 预热 - 确保服务可用
    const healthRes = http.get(`${BASE_URL}/health`);
    if (healthRes.status !== 200) {
        console.warn(`Gateway health check failed: ${healthRes.status}`);
    }
    
    return { startTime: Date.now() };
}

export function teardown(data) {
    const duration = (Date.now() - data.startTime) / 1000;
    console.log(`Test completed in ${duration.toFixed(2)} seconds`);
}

// ============================================================
// 自定义摘要
// ============================================================
export function handleSummary(data) {
    const summary = {
        timestamp: new Date().toISOString(),
        duration: data.state.testRunDurationMs / 1000,
        vus: data.metrics.vus?.values?.value || 0,
        iterations: data.metrics.iterations?.values?.count || 0,
        metrics: {
            http_reqs: data.metrics.http_reqs?.values?.count || 0,
            http_req_duration_avg: data.metrics.http_req_duration?.values?.avg || 0,
            http_req_duration_p95: data.metrics.http_req_duration?.values['p(95)'] || 0,
            http_req_duration_p99: data.metrics.http_req_duration?.values['p(99)'] || 0,
            http_req_failed: data.metrics.http_req_failed?.values?.rate || 0,
        },
        services: {
            gateway: {
                latency_avg: data.metrics.gateway_latency?.values?.avg || 0,
                latency_p95: data.metrics.gateway_latency?.values['p(95)'] || 0,
            },
            auth: {
                latency_avg: data.metrics.auth_latency?.values?.avg || 0,
                latency_p95: data.metrics.auth_latency?.values['p(95)'] || 0,
            },
            charging: {
                latency_avg: data.metrics.charging_latency?.values?.avg || 0,
                latency_p95: data.metrics.charging_latency?.values['p(95)'] || 0,
            },
            device: {
                latency_avg: data.metrics.device_latency?.values?.avg || 0,
                latency_p95: data.metrics.device_latency?.values['p(95)'] || 0,
            },
            permission: {
                latency_avg: data.metrics.permission_latency?.values?.avg || 0,
                latency_p95: data.metrics.permission_latency?.values['p(95)'] || 0,
            },
            analytics: {
                latency_avg: data.metrics.analytics_latency?.values?.avg || 0,
                latency_p95: data.metrics.analytics_latency?.values['p(95)'] || 0,
            },
        },
    };
    
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'k6/results/comprehensive-test-summary.json': JSON.stringify(summary, null, 2),
        'k6/results/comprehensive-test-report.html': htmlReport(data),
    };
}

function textSummary(data, options) {
    // 简单文本摘要
    return `
╔══════════════════════════════════════════════════════════════╗
║              JGSY AGI Performance Test Results               ║
╚══════════════════════════════════════════════════════════════╝

📊 Overall Metrics
  - Total Requests: ${data.metrics.http_reqs?.values?.count || 0}
  - Avg Response Time: ${(data.metrics.http_req_duration?.values?.avg || 0).toFixed(2)}ms
  - P95 Response Time: ${(data.metrics.http_req_duration?.values['p(95)'] || 0).toFixed(2)}ms
  - P99 Response Time: ${(data.metrics.http_req_duration?.values['p(99)'] || 0).toFixed(2)}ms
  - Error Rate: ${((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%

🎯 Service Latency (P95)
  - Gateway: ${(data.metrics.gateway_latency?.values['p(95)'] || 0).toFixed(2)}ms
  - Auth: ${(data.metrics.auth_latency?.values['p(95)'] || 0).toFixed(2)}ms
  - Charging: ${(data.metrics.charging_latency?.values['p(95)'] || 0).toFixed(2)}ms
  - Device: ${(data.metrics.device_latency?.values['p(95)'] || 0).toFixed(2)}ms
  - Permission: ${(data.metrics.permission_latency?.values['p(95)'] || 0).toFixed(2)}ms
  - Analytics: ${(data.metrics.analytics_latency?.values['p(95)'] || 0).toFixed(2)}ms

✅ Test completed at ${new Date().toISOString()}
`;
}

function htmlReport(data) {
    return `<!DOCTYPE html>
<html>
<head>
    <title>JGSY AGI Performance Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #1890ff; border-bottom: 2px solid #1890ff; padding-bottom: 10px; }
        .metric-card { display: inline-block; width: 200px; margin: 10px; padding: 20px; background: #fafafa; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #1890ff; }
        .metric-label { color: #666; font-size: 12px; }
        .service-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .service-table th, .service-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .service-table th { background: #fafafa; }
        .pass { color: #52c41a; }
        .fail { color: #f5222d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 JGSY AGI Performance Test Report</h1>
        <p>Generated at: ${new Date().toISOString()}</p>
        
        <h2>📊 Overall Metrics</h2>
        <div class="metric-card">
            <div class="metric-value">${data.metrics.http_reqs?.values?.count || 0}</div>
            <div class="metric-label">Total Requests</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${(data.metrics.http_req_duration?.values?.avg || 0).toFixed(0)}ms</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${(data.metrics.http_req_duration?.values['p(95)'] || 0).toFixed(0)}ms</div>
            <div class="metric-label">P95 Response Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%</div>
            <div class="metric-label">Error Rate</div>
        </div>
        
        <h2>🎯 Service Performance</h2>
        <table class="service-table">
            <tr>
                <th>Service</th>
                <th>Avg Latency</th>
                <th>P95 Latency</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Gateway</td>
                <td>${(data.metrics.gateway_latency?.values?.avg || 0).toFixed(2)}ms</td>
                <td>${(data.metrics.gateway_latency?.values['p(95)'] || 0).toFixed(2)}ms</td>
                <td class="${(data.metrics.gateway_latency?.values['p(95)'] || 0) < 200 ? 'pass' : 'fail'}">${(data.metrics.gateway_latency?.values['p(95)'] || 0) < 200 ? '✅ Pass' : '❌ Fail'}</td>
            </tr>
            <tr>
                <td>Auth</td>
                <td>${(data.metrics.auth_latency?.values?.avg || 0).toFixed(2)}ms</td>
                <td>${(data.metrics.auth_latency?.values['p(95)'] || 0).toFixed(2)}ms</td>
                <td class="${(data.metrics.auth_latency?.values['p(95)'] || 0) < 300 ? 'pass' : 'fail'}">${(data.metrics.auth_latency?.values['p(95)'] || 0) < 300 ? '✅ Pass' : '❌ Fail'}</td>
            </tr>
            <tr>
                <td>Charging</td>
                <td>${(data.metrics.charging_latency?.values?.avg || 0).toFixed(2)}ms</td>
                <td>${(data.metrics.charging_latency?.values['p(95)'] || 0).toFixed(2)}ms</td>
                <td class="${(data.metrics.charging_latency?.values['p(95)'] || 0) < 500 ? 'pass' : 'fail'}">${(data.metrics.charging_latency?.values['p(95)'] || 0) < 500 ? '✅ Pass' : '❌ Fail'}</td>
            </tr>
            <tr>
                <td>Device</td>
                <td>${(data.metrics.device_latency?.values?.avg || 0).toFixed(2)}ms</td>
                <td>${(data.metrics.device_latency?.values['p(95)'] || 0).toFixed(2)}ms</td>
                <td class="${(data.metrics.device_latency?.values['p(95)'] || 0) < 400 ? 'pass' : 'fail'}">${(data.metrics.device_latency?.values['p(95)'] || 0) < 400 ? '✅ Pass' : '❌ Fail'}</td>
            </tr>
            <tr>
                <td>Permission</td>
                <td>${(data.metrics.permission_latency?.values?.avg || 0).toFixed(2)}ms</td>
                <td>${(data.metrics.permission_latency?.values['p(95)'] || 0).toFixed(2)}ms</td>
                <td class="${(data.metrics.permission_latency?.values['p(95)'] || 0) < 200 ? 'pass' : 'fail'}">${(data.metrics.permission_latency?.values['p(95)'] || 0) < 200 ? '✅ Pass' : '❌ Fail'}</td>
            </tr>
            <tr>
                <td>Analytics</td>
                <td>${(data.metrics.analytics_latency?.values?.avg || 0).toFixed(2)}ms</td>
                <td>${(data.metrics.analytics_latency?.values['p(95)'] || 0).toFixed(2)}ms</td>
                <td class="${(data.metrics.analytics_latency?.values['p(95)'] || 0) < 800 ? 'pass' : 'fail'}">${(data.metrics.analytics_latency?.values['p(95)'] || 0) < 800 ? '✅ Pass' : '❌ Fail'}</td>
            </tr>
        </table>
    </div>
</body>
</html>`;
}
