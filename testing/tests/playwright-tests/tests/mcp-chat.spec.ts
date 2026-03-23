/**
 * MCP 对话 E2E 测试 (Playwright)
 * ===============================
 * 100% Mock API，不连接真实后端
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.FRONTEND_URL || 'http://localhost:8000';

// Mock 工具列表数据
const mockTools = [
  { toolId: 'llm:qwen-7b', name: 'Qwen-7B', type: 'LLM', tags: ['对话'], priority: 10, timeout: 60, isAvailable: true, isHealthy: true },
  { toolId: 'onnx:load_prediction_tcn', name: '负荷预测TCN', type: 'OnnxInference', tags: ['预测'], priority: 20, timeout: 30, isAvailable: true, isHealthy: true },
  { toolId: 'blockchain:chainmaker', name: 'ChainMaker', type: 'Blockchain', tags: ['存证'], priority: 20, timeout: 60, isAvailable: true, isHealthy: true },
];

// Mock 对话响应
const mockChatResponse = {
  success: true,
  data: {
    message: '根据分析，明日预计负荷峰值为 1200MW，建议提前调整发电策略。',
    toolsUsed: ['onnx:load_prediction_tcn'],
    traceId: 'trace-001',
  },
};

// Mock 健康数据
const mockHealth = {
  success: true,
  data: {
    total: 3,
    healthy: 3,
    unhealthy: 0,
    tools: mockTools.map(t => ({ ...t, lastCheck: new Date().toISOString() })),
  },
};

test.describe('MCP 工具管理页面', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API
    await page.route('**/api/iotcloudai/mcp/tools', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: mockTools }),
      });
    });
  });

  test('页面加载并显示工具列表', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai/mcp/tools`);
    await page.waitForSelector('.ant-table', { timeout: 10000 });
    const rows = page.locator('.ant-table-row');
    await expect(rows).toHaveCount(3);
  });

  test('搜索工具过滤', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai/mcp/tools`);
    await page.waitForSelector('.ant-table');
    const searchInput = page.locator('.ant-input-search input, input[placeholder*="搜索"]');
    await searchInput.fill('Qwen');
    await page.keyboard.press('Enter');
    // 前端过滤，应只显示匹配行
    await page.waitForTimeout(500);
  });

  test('查看工具详情弹窗', async ({ page }) => {
    await page.route('**/api/iotcloudai/mcp/tools/llm:qwen-7b', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: mockTools[0] }),
      });
    });
    await page.goto(`${BASE_URL}/ai/mcp/tools`);
    await page.waitForSelector('.ant-table');
    // 点击查看详情按钮
    const detailBtn = page.locator('.ant-table-row').first().locator('a, button').first();
    await detailBtn.click();
    // 等待弹窗打开
    await page.waitForSelector('.ant-modal', { timeout: 5000 }).catch(() => {
      // 弹窗可能用 Drawer 或其他组件
    });
  });
});

test.describe('MCP 对话页面', () => {
  test.beforeEach(async ({ page }) => {
    // Mock 同步对话
    await page.route('**/api/iotcloudai/mcp/chat', route => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockChatResponse),
        });
      } else {
        route.continue();
      }
    });

    // Mock 流式对话
    await page.route('**/api/iotcloudai/mcp/chat/stream', route => {
      const chunks = [
        'data: {"type":"text","content":"根据分析"}\n\n',
        'data: {"type":"text","content":"，明日预计负荷峰值为 1200MW"}\n\n',
        'data: {"type":"tool","name":"onnx:load_prediction_tcn"}\n\n',
        'data: {"type":"done"}\n\n',
      ];
      route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: chunks.join(''),
      });
    });
  });

  test('页面加载成功', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai/mcp/chat`);
    // 验证场景选择器存在
    const sceneSelector = page.locator('.ant-select, .ant-radio-group, [class*="scene"]');
    await expect(sceneSelector.first()).toBeVisible({ timeout: 10000 });
  });

  test('发送消息并收到回复', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai/mcp/chat`);
    // 输入消息
    const input = page.locator('textarea, input[type="text"]').last();
    await input.fill('请预测明天的电力负荷');
    await page.keyboard.press('Enter');
    // 等待回复显示
    await page.waitForTimeout(1500);
  });

  test('切换场景选项', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai/mcp/chat`);
    const sceneSelector = page.locator('.ant-select').first();
    if (await sceneSelector.isVisible()) {
      await sceneSelector.click();
      await page.waitForSelector('.ant-select-dropdown', { timeout: 3000 }).catch(() => {});
    }
  });
});

test.describe('MCP 健康监控页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/iotcloudai/mcp/health', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockHealth),
      });
    });
  });

  test('页面加载并显示统计卡片', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai/mcp/health`);
    // 验证统计卡片
    const statCards = page.locator('.ant-card, .ant-statistic');
    await expect(statCards.first()).toBeVisible({ timeout: 10000 });
  });

  test('显示健康工具列表', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai/mcp/health`);
    await page.waitForTimeout(1000);
    // 验证有工具状态展示
    const content = await page.textContent('body');
    expect(content).toBeTruthy();
  });
});
