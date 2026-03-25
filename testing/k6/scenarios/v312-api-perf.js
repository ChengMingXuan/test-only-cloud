/**
 * V3.1.2 新增/变更 API 性能测试
 * ============================================
 * 覆盖范围：
 * - 证书轮转 API (CertificateRotationController)
 * - WAL 缓冲存储 (WalBufferedStorageStrategy)
 * - 批量数据写入 (BatchIngestionWriter)
 * - OCPP 2.0 消息处理 (Ocpp20MessageHandler)
 * - 区块链多链容灾 (ChainFailoverManager)
 * - 碳交易 API (CarbonTradingController)
 * - 需求响应 API (DemandResponseController)
 * - VPP 调度 API (VppDispatchService)
 * - 钱包服务 (WalletService)
 * - 规则引擎执行 (RuleExecutionEngine)
 * 
 * 场景数：40
 * 运行: k6 run testing/k6/scenarios/v312-api-perf.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 测试环境配置 - 禁止连接生产环境
const BASE_URL = __ENV.TEST_BASE_URL || 'http://localhost:8000';
const MOCK_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test';

// 自定义指标
const errorRate = new Rate('errors');
const certRotationLatency = new Trend('cert_rotation_latency');
const walWriteLatency = new Trend('wal_write_latency');
const batchIngestLatency = new Trend('batch_ingest_latency');
const blockchainLatency = new Trend('blockchain_latency');
const carbonTradeLatency = new Trend('carbon_trade_latency');
const demandRespLatency = new Trend('demand_resp_latency');
const vppDispatchLatency = new Trend('vpp_dispatch_latency');
const walletLatency = new Trend('wallet_latency');
const ruleEngineLatency = new Trend('rule_engine_latency');
const ocppLatency = new Trend('ocpp_latency');
const totalRequests = new Counter('total_v312_requests');

// 公共请求头
const headers = {
    'Content-Type': 'application/json',
    'Authorization': MOCK_TOKEN,
    'X-Tenant-Code': 'TEST_TENANT'
};

// ── 测试选项
export const options = {
    stages: [
        { duration: '30s', target: 10 },   // 热身
        { duration: '2m', target: 30 },    // 正常负载
        { duration: '2m', target: 50 },    // 提升
        { duration: '1m', target: 30 },    // 降压
        { duration: '30s', target: 0 },    // 冷却
    ],
    thresholds: {
        http_req_failed: ['rate<1'],
        http_req_duration: ['p(95)<30000'],
        errors: ['rate<0.2'],
        cert_rotation_latency: ['p(95)<5000'],
        wal_write_latency: ['p(95)<3000'],
        batch_ingest_latency: ['p(95)<3000'],
        blockchain_latency: ['p(95)<5000'],
        carbon_trade_latency: ['p(95)<5000'],
        demand_resp_latency: ['p(95)<5000'],
        vpp_dispatch_latency: ['p(95)<5000'],
        wallet_latency: ['p(95)<3000'],
        rule_engine_latency: ['p(95)<3000'],
        ocpp_latency: ['p(95)<3000'],
    },
};

// ── 主测试函数
export default function () {
    const scenario = __ITER % 10;

    switch (scenario) {
        case 0: testCertRotation(); break;
        case 1: testWalStorage(); break;
        case 2: testBatchIngestion(); break;
        case 3: testOcppMessages(); break;
        case 4: testBlockchainFailover(); break;
        case 5: testCarbonTrading(); break;
        case 6: testDemandResponse(); break;
        case 7: testVppDispatch(); break;
        case 8: testWallet(); break;
        case 9: testRuleEngine(); break;
    }

    sleep(0.5);
}

// ═══════════════════════════════════════════════════
// 1. 证书轮转 API 性能
// ═══════════════════════════════════════════════════

function testCertRotation() {
    group('CertRotation', () => {
        // [S01] 获取证书状态
        const r1 = http.get(`${BASE_URL}/api/monitor/service-mesh/certificate-rotation/status`, { headers });
        check(r1, { '[S01] 证书状态 <500': r => r.status < 500 });
        certRotationLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S02] 查询轮转记录
        const r2 = http.get(`${BASE_URL}/api/monitor/service-mesh/certificate-rotation/records?page=1&pageSize=10`, { headers });
        check(r2, { '[S02] 轮转记录 <500': r => r.status < 500 });
        certRotationLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S03] 触发轮转
        const r3 = http.post(`${BASE_URL}/api/monitor/service-mesh/certificate-rotation/rotate`,
            JSON.stringify({ serviceName: 'gateway', reason: 'k6-test' }), { headers });
        check(r3, { '[S03] 触发轮转 <500': r => r.status < 500 || r.status === 401 });
        certRotationLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S04] 并发状态查询
        const r4 = http.get(`${BASE_URL}/api/monitor/service-mesh/certificate-rotation/status`, { headers });
        check(r4, { '[S04] 并发状态 <500': r => r.status < 500 });
        certRotationLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 2. WAL 缓冲存储性能
// ═══════════════════════════════════════════════════

function testWalStorage() {
    group('WAL Storage', () => {
        // [S05] WAL 状态查询
        const r1 = http.get(`${BASE_URL}/api/ingestion/wal/status`, { headers });
        check(r1, { '[S05] WAL状态 <500': r => r.status < 500 });
        walWriteLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S06] WAL 写入性能
        const payload = JSON.stringify({
            deviceId: 'device-k6-001',
            timestamp: new Date().toISOString(),
            metrics: { temperature: 35.5, voltage: 220.0, current: 15.0, power: 3300.0 }
        });
        const r2 = http.post(`${BASE_URL}/api/ingestion/wal/write`, payload, { headers });
        check(r2, { '[S06] WAL写入 <500': r => r.status < 500 || r.status === 401 });
        walWriteLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S07] 批量写入
        const batchPayload = JSON.stringify({
            items: Array.from({ length: 10 }, (_, i) => ({
                deviceId: `device-k6-${String(i).padStart(3, '0')}`,
                timestamp: new Date().toISOString(),
                metrics: { temperature: 30 + Math.random() * 10 }
            }))
        });
        const r3 = http.post(`${BASE_URL}/api/ingestion/wal/batch-write`, batchPayload, { headers });
        check(r3, { '[S07] 批量写入 <500': r => r.status < 500 || r.status === 401 });
        walWriteLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S08] Checkpoint 查询
        const r4 = http.get(`${BASE_URL}/api/ingestion/wal/checkpoint`, { headers });
        check(r4, { '[S08] Checkpoint <500': r => r.status < 500 });
        walWriteLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 3. 批量数据采集性能
// ═══════════════════════════════════════════════════

function testBatchIngestion() {
    group('Batch Ingestion', () => {
        // [S09] 入队写入
        const r1 = http.post(`${BASE_URL}/api/ingestion/batch/enqueue`,
            JSON.stringify({ deviceId: 'dev-k6', data: { temp: 35 } }), { headers });
        check(r1, { '[S09] 入队 <500': r => r.status < 500 || r.status === 401 });
        batchIngestLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S10] 队列深度
        const r2 = http.get(`${BASE_URL}/api/ingestion/batch/depth`, { headers });
        check(r2, { '[S10] 队列深度 <500': r => r.status < 500 });
        batchIngestLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S11] 写入统计
        const r3 = http.get(`${BASE_URL}/api/ingestion/batch/stats`, { headers });
        check(r3, { '[S11] 写入统计 <500': r => r.status < 500 });
        batchIngestLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S12] 强制刷新
        const r4 = http.post(`${BASE_URL}/api/ingestion/batch/flush`, '{}', { headers });
        check(r4, { '[S12] 刷新 <500': r => r.status < 500 || r.status === 401 });
        batchIngestLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 4. OCPP 2.0 消息处理性能
// ═══════════════════════════════════════════════════

function testOcppMessages() {
    group('OCPP 2.0', () => {
        // [S13] TransactionEvent Started
        const r1 = http.post(`${BASE_URL}/api/ingestion/ocpp20/transaction-event`,
            JSON.stringify({
                eventType: 'Started', transactionId: `tx-k6-${Date.now()}`,
                chargingStationId: 'cs-001', connectorId: 1,
                meterValue: [{ sampledValue: [{ value: '0', measurand: 'Energy.Active.Import.Register' }] }]
            }), { headers });
        check(r1, { '[S13] OCPP Started <500': r => r.status < 500 || r.status === 401 });
        ocppLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S14] TransactionEvent Updated
        const r2 = http.post(`${BASE_URL}/api/ingestion/ocpp20/transaction-event`,
            JSON.stringify({
                eventType: 'Updated', transactionId: `tx-k6-${Date.now()}`,
                chargingStationId: 'cs-001', connectorId: 1,
                meterValue: [{ sampledValue: [{ value: '15.5', measurand: 'Energy.Active.Import.Register' }] }]
            }), { headers });
        check(r2, { '[S14] OCPP Updated <500': r => r.status < 500 || r.status === 401 });
        ocppLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S15] StatusNotification
        const r3 = http.post(`${BASE_URL}/api/ingestion/ocpp20/status-notification`,
            JSON.stringify({
                chargingStationId: 'cs-001', connectorId: 1,
                connectorStatus: 'Available', timestamp: new Date().toISOString()
            }), { headers });
        check(r3, { '[S15] OCPP Status <500': r => r.status < 500 || r.status === 401 });
        ocppLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S16] 故障状态
        const r4 = http.post(`${BASE_URL}/api/ingestion/ocpp20/status-notification`,
            JSON.stringify({
                chargingStationId: 'cs-001', connectorId: 2,
                connectorStatus: 'Faulted', timestamp: new Date().toISOString()
            }), { headers });
        check(r4, { '[S16] OCPP Fault <500': r => r.status < 500 || r.status === 401 });
        ocppLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 5. 区块链多链容灾性能
// ═══════════════════════════════════════════════════

function testBlockchainFailover() {
    group('Blockchain Failover', () => {
        // [S17] 容灾状态
        const r1 = http.get(`${BASE_URL}/api/blockchain/chain/failover/status`, { headers });
        check(r1, { '[S17] 容灾状态 <500': r => r.status < 500 });
        blockchainLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S18] 节点列表
        const r2 = http.get(`${BASE_URL}/api/blockchain/chain/failover/nodes`, { headers });
        check(r2, { '[S18] 节点列表 <500': r => r.status < 500 });
        blockchainLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S19] 链健康
        const r3 = http.get(`${BASE_URL}/api/blockchain/chain/health`, { headers });
        check(r3, { '[S19] 链健康 <500': r => r.status < 500 });
        blockchainLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S20] 幂等性检查
        const r4 = http.get(`${BASE_URL}/api/blockchain/chain/idempotency/stats`, { headers });
        check(r4, { '[S20] 幂等统计 <500': r => r.status < 500 });
        blockchainLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 6. 碳交易 API 性能
// ═══════════════════════════════════════════════════

function testCarbonTrading() {
    group('Carbon Trading', () => {
        // [S21] 排放计算
        const r1 = http.post(`${BASE_URL}/api/iotcloudai/carbon/emission`,
            JSON.stringify({ stationId: 'station-001', period: '2026-03' }), { headers });
        check(r1, { '[S21] 排放计算 <500': r => r.status < 500 || r.status === 401 });
        carbonTradeLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S22] 碳资产查询
        const r2 = http.get(`${BASE_URL}/api/iotcloudai/carbon/asset?stationId=station-001`, { headers });
        check(r2, { '[S22] 碳资产 <500': r => r.status < 500 });
        carbonTradeLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S23] 碳价预测
        const r3 = http.get(`${BASE_URL}/api/iotcloudai/carbon/forecast?days=30`, { headers });
        check(r3, { '[S23] 碳价预测 <500': r => r.status < 500 });
        carbonTradeLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S24] 交易策略
        const r4 = http.get(`${BASE_URL}/api/iotcloudai/carbon/strategy`, { headers });
        check(r4, { '[S24] 交易策略 <500': r => r.status < 500 });
        carbonTradeLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 7. 需求响应 API 性能
// ═══════════════════════════════════════════════════

function testDemandResponse() {
    group('Demand Response', () => {
        // [S25] 事件列表
        const r1 = http.get(`${BASE_URL}/api/iotcloudai/demand-response/events`, { headers });
        check(r1, { '[S25] DR事件列表 <500': r => r.status < 500 });
        demandRespLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S26] 能力评估
        const r2 = http.get(`${BASE_URL}/api/iotcloudai/demand-response/capability`, { headers });
        check(r2, { '[S26] DR能力评估 <500': r => r.status < 500 });
        demandRespLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S27] 参与计划
        const r3 = http.post(`${BASE_URL}/api/iotcloudai/demand-response/participate`,
            JSON.stringify({ eventId: 'event-001', capacity: 100 }), { headers });
        check(r3, { '[S27] DR参与 <500': r => r.status < 500 || r.status === 401 });
        demandRespLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S28] 结算查询
        const r4 = http.get(`${BASE_URL}/api/iotcloudai/demand-response/settle?eventId=event-001`, { headers });
        check(r4, { '[S28] DR结算 <500': r => r.status < 500 });
        demandRespLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 8. VPP 调度性能
// ═══════════════════════════════════════════════════

function testVppDispatch() {
    group('VPP Dispatch', () => {
        // [S29] 调度列表
        const r1 = http.get(`${BASE_URL}/api/vpp/dispatch?page=1&pageSize=10`, { headers });
        check(r1, { '[S29] 调度列表 <500': r => r.status < 500 });
        vppDispatchLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S30] 执行调度
        const r2 = http.post(`${BASE_URL}/api/vpp/dispatch/execute`,
            JSON.stringify({ vppId: 'vpp-001', targetPower: 500 }), { headers });
        check(r2, { '[S30] 执行调度 <500': r => r.status < 500 || r.status === 401 });
        vppDispatchLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S31] 调度分解
        const r3 = http.get(`${BASE_URL}/api/vpp/dispatch/dispatch-001/decompose`, { headers });
        check(r3, { '[S31] 分解结果 <500': r => r.status < 500 });
        vppDispatchLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S32] 取消调度
        const r4 = http.post(`${BASE_URL}/api/vpp/dispatch/dispatch-002/cancel`,
            JSON.stringify({ reason: 'k6-test' }), { headers });
        check(r4, { '[S32] 取消调度 <500': r => r.status < 500 || r.status === 401 });
        vppDispatchLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 9. 钱包服务性能
// ═══════════════════════════════════════════════════

function testWallet() {
    group('Wallet', () => {
        // [S33] 余额查询
        const r1 = http.get(`${BASE_URL}/api/account/wallet/balance`, { headers });
        check(r1, { '[S33] 余额查询 <500': r => r.status < 500 });
        walletLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S34] 充值
        const r2 = http.post(`${BASE_URL}/api/account/wallet/recharge`,
            JSON.stringify({ amount: 100.00, paymentMethod: 'alipay' }), { headers });
        check(r2, { '[S34] 充值 <500': r => r.status < 500 || r.status === 401 });
        walletLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S35] 交易记录
        const r3 = http.get(`${BASE_URL}/api/account/wallet/transactions?page=1&pageSize=10`, { headers });
        check(r3, { '[S35] 交易记录 <500': r => r.status < 500 });
        walletLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S36] 消费记录
        const r4 = http.get(`${BASE_URL}/api/account/wallet/consume-history`, { headers });
        check(r4, { '[S36] 消费记录 <500': r => r.status < 500 });
        walletLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}

// ═══════════════════════════════════════════════════
// 10. 规则引擎执行性能
// ═══════════════════════════════════════════════════

function testRuleEngine() {
    group('Rule Engine', () => {
        // [S37] 规则链列表
        const r1 = http.get(`${BASE_URL}/api/ruleengine/chains?page=1&pageSize=10`, { headers });
        check(r1, { '[S37] 规则链列表 <500': r => r.status < 500 });
        ruleEngineLatency.add(r1.timings.duration);
        totalRequests.add(1);

        // [S38] 规则执行
        const r2 = http.post(`${BASE_URL}/api/ruleengine/execute`,
            JSON.stringify({
                deviceId: 'dev-001', msgType: 'telemetry',
                payload: { temperature: 85.5, voltage: 220 }
            }), { headers });
        check(r2, { '[S38] 规则执行 <500': r => r.status < 500 || r.status === 401 });
        ruleEngineLatency.add(r2.timings.duration);
        totalRequests.add(1);

        // [S39] 执行统计
        const r3 = http.get(`${BASE_URL}/api/ruleengine/execution/stats`, { headers });
        check(r3, { '[S39] 执行统计 <500': r => r.status < 500 });
        ruleEngineLatency.add(r3.timings.duration);
        totalRequests.add(1);

        // [S40] 匹配引擎调用
        const r4 = http.post(`${BASE_URL}/api/ruleengine/match`,
            JSON.stringify({ deviceId: 'dev-001', deviceType: 'charging_pile', msgType: 'alarm' }), { headers });
        check(r4, { '[S40] 规则匹配 <500': r => r.status < 500 || r.status === 401 });
        ruleEngineLatency.add(r4.timings.duration);
        totalRequests.add(1);
    });
}
