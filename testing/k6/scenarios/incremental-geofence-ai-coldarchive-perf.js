/**
 * 增量性能测试 — GeoFence + IotCloudAI AI新能力 + ColdArchive + 后台任务 + Gateway路由
 * ============================================================================
 * 覆盖本轮 Git 变更新增的全部 API 端点性能基准
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:18999';
const TOKEN = __ENV.AUTH_TOKEN || 'Bearer mock-token';
const headers = { 'Content-Type': 'application/json', Authorization: TOKEN };

export const options = {
  scenarios: {
    // 场景1: GeoFence CRUD 基准
    geofence_crud: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'geofenceCrud',
      tags: { group: 'station-geofence' },
    },
    // 场景2: IotCloudAI ImageSearch
    imagesearch: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
      exec: 'imageSearch',
      startTime: '10s',
      tags: { group: 'iotcloudai-imagesearch' },
    },
    // 场景3: IotCloudAI LLM
    llm_inference: {
      executor: 'constant-vus',
      vus: 2,
      duration: '30s',
      exec: 'llmInference',
      startTime: '20s',
      tags: { group: 'iotcloudai-llm' },
    },
    // 场景4: ModelRouting 路由
    model_routing: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'modelRouting',
      startTime: '30s',
      tags: { group: 'iotcloudai-modelrouting' },
    },
    // 场景5: SolarPrediction 光伏预测
    solar_prediction: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
      exec: 'solarPrediction',
      startTime: '40s',
      tags: { group: 'iotcloudai-solar' },
    },
    // 场景6: VisionInspection 视觉巡检
    vision_inspection: {
      executor: 'constant-vus',
      vus: 2,
      duration: '30s',
      exec: 'visionInspection',
      startTime: '50s',
      tags: { group: 'iotcloudai-vision' },
    },
    // 场景7: Storage Archive 冷归档
    storage_archive: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
      exec: 'storageArchive',
      startTime: '60s',
      tags: { group: 'storage-archive' },
    },
    // 场景8: Internal API 内部告警/工单
    internal_api: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      exec: 'internalApi',
      startTime: '70s',
      tags: { group: 'internal-api' },
    },
    // 场景9: Gateway 路由拆分验证
    gateway_routes: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      exec: 'gatewayRoutes',
      startTime: '80s',
      tags: { group: 'gateway-routes' },
    },
    // 场景10: Permission 三员分立权限查询
    permission_roles: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
      exec: 'permissionRoles',
      startTime: '90s',
      tags: { group: 'permission-roles' },
    },
    // 场景11: Trading 过期订单
    trading_expiration: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
      exec: 'tradingExpiration',
      startTime: '100s',
      tags: { group: 'trading-expiration' },
    },
    // 场景12: Ingestion 协议状态
    ingestion_sharding: {
      executor: 'constant-vus',
      vus: 3,
      duration: '30s',
      exec: 'ingestionSharding',
      startTime: '110s',
      tags: { group: 'ingestion-sharding' },
    },
    // ---- 峰值场景 ----
    // 场景13: GeoFence 坐标判断峰值
    geofence_check_peak: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 20 },
        { duration: '20s', target: 20 },
        { duration: '10s', target: 0 },
      ],
      exec: 'geofenceCheckPeak',
      startTime: '120s',
      tags: { group: 'station-geofence-peak' },
    },
    // 场景14: ModelRouting 路由峰值
    model_routing_peak: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 30 },
        { duration: '20s', target: 30 },
        { duration: '10s', target: 0 },
      ],
      exec: 'modelRoutingPeak',
      startTime: '160s',
      tags: { group: 'iotcloudai-modelrouting-peak' },
    },
    // 场景15: Gateway 混合路由峰值
    gateway_mixed_peak: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '10s', target: 50 },
        { duration: '30s', target: 50 },
        { duration: '10s', target: 0 },
      ],
      exec: 'gatewayMixedPeak',
      startTime: '200s',
      tags: { group: 'gateway-mixed-peak' },
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};


// ═══════════════════════════════════════════════════
// 场景实现
// ═══════════════════════════════════════════════════

const stationId = '11111111-1111-1111-1111-111111111111';
const fenceId = '22222222-2222-2222-2222-222222222222';

export function geofenceCrud() {
  group('GeoFence CRUD', () => {
    // 列表
    let r = http.get(`${BASE_URL}/api/stations/${stationId}/geo-fences`, { headers });
    check(r, { 'geofence list < 500': (r) => r.status < 500 });

    // 创建
    r = http.post(`${BASE_URL}/api/stations/${stationId}/geo-fences`,
      JSON.stringify({ name: 'k6围栏', fenceType: 1, centerLongitude: 116.4, centerLatitude: 39.9, radiusMeters: 500, isActive: true }),
      { headers });
    check(r, { 'geofence create < 500': (r) => r.status < 500 });

    // 详情
    r = http.get(`${BASE_URL}/api/stations/${stationId}/geo-fences/${fenceId}`, { headers });
    check(r, { 'geofence detail < 500': (r) => r.status < 500 });

    // 更新
    r = http.put(`${BASE_URL}/api/stations/${stationId}/geo-fences/${fenceId}`,
      JSON.stringify({ name: '更新围栏', radiusMeters: 800 }),
      { headers });
    check(r, { 'geofence update < 500': (r) => r.status < 500 });

    // 删除
    r = http.del(`${BASE_URL}/api/stations/${stationId}/geo-fences/${fenceId}`, null, { headers });
    check(r, { 'geofence delete < 500': (r) => r.status < 500 });

    sleep(0.5);
  });
}

export function imageSearch() {
  group('ImageSearch', () => {
    let r = http.get(`${BASE_URL}/api/iotcloudai/image-search/status`, { headers });
    check(r, { 'imgsearch status < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/iotcloudai/image-search/by-text`,
      JSON.stringify({ query: '光伏', topK: 10, minScore: 0.3 }),
      { headers });
    check(r, { 'imgsearch text < 500': (r) => r.status < 500 });

    sleep(0.5);
  });
}

export function llmInference() {
  group('LLM Inference', () => {
    let r = http.get(`${BASE_URL}/api/iotcloudai/llm/models`, { headers });
    check(r, { 'llm models < 500': (r) => r.status < 500 });

    r = http.get(`${BASE_URL}/api/iotcloudai/llm/active`, { headers });
    check(r, { 'llm active < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/iotcloudai/llm/generate`,
      JSON.stringify({ prompt: '设备状态查询', maxTokens: 64, temperature: 0.7 }),
      { headers });
    check(r, { 'llm generate < 500': (r) => r.status < 500 });

    sleep(1);
  });
}

export function modelRouting() {
  group('ModelRouting', () => {
    const intents = ['device_query', 'prediction_query', 'charging_query', 'report_query'];
    const intent = intents[Math.floor(Math.random() * intents.length)];

    let r = http.post(`${BASE_URL}/api/v1/iotcloudai/model-routing/route`,
      JSON.stringify({ intentType: intent, scene: 'general', confidence: 0.85 }),
      { headers });
    check(r, { 'routing route < 500': (r) => r.status < 500 });

    r = http.get(`${BASE_URL}/api/v1/iotcloudai/model-routing/roles`, { headers });
    check(r, { 'routing roles < 500': (r) => r.status < 500 });

    r = http.get(`${BASE_URL}/api/v1/iotcloudai/model-routing/dashboard`, { headers });
    check(r, { 'routing dashboard < 500': (r) => r.status < 500 });

    sleep(0.3);
  });
}

export function solarPrediction() {
  group('SolarPrediction', () => {
    let r = http.get(`${BASE_URL}/api/iotcloudai/solar/status`, { headers });
    check(r, { 'solar status < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/iotcloudai/solar/predict`,
      JSON.stringify({ longitude: 116.4, latitude: 39.9, capacityKw: 100, tiltAngle: 30, azimuth: 180, forecastHours: 24 }),
      { headers });
    check(r, { 'solar predict < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/iotcloudai/solar/predict/physical`,
      JSON.stringify({ longitude: 116.4, latitude: 39.9, capacityKw: 100, forecastHours: 12 }),
      { headers });
    check(r, { 'solar physical < 500': (r) => r.status < 500 });

    sleep(0.5);
  });
}

export function visionInspection() {
  group('VisionInspection', () => {
    let r = http.post(`${BASE_URL}/api/iotcloudai/vision/inspect/pv`, null, { headers });
    check(r, { 'vision pv < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/iotcloudai/vision/inspect/charger`, null, { headers });
    check(r, { 'vision charger < 500': (r) => r.status < 500 });

    sleep(1);
  });
}

export function storageArchive() {
  group('StorageArchive', () => {
    let r = http.get(`${BASE_URL}/api/storage/archive/exists?objectKey=archive/test.gz`, { headers });
    check(r, { 'archive exists < 500': (r) => r.status < 500 });

    r = http.get(`${BASE_URL}/api/storage/archive/download-url?objectKey=archive/test.gz&expiresMinutes=30`, { headers });
    check(r, { 'archive download < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/storage/archive/upload`,
      JSON.stringify({ objectKey: 'archive/k6test.gz', contentBase64: 'dGVzdA==', serviceName: 'k6' }),
      { headers });
    check(r, { 'archive upload < 500': (r) => r.status < 500 });

    sleep(0.5);
  });
}

export function internalApi() {
  group('InternalAPI', () => {
    let r = http.post(`${BASE_URL}/api/internal/observability/alerts`,
      JSON.stringify({ alertId: `k6-${Date.now()}`, source: 'k6', severity: 'info', title: 'k6测试告警' }),
      { headers });
    check(r, { 'internal alert < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/internal/observability/notifications`,
      JSON.stringify({ notificationId: `k6-${Date.now()}`, source: 'k6', type: 'webhook', title: 'k6测试通知' }),
      { headers });
    check(r, { 'internal notify < 500': (r) => r.status < 500 });

    r = http.post(`${BASE_URL}/api/internal/workorder/from-alarm`,
      JSON.stringify({ alarmId: `k6-${Date.now()}`, deviceId: 'd001', severity: 'warning', alarmType: 'k6_test' }),
      { headers });
    check(r, { 'internal workorder < 500': (r) => r.status < 500 });

    sleep(0.3);
  });
}

export function gatewayRoutes() {
  group('GatewayRoutes', () => {
    const routes = [
      '/api/auth/health',             // platform
      '/api/permission/health',       // platform
      '/api/charging/health',         // charging
      '/api/settlement/health',       // charging
      '/api/vpp/health',              // energy
      '/api/microgrid/health',        // energy
      '/api/device/health',           // business
      '/api/station/health',          // business
      '/api/blockchain/health',       // advanced
      '/api/iotcloudai/health',       // advanced
    ];
    const route = routes[Math.floor(Math.random() * routes.length)];
    const r = http.get(`${BASE_URL}${route}`, { headers });
    check(r, { 'gateway route < 500': (r) => r.status < 500 });
    sleep(0.1);
  });
}

export function permissionRoles() {
  group('PermissionRoles', () => {
    const roleIds = [
      '00000000-0000-0000-0000-000000000001', // SUPER_ADMIN
      '00000000-0000-0000-0000-000000000010', // 安全管理员
      '00000000-0000-0000-0000-000000000011', // 审计管理员
      '00000000-0000-0000-0000-000000000012', // 系统管理员
    ];
    const roleId = roleIds[Math.floor(Math.random() * roleIds.length)];
    const r = http.get(`${BASE_URL}/api/role/permissions?roleId=${roleId}`, { headers });
    check(r, { 'permission roles < 500': (r) => r.status < 500 });
    sleep(0.3);
  });
}

export function tradingExpiration() {
  group('TradingExpiration', () => {
    let r = http.get(`${BASE_URL}/api/electrade/orders?page=1&pageSize=10&status=expired`, { headers });
    check(r, { 'expired orders < 500': (r) => r.status < 500 });

    r = http.get(`${BASE_URL}/api/electrade/bilateral-trades?page=1&pageSize=10&status=cancelled`, { headers });
    check(r, { 'cancelled trades < 500': (r) => r.status < 500 });

    sleep(0.3);
  });
}

export function ingestionSharding() {
  group('IngestionSharding', () => {
    let r = http.get(`${BASE_URL}/api/ingestion/protocol/status`, { headers });
    check(r, { 'ingestion status < 500': (r) => r.status < 500 });

    r = http.get(`${BASE_URL}/api/ingestion-message/list?page=1&pageSize=10`, { headers });
    check(r, { 'ingestion messages < 500': (r) => r.status < 500 });

    sleep(0.3);
  });
}

// ---- 峰值场景 ----

export function geofenceCheckPeak() {
  const lng = 116.3 + Math.random() * 0.2;
  const lat = 39.8 + Math.random() * 0.2;
  const r = http.post(`${BASE_URL}/api/stations/${stationId}/geo-fences/check`,
    JSON.stringify({ longitude: lng, latitude: lat }),
    { headers });
  check(r, { 'geofence check peak < 500': (r) => r.status < 500 });
}

export function modelRoutingPeak() {
  const intents = ['device_query', 'prediction_query', 'charging_query', 'report_query', 'alarm_query', 'general'];
  const intent = intents[Math.floor(Math.random() * intents.length)];
  const confidence = 0.3 + Math.random() * 0.7;
  const r = http.post(`${BASE_URL}/api/v1/iotcloudai/model-routing/route`,
    JSON.stringify({ intentType: intent, scene: 'general', confidence }),
    { headers });
  check(r, { 'routing peak < 500': (r) => r.status < 500 });
}

export function gatewayMixedPeak() {
  const endpoints = [
    '/api/auth/health', '/api/device/health', '/api/charging/health',
    '/api/vpp/health', '/api/blockchain/health', '/api/iotcloudai/health',
    `/api/stations/${stationId}/geo-fences`,
    '/api/iotcloudai/llm/models',
    '/api/iotcloudai/solar/status',
    '/api/storage/archive/exists?objectKey=test',
  ];
  const ep = endpoints[Math.floor(Math.random() * endpoints.length)];
  const r = http.get(`${BASE_URL}${ep}`, { headers });
  check(r, { 'gateway mixed peak < 500': (r) => r.status < 500 });
}
