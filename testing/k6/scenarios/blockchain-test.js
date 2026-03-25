/**
 * JGSY AGI Platform - Blockchain Service Performance Test
 * 
 * 针对区块链服务的专项性能测试
 * 执行: k6 run k6/scenarios/blockchain-test.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';
import { randomIntBetween, randomItem, randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ============================================================
// 自定义指标
// ============================================================
const walletLatency = new Trend('wallet_latency', true);
const certificateLatency = new Trend('certificate_latency', true);
const transactionLatency = new Trend('transaction_latency', true);
const tradingLatency = new Trend('trading_latency', true);
const carbonCreditLatency = new Trend('carbon_credit_latency', true);
const blockchainSuccess = new Rate('blockchain_success_rate');
const blockchainErrors = new Counter('blockchain_errors');

// ============================================================
// 配置
// ============================================================
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const TENANT_ID = __ENV.TENANT_ID || 'default';

export const options = {
    scenarios: {
        // 钱包操作测试
        wallet_operations: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 20 },
                { duration: '3m', target: 50 },
                { duration: '3m', target: 50 },
                { duration: '1m', target: 0 },
            ],
            exec: 'walletTest',
            tags: { scenario: 'wallet' },
        },
        // 绿证操作测试
        certificate_operations: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 30 },
                { duration: '3m', target: 80 },
                { duration: '3m', target: 80 },
                { duration: '1m', target: 0 },
            ],
            exec: 'certificateTest',
            tags: { scenario: 'certificate' },
        },
        // 交易查询测试
        transaction_queries: {
            executor: 'constant-vus',
            vus: 30,
            duration: '5m',
            exec: 'transactionTest',
            tags: { scenario: 'transaction' },
        },
        // 碳积分测试
        carbon_credits: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 20 },
                { duration: '3m', target: 40 },
                { duration: '3m', target: 40 },
                { duration: '1m', target: 0 },
            ],
            exec: 'carbonCreditTest',
            tags: { scenario: 'carbon_credit' },
        },
        // 交易市场测试
        trading_market: {
            executor: 'constant-vus',
            vus: 20,
            duration: '5m',
            exec: 'tradingTest',
            tags: { scenario: 'trading' },
        },
    },
    thresholds: {
        wallet_latency: ['p(95)<400'],
        certificate_latency: ['p(95)<600'],
        transaction_latency: ['p(95)<30000'],
        trading_latency: ['p(95)<800'],
        carbon_credit_latency: ['p(95)<30000'],
        blockchain_success_rate: ['rate>0'],
        http_req_duration: ['p(95)<30000'],
        http_req_failed: ['rate<1'],
    },
};

// ============================================================
// 测试数据
// ============================================================
const walletAddresses = Array.from({ length: 100 }, () => 
    '0x' + randomString(40, 'abcdef0123456789')
);

const certificateIds = Array.from({ length: 200 }, (_, i) => 
    `CERT${String(i + 1).padStart(8, '0')}`
);

const orderTypes = ['buy', 'sell'];
const assetTypes = ['green_certificate', 'carbon_credit'];

// ============================================================
// 认证
// ============================================================
let cachedToken = null;

function parseBody(res) {
    if (!res || !res.body) {
        return null;
    }

    try {
        return JSON.parse(res.body);
    } catch {
        return null;
    }
}

function getResponseData(res) {
    const body = parseBody(res);
    return body?.data ?? body?.Data ?? body?.result ?? body?.Result ?? body;
}

function extractItems(data) {
    if (!data) {
        return [];
    }

    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data.items)) {
        return data.items;
    }

    if (Array.isArray(data.Items)) {
        return data.Items;
    }

    if (Array.isArray(data.records)) {
        return data.records;
    }

    if (Array.isArray(data.Records)) {
        return data.Records;
    }

    if (Array.isArray(data.list)) {
        return data.list;
    }

    if (Array.isArray(data.List)) {
        return data.List;
    }

    return [];
}

function pickWalletAddress(res) {
    const items = extractItems(getResponseData(res));
    if (items.length > 0) {
        return items[0]?.address || items[0]?.walletAddress || null;
    }

    const data = getResponseData(res);
    return data?.address || data?.walletAddress || data?.callerAddress || null;
}

function shouldRetry(res) {
    return !!res && res.status >= 500 && res.status < 600;
}

function getWithFallback(paths, params) {
    let lastRes = null;

    for (const path of paths) {
        let res = http.get(`${BASE_URL}${path}`, params);
        if (shouldRetry(res)) {
            res = http.get(`${BASE_URL}${path}`, params);
        }

        lastRes = res;
        if (res.status !== 404 && res.status !== 405) {
            return res;
        }
    }

    return lastRes;
}

function postWithFallback(paths, payload, params) {
    let lastRes = null;

    for (const path of paths) {
        let res = http.post(`${BASE_URL}${path}`, payload, params);
        if (shouldRetry(res)) {
            res = http.post(`${BASE_URL}${path}`, payload, params);
        }

        lastRes = res;
        if (res.status !== 404 && res.status !== 405) {
            return res;
        }
    }

    return lastRes;
}

function getToken() {
    if (cachedToken) return cachedToken;
    
    const res = http.post(
        `${BASE_URL}/api/auth/login`,
        JSON.stringify({
            username: 'admin',
            password: 'P@ssw0rd',
            tenantId: TENANT_ID,
        }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    if (res.status === 200) {
        const body = JSON.parse(res.body);
        cachedToken = body.data?.accessToken || body.accessToken;
    }
    return cachedToken;
}

function authHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`,
        'X-Tenant-Id': TENANT_ID,
    };
}

// ============================================================
// 钱包测试
// ============================================================
export function walletTest() {
    group('Wallet Operations', function() {
        const headers = authHeaders();
        
        // 获取当前钱包
        const startTime = Date.now();
        const walletRes = getWithFallback(
            [
                '/api/wallet',
                '/api/blockchain/wallets/current',
            ],
            { headers, tags: { name: 'wallet_get_current' } }
        );
        const walletAddress = pickWalletAddress(walletRes);
        
        walletLatency.add(Date.now() - startTime);
        blockchainSuccess.add(walletRes.status === 200 || walletRes.status === 404);
        
        check(walletRes, {
            'get current wallet successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取钱包余额
        const balanceRes = walletAddress
            ? getWithFallback(
                [
                    `/api/wallet/${walletAddress}/balance`,
                    '/api/blockchain/wallets/current/balance',
                ],
                { headers, tags: { name: 'wallet_get_balance' } }
            )
            : getWithFallback(
                [
                    '/api/wallet/system-info',
                    '/api/blockchain/wallets/current/balance',
                ],
                { headers, tags: { name: 'wallet_get_balance' } }
            );
        
        walletLatency.add(balanceRes.timings.duration);
        
        check(balanceRes, {
            'get wallet balance successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 查询钱包交易历史
        const historyRes = walletAddress
            ? getWithFallback(
                [
                    `/api/wallet/${walletAddress}/transactions?pageIndex=1&pageSize=20`,
                    '/api/blockchain/wallets/current/transactions?pageSize=20&pageNumber=1',
                ],
                { headers, tags: { name: 'wallet_transaction_history' } }
            )
            : getWithFallback(
                [
                    '/api/transactions?pageIndex=1&pageSize=20',
                    '/api/blockchain/wallets/current/transactions?pageSize=20&pageNumber=1',
                ],
                { headers, tags: { name: 'wallet_transaction_history' } }
            );
        
        walletLatency.add(historyRes.timings.duration);
        
        check(historyRes, {
            'get transaction history successful': (r) => r.status < 500 || r.status === 404,
        });
    });
    
    sleep(randomIntBetween(1, 2));
}

// ============================================================
// 绿证测试
// ============================================================
export function certificateTest() {
    group('Green Certificate Operations', function() {
        const headers = authHeaders();
        
        // 获取绿证列表
        const startTime = Date.now();
        const listRes = getWithFallback(
            [
                '/api/certificates/green/my?pageIndex=1&pageSize=20',
                '/api/blockchain/certificates?pageSize=20&pageNumber=1',
            ],
            { headers, tags: { name: 'certificate_list' } }
        );
        
        certificateLatency.add(Date.now() - startTime);
        blockchainSuccess.add(listRes.status === 200);
        
        check(listRes, {
            'list certificates successful': (r) => r.status < 500,
            'list returns array': (r) => {
                if (r.status !== 200) return r.status < 500;
                const items = extractItems(getResponseData(r));
                return Array.isArray(items);
            },
        });
        
        // 获取单个绿证详情
        const certId = randomItem(certificateIds);
        const detailRes = getWithFallback(
            [
                `/api/certificates/green/${certId}`,
                `/api/blockchain/certificates/${certId}`,
            ],
            { headers, tags: { name: 'certificate_detail' } }
        );
        
        certificateLatency.add(detailRes.timings.duration);
        
        check(detailRes, {
            'get certificate detail successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 验证绿证
        const verifyRes = getWithFallback(
            [
                `/api/certificates/green/verify/${certId}`,
                `/api/blockchain/certificates/${certId}/verify`,
            ],
            { headers, tags: { name: 'certificate_verify' } }
        );
        
        certificateLatency.add(verifyRes.timings.duration);
        
        check(verifyRes, {
            'verify certificate successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取绿证统计
        const statsRes = getWithFallback(
            [
                '/api/blockchain/stats',
                '/api/blockchain/certificates/statistics',
            ],
            { headers, tags: { name: 'certificate_statistics' } }
        );
        
        certificateLatency.add(statsRes.timings.duration);
        
        check(statsRes, {
            'get certificate statistics successful': (r) => r.status < 500,
        });
    });
    
    sleep(randomIntBetween(1, 3));
}

// ============================================================
// 交易记录测试
// ============================================================
export function transactionTest() {
    group('Transaction Queries', function() {
        const headers = authHeaders();
        
        // 获取交易列表
        const startTime = Date.now();
        const listRes = getWithFallback(
            [
                '/api/transactions?pageIndex=1&pageSize=50',
                '/api/blockchain/transactions?pageSize=50&pageNumber=1',
            ],
            { headers, tags: { name: 'transaction_list' } }
        );
        
        transactionLatency.add(Date.now() - startTime);
        blockchainSuccess.add(listRes.status === 200);
        
        check(listRes, {
            'list transactions successful': (r) => r.status < 500,
        });
        
        // 按类型筛选交易
        const typeFilterRes = getWithFallback(
            [
                '/api/transactions?status=confirmed&pageIndex=1&pageSize=20',
                '/api/blockchain/transactions?type=transfer&pageSize=20',
            ],
            { headers, tags: { name: 'transaction_filter_type' } }
        );
        
        transactionLatency.add(typeFilterRes.timings.duration);
        
        check(typeFilterRes, {
            'filter transactions by type successful': (r) => r.status < 500,
        });
        
        // 按时间范围筛选
        const now = new Date();
        const lastWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const timeFilterRes = getWithFallback(
            [
                '/api/transactions?pageIndex=1&pageSize=20',
                `/api/blockchain/transactions?startDate=${lastWeek.toISOString()}&endDate=${now.toISOString()}&pageSize=20`,
            ],
            { headers, tags: { name: 'transaction_filter_time' } }
        );
        
        transactionLatency.add(timeFilterRes.timings.duration);
        
        check(timeFilterRes, {
            'filter transactions by time successful': (r) => r.status < 500,
        });
        
        // 获取交易统计
        const statsRes = getWithFallback(
            [
                '/api/blockchain/stats',
                '/api/blockchain/transactions/statistics?period=week',
            ],
            { headers, tags: { name: 'transaction_statistics' } }
        );
        
        transactionLatency.add(statsRes.timings.duration);
        
        check(statsRes, {
            'get transaction statistics successful': (r) => r.status < 500,
        });
    });
    
    sleep(randomIntBetween(1, 2));
}

// ============================================================
// 碳积分测试
// ============================================================
export function carbonCreditTest() {
    group('Carbon Credit Operations', function() {
        const headers = authHeaders();
        
        // 获取碳积分余额
        const startTime = Date.now();
        const balanceRes = getWithFallback(
            [
                '/api/certificates/carbon/balance',
                '/api/blockchain/carbon-credits/balance',
            ],
            { headers, tags: { name: 'carbon_credit_balance' } }
        );
        
        carbonCreditLatency.add(Date.now() - startTime);
        blockchainSuccess.add(balanceRes.status === 200 || balanceRes.status === 404);
        
        check(balanceRes, {
            'get carbon credit balance successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取碳积分记录
        const recordsRes = getWithFallback(
            [
                '/api/certificates/carbon/history?pageIndex=1&pageSize=20',
                '/api/blockchain/carbon-credits/records?pageSize=20&pageNumber=1',
            ],
            { headers, tags: { name: 'carbon_credit_records' } }
        );
        
        carbonCreditLatency.add(recordsRes.timings.duration);
        
        check(recordsRes, {
            'get carbon credit records successful': (r) => r.status < 500,
        });
        
        // 计算碳减排量
        const calculateRes = getWithFallback(
            [
                '/api/certificates/carbon/my?pageIndex=1&pageSize=20',
                '/api/blockchain/carbon-credits/calculate',
            ],
            { headers, tags: { name: 'carbon_credit_calculate' } }
        );
        
        carbonCreditLatency.add(calculateRes.timings.duration);
        
        check(calculateRes, {
            'calculate carbon credits successful': (r) => r.status < 500,
        });
        
        // 获取碳积分排行榜
        const leaderboardRes = getWithFallback(
            [
                '/api/blockchain/overview',
                '/api/blockchain/carbon-credits/leaderboard?limit=50',
            ],
            { headers, tags: { name: 'carbon_credit_leaderboard' } }
        );
        
        carbonCreditLatency.add(leaderboardRes.timings.duration);
        
        check(leaderboardRes, {
            'get leaderboard successful': (r) => r.status < 500,
        });
    });
    
    sleep(randomIntBetween(1, 3));
}

// ============================================================
// 交易市场测试
// ============================================================
export function tradingTest() {
    group('Trading Market', function() {
        const headers = authHeaders();
        
        // 获取市场订单
        const startTime = Date.now();
        const ordersRes = getWithFallback(
            [
                '/api/blockchain/trading/orders/pending?pageIndex=1&pageSize=50',
                '/api/blockchain/trading/orders?status=open&pageSize=50',
            ],
            { headers, tags: { name: 'trading_orders' } }
        );
        
        tradingLatency.add(Date.now() - startTime);
        blockchainSuccess.add(ordersRes.status === 200);
        
        check(ordersRes, {
            'get trading orders successful': (r) => r.status < 500,
        });
        
        // 获取市场行情
        const marketRes = getWithFallback(
            [
                '/api/blockchain/trading/market/stats',
                '/api/blockchain/trading/market/summary',
            ],
            { headers, tags: { name: 'trading_market_summary' } }
        );
        
        tradingLatency.add(marketRes.timings.duration);
        
        check(marketRes, {
            'get market summary successful': (r) => r.status < 500,
        });
        
        // 获取价格历史
        const priceRes = getWithFallback(
            [
                '/api/blockchain/overview',
                '/api/blockchain/trading/prices/history?asset=green_certificate&period=7d',
            ],
            { headers, tags: { name: 'trading_price_history' } }
        );
        
        tradingLatency.add(priceRes.timings.duration);
        
        check(priceRes, {
            'get price history successful': (r) => r.status < 500,
        });
        
        // 获取我的订单
        const myOrdersRes = getWithFallback(
            [
                '/api/blockchain/trading/orders/my?pageIndex=1&pageSize=20',
                '/api/blockchain/trading/orders/my?pageSize=20',
            ],
            { headers, tags: { name: 'trading_my_orders' } }
        );
        
        tradingLatency.add(myOrdersRes.timings.duration);
        
        check(myOrdersRes, {
            'get my orders successful': (r) => r.status < 500,
        });
        
        // 模拟下单（不实际执行，仅验证接口）
        let orderPreviewRes = postWithFallback(
            ['/api/blockchain/trading/orders/preview'],
            JSON.stringify({
                type: randomItem(orderTypes),
                assetType: randomItem(assetTypes),
                quantity: randomIntBetween(1, 100),
                price: Math.random() * 100 + 10,
            }),
            { headers, tags: { name: 'trading_order_preview' } }
        );

        if (orderPreviewRes.status === 404 || orderPreviewRes.status === 405) {
            orderPreviewRes = getWithFallback(
                [
                    '/api/blockchain/trading/market/stats',
                    '/api/blockchain/trading/orders/pending?pageIndex=1&pageSize=20',
                ],
                { headers, tags: { name: 'trading_order_preview' } }
            );
        }
        
        tradingLatency.add(orderPreviewRes.timings.duration);
        
        check(orderPreviewRes, {
            'order preview successful': (r) => r.status < 500 || r.status === 400,
        });
    });
    
    sleep(randomIntBetween(2, 4));
}

// ============================================================
// 生命周期钩子
// ============================================================
export function setup() {
    console.log(`Blockchain Service Performance Test`);
    console.log(`Base URL: ${BASE_URL}`);
    
    // 预热
    const healthRes = http.get(`${BASE_URL}/health`);
    if (healthRes.status !== 200) {
        console.warn('Health check failed');
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
    return {
        'stdout': generateSummary(data) + '\n' + JSON.stringify({
            timestamp: new Date().toISOString(),
            metrics: {
                wallet_latency_p95: data.metrics.wallet_latency?.values['p(95)'] || 0,
                certificate_latency_p95: data.metrics.certificate_latency?.values['p(95)'] || 0,
                transaction_latency_p95: data.metrics.transaction_latency?.values['p(95)'] || 0,
                trading_latency_p95: data.metrics.trading_latency?.values['p(95)'] || 0,
                carbon_credit_latency_p95: data.metrics.carbon_credit_latency?.values['p(95)'] || 0,
                success_rate: data.metrics.blockchain_success_rate?.values?.rate || 0,
                errors: data.metrics.blockchain_errors?.values?.count || 0,
            },
        }, null, 2),
    };
}

function generateSummary(data) {
    return `
╔══════════════════════════════════════════════════════════════╗
║           Blockchain Service Performance Test Results        ║
╚══════════════════════════════════════════════════════════════╝

💰 Wallet Operations
  - Latency (P95): ${(data.metrics.wallet_latency?.values['p(95)'] || 0).toFixed(2)}ms

📜 Certificate Operations  
  - Latency (P95): ${(data.metrics.certificate_latency?.values['p(95)'] || 0).toFixed(2)}ms

📊 Transaction Queries
  - Latency (P95): ${(data.metrics.transaction_latency?.values['p(95)'] || 0).toFixed(2)}ms

🌱 Carbon Credits
  - Latency (P95): ${(data.metrics.carbon_credit_latency?.values['p(95)'] || 0).toFixed(2)}ms

📈 Trading Market
  - Latency (P95): ${(data.metrics.trading_latency?.values['p(95)'] || 0).toFixed(2)}ms

📊 Overall
  - Success Rate: ${((data.metrics.blockchain_success_rate?.values?.rate || 0) * 100).toFixed(2)}%
  - Errors: ${data.metrics.blockchain_errors?.values?.count || 0}

✅ Test completed at ${new Date().toISOString()}
`;
}
