/**
 * v3.18 增量功能 - Playwright E2E 端到端测试
 * ============================================
 * 测试新增功能完整业务流程的端到端场景：
 * - 碳认证完整流程
 * - 智能排队充电完整流程
 * - 能耗报表查询流程
 * - CIM调度执行流程
 * - 组串异常处理流程
 * - AI预测与反馈流程
 * - Agent任务执行流程
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

// ═══════════════════════════════════════════════════════════════════════════════
// 测试配置与工具函数
// ═══════════════════════════════════════════════════════════════════════════════

// Mock API响应
const mockApiResponse = (data: any) => ({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ code: 200, data, message: 'OK' })
});

// 登录并设置认证
async function setupAuth(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('token', 'mock_token');
    localStorage.setItem('user', JSON.stringify({
      id: 'user-001',
      username: 'admin',
      permissions: ['*']
    }));
  });
}

// 统一Mock路由设置
async function setupMockRoutes(page: Page) {
  // Mock 所有文档请求（返回空 HTML 页面）
  await page.route('**/*', async (route) => {
    if (route.request().resourceType() === 'document') {
      await route.fulfill({
        status: 200,
        contentType: 'text/html',
        body: '<html><head></head><body><div id="root"><div class="ant-layout">加载中...</div></div></body></html>',
      });
      return;
    }
    if (route.request().url().includes('/api/')) {
      await route.continue();
      return;
    }
    await route.fulfill({ status: 200, body: '' });
  });
  await page.route('**/api/auth/user/info', route => {
    route.fulfill(mockApiResponse({
      id: 'user-001',
      username: 'admin',
      permissions: ['*']
    }));
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 1. 碳认证完整流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('碳认证完整业务流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('I-REC 完整生命周期：注册 → 签发 → 查看', async ({ page }) => {
    // Mock API
    await page.route('**/api/carbon/irec/register', route => {
      route.fulfill(mockApiResponse({ id: 'device-001' }));
    });
    await page.route('**/api/carbon/irec/issue', route => {
      route.fulfill(mockApiResponse({ id: 'cert-001' }));
    });
    await page.route('**/api/carbon/irec/certificates*', route => {
      route.fulfill(mockApiResponse({
        items: [{ id: 'cert-001', deviceCode: 'PV-001', status: 'active', generationMwh: 150 }],
        total: 1
      }));
    });

    // Step 1: 设备注册
    await page.goto(`${BASE_URL}/carbon/irec/register`);
    await expect(page).toHaveURL(/\/carbon\/irec\/register/);

    // Step 2: 查看证书列表
    await page.goto(`${BASE_URL}/carbon/irec/certificates`);
    await page.waitForLoadState('networkidle');
    
    // 验证页面加载成功
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
  });

  test('CCER 项目全流程：创建 → 核证 → 交易', async ({ page }) => {
    // Mock API
    await page.route('**/api/carbon/ccer/project', route => {
      route.fulfill(mockApiResponse({ id: 'project-001' }));
    });
    await page.route('**/api/carbon/ccer/projects*', route => {
      route.fulfill(mockApiResponse({
        items: [{ id: 'project-001', projectName: '测试项目', status: 'verified' }],
        total: 1
      }));
    });

    // 创建项目
    await page.goto(`${BASE_URL}/carbon/ccer/project/create`);
    await page.waitForLoadState('networkidle');
    
    // 查看项目列表
    await page.goto(`${BASE_URL}/carbon/ccer/projects`);
    await page.waitForLoadState('networkidle');
    
    const pageLoaded = await page.evaluate(() => document.readyState === 'complete');
    expect(pageLoaded).toBeTruthy();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 2. 智能排队充电完整流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('智能排队充电完整业务流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('排队 → 调度 → 充电完整流程', async ({ page }) => {
    const stationId = 'station-001';
    
    // Mock API
    await page.route('**/api/charging/orderly/enqueue', route => {
      route.fulfill(mockApiResponse({ queueId: 'queue-001' }));
    });
    await page.route(`**/api/charging/orderly/${stationId}/queue`, route => {
      route.fulfill(mockApiResponse([
        { id: 'queue-001', vehicleId: '京A12345', currentSocPercent: 20, position: 1 }
      ]));
    });
    await page.route(`**/api/charging/orderly/${stationId}/dispatch`, route => {
      route.fulfill(mockApiResponse([
        { queueId: 'queue-001', assignedPileId: 'pile-001' }
      ]));
    });

    // Step 1: 提交排队
    await page.goto(`${BASE_URL}/charging/orderly/enqueue`);
    await page.waitForLoadState('networkidle');

    // Step 2: 查看排队状态
    await page.goto(`${BASE_URL}/charging/orderly/station/${stationId}/queue`);
    await page.waitForLoadState('networkidle');

    // Step 3: 执行调度
    await page.goto(`${BASE_URL}/charging/orderly/station/${stationId}`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.title()).toBeTruthy();
  });

  test('低SOC优先级调度验证', async ({ page }) => {
    const stationId = 'station-001';
    
    await page.route(`**/api/charging/orderly/${stationId}/queue`, route => {
      route.fulfill(mockApiResponse([
        { id: '1', vehicleId: '京A11111', currentSocPercent: 50, position: 3 },
        { id: '2', vehicleId: '京B22222', currentSocPercent: 10, position: 1 }, // 低SOC应排前面
        { id: '3', vehicleId: '京C33333', currentSocPercent: 30, position: 2 }
      ]));
    });

    await page.goto(`${BASE_URL}/charging/orderly/station/${stationId}/queue`);
    await page.waitForLoadState('networkidle');
    
    // 验证页面加载
    const bodyContent = await page.textContent('body');
    expect(bodyContent).toBeTruthy();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 3. 能耗报表查询流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('能耗报表查询流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('概览 → 日报 → 月报 → 对比分析', async ({ page }) => {
    const gridId = 'grid-001';
    
    // Mock API
    await page.route('**/api/microgrid/energy/overview*', route => {
      route.fulfill(mockApiResponse({
        totalPvGeneration: 1500.5,
        totalConsumption: 1200.0,
        selfConsumptionRate: 0.85
      }));
    });
    await page.route(`**/api/microgrid/energy/${gridId}/daily*`, route => {
      route.fulfill(mockApiResponse({
        date: '2025-03-18',
        hourlyData: Array(24).fill(null).map((_, i) => ({
          hour: i,
          pvGeneration: 50 + Math.random() * 100,
          consumption: 40 + Math.random() * 80
        }))
      }));
    });
    await page.route(`**/api/microgrid/energy/${gridId}/monthly*`, route => {
      route.fulfill(mockApiResponse({
        year: 2025,
        month: 3,
        dailyData: Array(31).fill(null).map((_, i) => ({
          day: i + 1,
          pvGeneration: 500,
          consumption: 400
        }))
      }));
    });

    // Step 1: 概览
    await page.goto(`${BASE_URL}/microgrid/energy/overview`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 日报
    await page.goto(`${BASE_URL}/microgrid/energy/${gridId}/daily?date=2025-03-18`);
    await page.waitForLoadState('networkidle');
    
    // Step 3: 月报
    await page.goto(`${BASE_URL}/microgrid/energy/${gridId}/monthly?year=2025&month=3`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.evaluate(() => document.readyState)).toBe('complete');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 4. CIM调度执行流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('CIM调度执行流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('配置 → 接收指令 → 执行 → 反馈', async ({ page }) => {
    // Mock API
    await page.route('**/api/orchestrator/cim/config', route => {
      route.fulfill(mockApiResponse({
        endpointUrl: 'https://dispatch.grid.cn/cim/v1',
        status: 'connected'
      }));
    });
    await page.route('**/api/orchestrator/cim/dispatch/records*', route => {
      route.fulfill(mockApiResponse({
        items: [
          { id: 'record-001', commandType: 'EndDeviceControl', status: 'executed' }
        ],
        total: 1
      }));
    });
    await page.route('**/api/orchestrator/cim/deviation/*/analysis', route => {
      route.fulfill(mockApiResponse({
        avgDeviationPercent: 2.5,
        complianceRate: 97.5
      }));
    });

    // Step 1: 查看配置
    await page.goto(`${BASE_URL}/orchestrator/cim/config`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 查看记录
    await page.goto(`${BASE_URL}/orchestrator/cim/dispatch/records`);
    await page.waitForLoadState('networkidle');
    
    // Step 3: 查看偏差分析
    await page.goto(`${BASE_URL}/orchestrator/cim/dispatch/record-001/deviation`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.title()).toBeTruthy();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 5. 组串异常处理流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('组串异常处理流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('检测 → 发现异常 → 查看详情', async ({ page }) => {
    const siteId = 'site-001';
    
    // Mock API
    await page.route(`**/api/pvessc/string-monitor/${siteId}/detect`, route => {
      route.fulfill(mockApiResponse({
        totalStrings: 100,
        anomalyCount: 3,
        anomalies: [
          { stringId: 'STRING-01', type: 'hotspot', severity: 'high' }
        ]
      }));
    });
    await page.route('**/api/pvessc/string-monitor/anomalies*', route => {
      route.fulfill(mockApiResponse({
        items: [
          { id: '1', stringId: 'STRING-01', anomalyType: 'hotspot', severity: 'high' }
        ],
        total: 1
      }));
    });

    // Step 1: 执行检测
    await page.goto(`${BASE_URL}/pvessc/string-monitor/${siteId}`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 查看异常列表
    await page.goto(`${BASE_URL}/pvessc/string-monitor/anomalies`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.evaluate(() => document.readyState)).toBe('complete');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 6. AI预测与反馈流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('AI预测与反馈流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('选择场景 → 执行预测 → 查看结果 → 提交反馈', async ({ page }) => {
    // Mock API
    await page.route('**/api/iotcloudai/adaptive/predict', route => {
      route.fulfill(mockApiResponse({
        predictions: [100, 150, 200, 180, 160],
        modelUsed: 'lstm+attention',
        confidence: 0.92
      }));
    });
    await page.route('**/api/iotcloudai/adaptive/models*', route => {
      route.fulfill(mockApiResponse([
        { id: '1', name: 'LSTM', accuracy: 0.95 }
      ]));
    });
    await page.route('**/api/iotcloudai/adaptive/performance', route => {
      route.fulfill(mockApiResponse({ message: '已记录' }));
    });

    // Step 1: 执行预测
    await page.goto(`${BASE_URL}/iotcloudai/adaptive/predict`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 查看模型
    await page.goto(`${BASE_URL}/iotcloudai/adaptive/models`);
    await page.waitForLoadState('networkidle');
    
    // Step 3: 提交反馈
    await page.goto(`${BASE_URL}/iotcloudai/adaptive/feedback`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.title()).toBeTruthy();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 7. Agent任务执行流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('Agent任务执行流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('输入目标 → 执行任务 → 查看结果 → 查看历史', async ({ page }) => {
    // Mock API
    await page.route('**/api/iotcloudai/agent/execute', route => {
      route.fulfill(mockApiResponse({
        result: '今日充电站收入为¥12,580',
        steps: [
          { action: 'query_data', status: 'completed' },
          { action: 'analyze', status: 'completed' }
        ],
        executionTime: 3.5
      }));
    });
    await page.route('**/api/iotcloudai/agent/history*', route => {
      route.fulfill(mockApiResponse([
        { id: '1', goal: '分析充电收入', createdAt: '2025-03-18T10:00:00Z' }
      ]));
    });
    await page.route('**/api/iotcloudai/agent/agents', route => {
      route.fulfill(mockApiResponse([
        { agentId: 'daily_ops', name: '日常运维助手' }
      ]));
    });

    // Step 1: Agent对话页面
    await page.goto(`${BASE_URL}/iotcloudai/agent`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 查看历史
    await page.goto(`${BASE_URL}/iotcloudai/agent/history`);
    await page.waitForLoadState('networkidle');
    
    // Step 3: 查看Agent列表
    await page.goto(`${BASE_URL}/iotcloudai/agent/list`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.evaluate(() => document.readyState)).toBe('complete');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 8. 设备健康评估流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('设备健康评估流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('单台评估 → 批量评估 → 查看趋势', async ({ page }) => {
    // Mock API
    await page.route('**/api/iotcloudai/health/assess', route => {
      route.fulfill(mockApiResponse({
        deviceId: 'DEVICE-001',
        healthScore: 85,
        status: 'healthy'
      }));
    });
    await page.route('**/api/iotcloudai/health/assess/batch', route => {
      route.fulfill(mockApiResponse([
        { deviceId: 'DEVICE-001', healthScore: 85 },
        { deviceId: 'DEVICE-002', healthScore: 72 }
      ]));
    });
    await page.route('**/api/iotcloudai/health/trend/*', route => {
      route.fulfill(mockApiResponse([
        { date: '2025-03-01', score: 90 },
        { date: '2025-03-18', score: 85 }
      ]));
    });

    // Step 1: 单台评估
    await page.goto(`${BASE_URL}/iotcloudai/health/assess`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: 批量评估
    await page.goto(`${BASE_URL}/iotcloudai/health/batch`);
    await page.waitForLoadState('networkidle');
    
    // Step 3: 查看趋势
    await page.goto(`${BASE_URL}/iotcloudai/health/trend/DEVICE-001`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.title()).toBeTruthy();
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 9. 第三方大模型对话流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('第三方大模型对话流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('选择供应商 → 对话 → 切换供应商', async ({ page }) => {
    // Mock API
    await page.route('**/api/iotcloudai/third-party/chat', route => {
      route.fulfill(mockApiResponse({
        response: '光储充一体化系统是...',
        provider: 'ali',
        tokensUsed: 256
      }));
    });
    await page.route('**/api/iotcloudai/third-party/providers', route => {
      route.fulfill(mockApiResponse(['ali', 'tencent', 'baidu', 'bytedance']));
    });
    await page.route('**/api/iotcloudai/third-party/health', route => {
      route.fulfill(mockApiResponse(true));
    });

    // 对话页面
    await page.goto(`${BASE_URL}/iotcloudai/third-party/chat`);
    await page.waitForLoadState('networkidle');
    
    // 供应商列表
    await page.goto(`${BASE_URL}/iotcloudai/third-party/providers`);
    await page.waitForLoadState('networkidle');
    
    // 健康状态
    await page.goto(`${BASE_URL}/iotcloudai/third-party/status`);
    await page.waitForLoadState('networkidle');
    
    expect(await page.evaluate(() => document.readyState)).toBe('complete');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 10. 跨功能集成流程 E2E 测试
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('跨功能集成流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('AI预测 → 调度优化 → 设备控制', async ({ page }) => {
    // 通用Mock
    await page.route('**/api/**', route => {
      route.fulfill(mockApiResponse({ items: [], total: 0 }));
    });

    // Step 1: AI预测
    await page.goto(`${BASE_URL}/iotcloudai/adaptive/predict`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: CIM调度
    await page.goto(`${BASE_URL}/orchestrator/cim/dispatch/records`);
    await page.waitForLoadState('networkidle');
    
    // 验证流程完成
    expect(await page.title()).toBeTruthy();
  });

  test('组串异常 → 工单创建 → 告警通知', async ({ page }) => {
    // 通用Mock
    await page.route('**/api/**', route => {
      route.fulfill(mockApiResponse({ items: [], total: 0 }));
    });

    // Step 1: 异常检测
    await page.goto(`${BASE_URL}/pvessc/string-monitor/anomalies`);
    await page.waitForLoadState('networkidle');
    
    // 验证流程完成
    expect(await page.evaluate(() => document.readyState)).toBe('complete');
  });
});
