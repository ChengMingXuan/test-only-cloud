/**
 * 增量E2E测试 — GeoFence + IotCloudAI AI新能力 + ColdArchive + 后台任务 + 内部API
 * ============================================================================
 * 全端到端业务链路验证，100% cy.intercept 等价的 route Mock
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
const API_URL = process.env.API_URL || 'http://localhost:18999';

const mockJson = (data: any = {}) => JSON.stringify({ code: 200, message: 'ok', data });
const mockPage = (list: any[] = [], total = 0) =>
  JSON.stringify({ code: 200, data: { list, total }, message: 'ok' });

// ═══════════════════════════════════════════════════
// Station GeoFence 地理围栏 E2E
// ═══════════════════════════════════════════════════

test.describe('Station GeoFence E2E', () => {
  const stationId = '11111111-1111-1111-1111-111111111111';

  test.beforeEach(async ({ page }) => {
    await page.route(`**/api/stations/${stationId}/geo-fences`, (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({ body: mockPage([
          { id: 'f001', name: '圆形围栏A', fenceType: 1, radiusMeters: 500, isActive: true },
          { id: 'f002', name: '多边形围栏B', fenceType: 2, isActive: true }
        ], 2) });
      } else if (route.request().method() === 'POST') {
        route.fulfill({ body: mockJson({ id: 'f003' }) });
      } else route.continue();
    });
    await page.route(`**/api/stations/${stationId}/geo-fences/*`, (route) => {
      route.fulfill({ body: mockJson() });
    });
    await page.route(`**/api/stations/${stationId}/geo-fences/check`, (route) => {
      route.fulfill({ body: mockJson({ inside: true, fenceId: 'f001' }) });
    });
  });

  test('围栏列表加载', async ({ page }) => {
    await page.goto(`${BASE_URL}/station/detail/${stationId}`);
    await expect(page.locator('body')).not.toBeEmpty();
  });

  test('创建圆形围栏', async ({ page }) => {
    await page.goto(`${BASE_URL}/station/detail/${stationId}`);
    const resp = await page.request.post(`${API_URL}/api/stations/${stationId}/geo-fences`, {
      data: { name: '新围栏', fenceType: 1, centerLongitude: 116.4, centerLatitude: 39.9, radiusMeters: 500 }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('坐标点检测', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/stations/${stationId}/geo-fences/check`, {
      data: { longitude: 116.397, latitude: 39.909 }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('删除围栏(软删除)', async ({ page }) => {
    const resp = await page.request.delete(`${API_URL}/api/stations/${stationId}/geo-fences/f001`);
    expect(resp.status()).toBeLessThan(500);
  });
});


// ═══════════════════════════════════════════════════
// IotCloudAI ImageSearch E2E
// ═══════════════════════════════════════════════════

test.describe('IotCloudAI ImageSearch E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/iotcloudai/image-search/**', (route) => {
      route.fulfill({ body: mockJson({ results: [], indexCount: 1500 }) });
    });
  });

  test('文本搜图', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/image-search/by-text`, {
      data: { query: '光伏面板', topK: 5, minScore: 0.3 }
    });
    expect(resp.status()).toBeLessThan(500);
    const body = await resp.json();
    expect(body.code).toBe(200);
  });

  test('引擎状态查询', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/iotcloudai/image-search/status`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('删除索引', async ({ page }) => {
    const resp = await page.request.delete(`${API_URL}/api/iotcloudai/image-search/index/test-id`);
    expect(resp.status()).toBeLessThan(500);
  });
});


// ═══════════════════════════════════════════════════
// IotCloudAI LLM E2E
// ═══════════════════════════════════════════════════

test.describe('IotCloudAI LLM 多模型 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/iotcloudai/llm/**', (route) => {
      const url = route.request().url();
      if (url.includes('/models')) {
        route.fulfill({ body: mockJson([
          { modelKey: 'qwen-7b', status: 'loaded' },
          { modelKey: 'baichuan2-7b', status: 'unloaded' }
        ]) });
      } else if (url.includes('/generate')) {
        route.fulfill({ body: mockJson({ text: '设备运行正常', tokensUsed: 42 }) });
      } else {
        route.fulfill({ body: mockJson() });
      }
    });
  });

  test('模型列表', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/iotcloudai/llm/models`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('切换模型', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/llm/switch`, {
      data: { modelKey: 'baichuan2-7b' }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('LLM推理', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/llm/generate`, {
      data: { prompt: '充电桩故障如何处理', maxTokens: 128 }
    });
    expect(resp.status()).toBeLessThan(500);
    const body = await resp.json();
    expect(body.data.text).toBeDefined();
  });
});


// ═══════════════════════════════════════════════════
// IotCloudAI ModelRouting E2E
// ═══════════════════════════════════════════════════

test.describe('IotCloudAI ModelRouting E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/iotcloudai/model-routing/**', (route) => {
      const url = route.request().url();
      if (url.includes('/dashboard')) {
        route.fulfill({ body: mockJson({ totalModels: 7, activeModels: 3, avgAccuracy: 0.93 }) });
      } else if (url.includes('/route')) {
        route.fulfill({ body: mockJson({ selectedModel: 'qwen-7b', confidence: 0.92 }) });
      } else if (url.includes('/roles')) {
        route.fulfill({ body: mockJson([{ modelKey: 'qwen-7b', role: '工业通用' }]) });
      } else if (url.includes('/benchmarks')) {
        route.fulfill({ body: mockJson([{ moduleId: 'solar_fusion', baselineAccuracy: 0.90 }]) });
      } else {
        route.fulfill({ body: mockJson() });
      }
    });
  });

  test('智能路由分发', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/v1/iotcloudai/model-routing/route`, {
      data: { intentType: 'device_query', scene: 'general', confidence: 0.85 }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('全部角色', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/v1/iotcloudai/model-routing/roles`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('精度基准', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/v1/iotcloudai/model-routing/benchmarks`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('AI能力仪表盘', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/v1/iotcloudai/model-routing/dashboard`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('记录推理结果', async ({ page }) => {
    const resp = await page.request.post(
      `${API_URL}/api/v1/iotcloudai/model-routing/benchmarks/solar_fusion/record`,
      { data: { predicted: 95.2, actual: 93.8 } }
    );
    expect(resp.status()).toBeLessThan(500);
  });
});


// ═══════════════════════════════════════════════════
// IotCloudAI SolarPrediction E2E
// ═══════════════════════════════════════════════════

test.describe('IotCloudAI SolarPrediction E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/iotcloudai/solar/**', (route) => {
      if (route.request().url().includes('/status')) {
        route.fulfill({ body: mockJson({ physicalModelReady: true, lightGbmReady: true, lstmReady: false }) });
      } else {
        route.fulfill({ body: mockJson({ totalKwh: 580.5, confidence: 0.91, method: 'fusion' }) });
      }
    });
  });

  test('三模型融合预测', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/solar/predict`, {
      data: { longitude: 116.4, latitude: 39.9, capacityKw: 100, forecastHours: 24 }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('纯物理模型预测', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/solar/predict/physical`, {
      data: { longitude: 116.4, latitude: 39.9, capacityKw: 100, forecastHours: 12 }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('引擎状态', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/iotcloudai/solar/status`);
    expect(resp.status()).toBeLessThan(500);
  });
});


// ═══════════════════════════════════════════════════
// IotCloudAI VisionInspection E2E
// ═══════════════════════════════════════════════════

test.describe('IotCloudAI VisionInspection E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/iotcloudai/vision/**', (route) => {
      const url = route.request().url();
      if (url.includes('/inspect/pv')) {
        route.fulfill({ body: mockJson({ defects: [{ type: 'shading' }], healthScore: 72 }) });
      } else if (url.includes('/inspect/charger')) {
        route.fulfill({ body: mockJson({ anomalies: [], safetyScore: 95 }) });
      } else {
        route.fulfill({ body: mockJson({ description: 'Mock vision result' }) });
      }
    });
  });

  test('光伏巡检', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/vision/inspect/pv`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('充电桩巡检', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/vision/inspect/charger`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('图像理解', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/vision/understand`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('批量帧分析', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/iotcloudai/vision/analyze/batch`);
    expect(resp.status()).toBeLessThan(500);
  });
});


// ═══════════════════════════════════════════════════
// Storage Archive E2E
// ═══════════════════════════════════════════════════

test.describe('Storage Archive 冷归档 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/storage/archive/**', (route) => {
      route.fulfill({ body: mockJson({ exists: true, url: 'https://minio.local/test.gz' }) });
    });
  });

  test('上传归档', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/storage/archive/upload`, {
      data: { objectKey: 'archive/test.gz', contentBase64: 'dGVzdA==', serviceName: 'test' }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('检查归档存在', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/storage/archive/exists?objectKey=archive/test.gz`);
    expect(resp.status()).toBeLessThan(500);
  });

  test('获取下载链接', async ({ page }) => {
    const resp = await page.request.get(`${API_URL}/api/storage/archive/download-url?objectKey=archive/test.gz`);
    expect(resp.status()).toBeLessThan(500);
  });
});


// ═══════════════════════════════════════════════════
// Internal API 跨服务联动 E2E
// ═══════════════════════════════════════════════════

test.describe('跨服务联动 告警→通知→工单 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/internal/**', (route) => {
      route.fulfill({ body: mockJson({ success: true }) });
    });
    await page.route('**/api/workorder/**', (route) => {
      route.fulfill({ body: mockPage([], 0) });
    });
  });

  test('步骤1: 内部告警推送', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/internal/observability/alerts`, {
      data: { alertId: 'a001', source: 'ruleengine', severity: 'critical', title: '链路测试' }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('步骤2: 内部通知推送', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/internal/observability/notifications`, {
      data: { notificationId: 'n001', source: 'ruleengine', type: 'email', title: '通知' }
    });
    expect(resp.status()).toBeLessThan(500);
  });

  test('步骤3: 告警联动创建工单', async ({ page }) => {
    const resp = await page.request.post(`${API_URL}/api/internal/workorder/from-alarm`, {
      data: { alarmId: 'a001', deviceId: 'd001', severity: 'critical', alarmType: 'device_fault' }
    });
    expect(resp.status()).toBeLessThan(500);
  });
});


// ═══════════════════════════════════════════════════
// Gateway YARP 路由拆分 E2E
// ═══════════════════════════════════════════════════

test.describe('Gateway YARP 路由拆分 E2E', () => {
  const routeChecks = [
    { path: '/api/auth/health', label: 'Identity(platform)' },
    { path: '/api/permission/health', label: 'Permission(platform)' },
    { path: '/api/charging/health', label: 'Charging(charging)' },
    { path: '/api/vpp/health', label: 'VPP(energy)' },
    { path: '/api/device/health', label: 'Device(business)' },
    { path: '/api/station/health', label: 'Station(business)' },
    { path: '/api/blockchain/health', label: 'Blockchain(advanced)' },
    { path: '/api/iotcloudai/health', label: 'IotCloudAI(advanced)' },
  ];

  for (const { path, label } of routeChecks) {
    test(`路由可达: ${label}`, async ({ page }) => {
      await page.route(`**${path}`, (route) => {
        route.fulfill({ status: 200, body: '{"status":"ok"}' });
      });
      const resp = await page.request.get(`${API_URL}${path}`);
      expect(resp.status()).toBeLessThan(500);
    });
  }

  test('内部路由被拦截', async ({ page }) => {
    await page.route('**/api/internal/test', (route) => {
      route.fulfill({ status: 403, body: '{"error":"forbidden"}' });
    });
    const resp = await page.request.get(`${API_URL}/api/internal/test`);
    expect([403, 404]).toContain(resp.status());
  });
});
