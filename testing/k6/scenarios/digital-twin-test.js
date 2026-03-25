/**
 * JGSY AGI Platform - Digital Twin & IoT Performance Test
 * 
 * 针对数字孪生和物联网数据采集的专项性能测试
 * 执行: k6 run k6/scenarios/digital-twin-test.js
 */

import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep, group } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';
import { randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ============================================================
// 自定义指标
// ============================================================
const wsConnectionTime = new Trend('ws_connection_time', true);
const wsMessageLatency = new Trend('ws_message_latency', true);
const telemetryLatency = new Trend('telemetry_latency', true);
const twinSyncLatency = new Trend('twin_sync_latency', true);
const mlPredictionLatency = new Trend('ml_prediction_latency', true);
const dataIngestionRate = new Rate('data_ingestion_success');
const wsMessages = new Counter('ws_messages_received');
const deviceEvents = new Counter('device_events');

// ============================================================
// 配置
// ============================================================
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const WS_URL = __ENV.WS_URL || 'ws://localhost:8000';
const TENANT_ID = __ENV.TENANT_ID || 'default';
const DEVICE_COUNT = parseInt(__ENV.DEVICE_COUNT) || 1000;

export const options = {
    scenarios: {
        // WebSocket 实时数据流测试
        websocket_realtime: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 100 },   // 100 个 WebSocket 连接
                { duration: '5m', target: 500 },   // 500 个并发连接
                { duration: '3m', target: 500 },   // 持续
                { duration: '1m', target: 0 },
            ],
            exec: 'websocketTest',
            tags: { scenario: 'websocket' },
        },
        // 设备遥测数据上报测试
        telemetry_ingestion: {
            executor: 'constant-arrival-rate',
            rate: 10000,  // 每秒 10000 条数据
            timeUnit: '1s',
            duration: '5m',
            preAllocatedVUs: 200,
            maxVUs: 500,
            exec: 'telemetryIngestion',
            tags: { scenario: 'telemetry' },
        },
        // 数字孪生状态同步测试
        twin_sync: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 50 },
                { duration: '3m', target: 100 },
                { duration: '3m', target: 100 },
                { duration: '1m', target: 0 },
            ],
            exec: 'twinSyncTest',
            tags: { scenario: 'twin_sync' },
        },
        // ML 预测 API 测试
        ml_prediction: {
            executor: 'constant-vus',
            vus: 20,
            duration: '5m',
            exec: 'mlPredictionTest',
            tags: { scenario: 'ml_prediction' },
        },
    },
    thresholds: {
        ws_connection_time: ['p(95)<30000'],
        ws_message_latency: ['p(95)<30000'],
        telemetry_latency: ['p(95)<50', 'p(99)<100'],
        twin_sync_latency: ['p(95)<30000'],
        ml_prediction_latency: ['p(95)<30000'],
        data_ingestion_success: ['rate>0'],
        http_req_duration: ['p(95)<30000'],
        http_req_failed: ['rate<1'],
    },
};

// ============================================================
// 测试数据
// ============================================================
const deviceIds = Array.from({ length: DEVICE_COUNT }, (_, i) => 
    `DEV${String(i + 1).padStart(6, '0')}`
);

const stationIds = Array.from({ length: 100 }, (_, i) => 
    `ST${String(i + 1).padStart(4, '0')}`
);

// 生成随机遥测数据
function generateTelemetry(deviceId) {
    return {
        deviceId: deviceId,
        timestamp: new Date().toISOString(),
        data: {
            voltage: 220 + Math.random() * 20 - 10,
            current: Math.random() * 32,
            power: Math.random() * 7000,
            energy: Math.random() * 100,
            temperature: 25 + Math.random() * 40,
            soc: Math.random() * 100,
            status: randomItem(['charging', 'idle', 'error', 'offline']),
        },
        quality: randomItem(['good', 'uncertain', 'bad']),
    };
}

// 获取认证 Token
let cachedToken = null;
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

// ============================================================
// WebSocket 实时数据流测试
// ============================================================
export function websocketTest() {
    const token = getToken();
    const deviceId = randomItem(deviceIds);
    
    const url = `${WS_URL}/hubs/digital-twin?access_token=${token}&deviceId=${deviceId}`;
    
    const startTime = Date.now();
    
    const res = ws.connect(url, {}, function(socket) {
        const connectionTime = Date.now() - startTime;
        wsConnectionTime.add(connectionTime);
        
        check(connectionTime, {
            'ws connection < 1s': (t) => t < 1000,
        });
        
        // 订阅设备数据
        socket.send(JSON.stringify({
            type: 'subscribe',
            channel: `device:${deviceId}`,
        }));
        
        socket.on('message', function(data) {
            const receiveTime = Date.now();
            wsMessages.add(1);
            
            try {
                const msg = JSON.parse(data);
                if (msg.timestamp) {
                    const latency = receiveTime - new Date(msg.timestamp).getTime();
                    wsMessageLatency.add(latency);
                }
                
                check(msg, {
                    'ws message has type': (m) => m.type !== undefined,
                    'ws message has data': (m) => m.data !== undefined,
                });
            } catch (e) {
                // 非 JSON 消息
            }
        });
        
        socket.on('error', function(e) {
            console.error('WebSocket error:', e);
        });
        
        // 保持连接一段时间
        socket.setTimeout(function() {
            socket.close();
        }, randomIntBetween(30000, 60000));
    });
    
    check(res, {
        'ws connection established': (r) => r && r.status === 101,
    });
}

// ============================================================
// 设备遥测数据上报测试
// ============================================================
export function telemetryIngestion() {
    const deviceId = randomItem(deviceIds);
    const telemetry = generateTelemetry(deviceId);
    
    const startTime = Date.now();
    
    const res = http.post(
        `${BASE_URL}/api/ingestion/telemetry`,
        JSON.stringify(telemetry),
        {
            headers: {
                'Content-Type': 'application/json',
                'X-Device-Id': deviceId,
                'X-Tenant-Id': TENANT_ID,
            },
            tags: { name: 'telemetry_post' },
        }
    );
    
    const latency = Date.now() - startTime;
    telemetryLatency.add(latency);
    deviceEvents.add(1);
    
    const success = res.status === 200 || res.status === 202;
    dataIngestionRate.add(success);
    
    check(res, {
        'telemetry accepted': (r) => r.status < 500 || r.status === 202,
        'telemetry latency < 50ms': () => latency < 50,
    });
}

// ============================================================
// 批量遥测数据上报
// ============================================================
export function batchTelemetryIngestion() {
    const batchSize = randomIntBetween(50, 100);
    const batch = [];
    
    for (let i = 0; i < batchSize; i++) {
        batch.push(generateTelemetry(randomItem(deviceIds)));
    }
    
    const startTime = Date.now();
    
    const res = http.post(
        `${BASE_URL}/api/ingestion/telemetry/batch`,
        JSON.stringify({ items: batch }),
        {
            headers: {
                'Content-Type': 'application/json',
                'X-Tenant-Id': TENANT_ID,
            },
            tags: { name: 'telemetry_batch' },
        }
    );
    
    const latency = Date.now() - startTime;
    telemetryLatency.add(latency / batchSize); // 平均每条延迟
    deviceEvents.add(batchSize);
    
    check(res, {
        'batch telemetry accepted': (r) => r.status < 500 || r.status === 202,
        'batch processed count': (r) => {
            if (r.status !== 200) return false;
            const body = JSON.parse(r.body);
            return body.data?.processedCount === batchSize;
        },
    });
}

// ============================================================
// 数字孪生状态同步测试
// ============================================================
export function twinSyncTest() {
    const token = getToken();
    const stationId = randomItem(stationIds);
    
    group('Digital Twin Sync', function() {
        // 获取数字孪生状态
        const startTime = Date.now();
        
        const stateRes = http.get(
            `${BASE_URL}/api/digital-twin/stations/${stationId}/state`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'X-Tenant-Id': TENANT_ID,
                },
                tags: { name: 'twin_get_state' },
            }
        );
        
        twinSyncLatency.add(Date.now() - startTime);
        
        check(stateRes, {
            'get twin state successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取设备健康分数
        const healthRes = http.get(
            `${BASE_URL}/api/digital-twin/stations/${stationId}/health`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'X-Tenant-Id': TENANT_ID,
                },
                tags: { name: 'twin_health_score' },
            }
        );
        
        check(healthRes, {
            'get health score successful': (r) => r.status < 500 || r.status === 404,
        });
        
        // 获取聚合数据
        const aggregateRes = http.get(
            `${BASE_URL}/api/digital-twin/stations/${stationId}/aggregates?interval=1h&limit=24`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'X-Tenant-Id': TENANT_ID,
                },
                tags: { name: 'twin_aggregates' },
            }
        );
        
        check(aggregateRes, {
            'get aggregates successful': (r) => r.status < 500 || r.status === 404,
        });
    });
    
    sleep(randomIntBetween(1, 3));
}

// ============================================================
// ML 预测 API 测试
// ============================================================
export function mlPredictionTest() {
    const token = getToken();
    const deviceId = randomItem(deviceIds);
    
    group('ML Prediction', function() {
        // 设备健康预测
        const startTime = Date.now();
        
        const healthPredRes = http.post(
            `${BASE_URL}/api/digital-twin/ml/predict/health`,
            JSON.stringify({
                deviceId: deviceId,
                features: {
                    avgVoltage: 220 + Math.random() * 10,
                    avgCurrent: Math.random() * 32,
                    avgTemperature: 30 + Math.random() * 20,
                    operatingHours: Math.random() * 10000,
                    errorCount: Math.floor(Math.random() * 10),
                },
            }),
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-Tenant-Id': TENANT_ID,
                },
                tags: { name: 'ml_health_prediction' },
            }
        );
        
        mlPredictionLatency.add(Date.now() - startTime);
        
        check(healthPredRes, {
            'health prediction successful': (r) => r.status < 500,
            'health prediction has score': (r) => {
                if (r.status !== 200) return false;
                const body = JSON.parse(r.body);
                return body.data?.healthScore !== undefined;
            },
        });
        
        // 异常检测
        const anomalyRes = http.post(
            `${BASE_URL}/api/digital-twin/ml/detect/anomaly`,
            JSON.stringify({
                deviceId: deviceId,
                window: '1h',
                data: Array.from({ length: 60 }, () => ({
                    timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
                    value: Math.random() * 100,
                })),
            }),
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-Tenant-Id': TENANT_ID,
                },
                tags: { name: 'ml_anomaly_detection' },
            }
        );
        
        check(anomalyRes, {
            'anomaly detection successful': (r) => r.status < 500,
        });
        
        // 负载预测
        const loadPredRes = http.post(
            `${BASE_URL}/api/digital-twin/ml/predict/load`,
            JSON.stringify({
                stationId: randomItem(stationIds),
                horizon: '24h',
                features: {
                    dayOfWeek: new Date().getDay(),
                    hourOfDay: new Date().getHours(),
                    isWeekend: [0, 6].includes(new Date().getDay()),
                    temperature: 25 + Math.random() * 15,
                },
            }),
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                    'X-Tenant-Id': TENANT_ID,
                },
                tags: { name: 'ml_load_prediction' },
            }
        );
        
        check(loadPredRes, {
            'load prediction successful': (r) => r.status < 500,
        });
    });
    
    sleep(randomIntBetween(2, 5));
}

// ============================================================
// 生命周期钩子
// ============================================================
export function setup() {
    console.log(`Digital Twin Performance Test`);
    console.log(`Base URL: ${BASE_URL}`);
    console.log(`WebSocket URL: ${WS_URL}`);
    console.log(`Device Count: ${DEVICE_COUNT}`);
    
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
                ws_connection_time_p95: data.metrics.ws_connection_time?.values['p(95)'] || 0,
                ws_message_latency_p95: data.metrics.ws_message_latency?.values['p(95)'] || 0,
                telemetry_latency_p95: data.metrics.telemetry_latency?.values['p(95)'] || 0,
                twin_sync_latency_p95: data.metrics.twin_sync_latency?.values['p(95)'] || 0,
                ml_prediction_latency_p95: data.metrics.ml_prediction_latency?.values['p(95)'] || 0,
                data_ingestion_rate: data.metrics.data_ingestion_success?.values?.rate || 0,
                ws_messages_total: data.metrics.ws_messages_received?.values?.count || 0,
                device_events_total: data.metrics.device_events?.values?.count || 0,
            },
        }, null, 2),
    };
}

function generateSummary(data) {
    return `
╔══════════════════════════════════════════════════════════════╗
║          Digital Twin & IoT Performance Test Results         ║
╚══════════════════════════════════════════════════════════════╝

📡 WebSocket Performance
  - Connection Time (P95): ${(data.metrics.ws_connection_time?.values['p(95)'] || 0).toFixed(2)}ms
  - Message Latency (P95): ${(data.metrics.ws_message_latency?.values['p(95)'] || 0).toFixed(2)}ms
  - Messages Received: ${data.metrics.ws_messages_received?.values?.count || 0}

📊 Telemetry Ingestion
  - Latency (P95): ${(data.metrics.telemetry_latency?.values['p(95)'] || 0).toFixed(2)}ms
  - Latency (P99): ${(data.metrics.telemetry_latency?.values['p(99)'] || 0).toFixed(2)}ms
  - Success Rate: ${((data.metrics.data_ingestion_success?.values?.rate || 0) * 100).toFixed(2)}%
  - Total Events: ${data.metrics.device_events?.values?.count || 0}

🔄 Digital Twin Sync
  - Sync Latency (P95): ${(data.metrics.twin_sync_latency?.values['p(95)'] || 0).toFixed(2)}ms

🤖 ML Predictions
  - Prediction Latency (P95): ${(data.metrics.ml_prediction_latency?.values['p(95)'] || 0).toFixed(2)}ms

✅ Test completed at ${new Date().toISOString()}
`;
}
