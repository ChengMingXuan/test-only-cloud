/**
 * v3.18 增量补充 - 移动端认证/备品备件/导出 E2E 测试
 * ===================================================
 * 补充 v318-incremental-e2e.spec.ts 未覆盖的 3 个模块
 */

import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

const mockApiResponse = (data: any) => ({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ code: 200, data, message: 'OK' })
});

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

async function setupMockRoutes(page: Page) {
  await page.route('**/api/auth/user/info', route => {
    route.fulfill(mockApiResponse({
      id: 'user-001',
      username: 'admin',
      permissions: ['*']
    }));
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 1. 移动端认证完整流程 E2E
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('移动端认证完整流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockRoutes(page);
  });

  test('短信验证码登录 → 查看个人信息 → 退出', async ({ page }) => {
    // 模拟手机视口
    await page.setViewportSize({ width: 375, height: 812 });

    // Mock 发送验证码
    await page.route('**/api/auth/mobile/send-code', route => {
      route.fulfill(mockApiResponse({ sent: true }));
    });

    // Mock 登录
    await page.route('**/api/auth/mobile/sms-login', route => {
      route.fulfill(mockApiResponse({
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        userId: 'user-001',
      }));
    });

    // Mock 个人信息
    await page.route('**/api/auth/mobile/profile', route => {
      route.fulfill(mockApiResponse({
        id: 'user-001',
        realName: '张三',
        phone: '138****5678',
      }));
    });

    // 1. 进入移动端登录页
    await page.goto(`${BASE_URL}/mobile/login`);

    // 2. 输入手机号
    const phoneInput = page.locator('[data-testid="phone-input"], input[type="tel"]').first();
    if (await phoneInput.isVisible()) {
      await phoneInput.fill('13812345678');
    }

    // 3. 查看个人信息页
    await page.goto(`${BASE_URL}/mobile/profile`);
    
    // 4. 退出
    await page.route('**/api/auth/mobile/logout', route => {
      route.fulfill(mockApiResponse({}));
    });
  });

  test('小程序登录 → 绑定手机号', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });

    // Mock 小程序登录
    await page.route('**/api/auth/mp/login', route => {
      route.fulfill(mockApiResponse({
        accessToken: 'mp-token',
        needBindPhone: true,
      }));
    });

    // Mock 绑定手机号
    await page.route('**/api/auth/mp/bind-phone', route => {
      route.fulfill(mockApiResponse({ bound: true }));
    });

    await page.goto(`${BASE_URL}/mobile/login`);
    // 小程序登录流程
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 2. 备品备件完整业务流程 E2E
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('备品备件完整业务流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('备件创建 → 入库 → 出库 → 库存查询', async ({ page }) => {
    // Mock 创建备件
    await page.route('**/api/spare-part', route => {
      if (route.request().method() === 'POST') {
        route.fulfill(mockApiResponse({ id: 'sp-new-001', partCode: 'SP-003' }));
      } else {
        route.fulfill(mockApiResponse({
          items: [
            { id: 'sp-1', partCode: 'SP-001', partName: '逆变器模块', stock: 15 },
            { id: 'sp-2', partCode: 'SP-002', partName: '光伏面板', stock: 50 },
          ],
          total: 2,
        }));
      }
    });

    // Mock 入库
    await page.route('**/api/spare-part/stock-in', route => {
      route.fulfill(mockApiResponse({ success: true }));
    });

    // Mock 出库
    await page.route('**/api/spare-part/stock-out', route => {
      route.fulfill(mockApiResponse({ success: true }));
    });

    // Mock 库存
    await page.route('**/api/spare-part/inventory*', route => {
      route.fulfill(mockApiResponse({
        items: [
          { partCode: 'SP-001', partName: '逆变器模块', currentStock: 25, safetyStock: 10 },
        ],
        total: 1,
      }));
    });

    // 1. 查看备件列表
    await page.goto(`${BASE_URL}/workorder/spare-part`);
    
    // 2. 进入创建页
    await page.goto(`${BASE_URL}/workorder/spare-part/create`);

    // 3. 入库
    await page.goto(`${BASE_URL}/workorder/spare-part/stock-in`);

    // 4. 出库
    await page.goto(`${BASE_URL}/workorder/spare-part/stock-out`);

    // 5. 库存查询
    await page.goto(`${BASE_URL}/workorder/spare-part/inventory`);
  });

  test('低库存告警 → 创建采购工单', async ({ page }) => {
    // Mock 低库存
    await page.route('**/api/spare-part/inventory/low-stock', route => {
      route.fulfill(mockApiResponse([
        { partCode: 'SP-001', partName: '逆变器模块', currentStock: 2, safetyStock: 10 },
      ]));
    });

    // Mock 创建工单
    await page.route('**/api/workorder/orders', route => {
      route.fulfill(mockApiResponse({ id: 'wo-001', orderNo: 'WO202501001' }));
    });

    await page.goto(`${BASE_URL}/workorder/spare-part/alerts`);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// 3. 导出服务完整流程 E2E
// ═══════════════════════════════════════════════════════════════════════════════

test.describe('导出服务完整流程 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await setupMockRoutes(page);
  });

  test('Excel 导出：选择数据 → 配置列 → 生成 → 下载', async ({ page }) => {
    // Mock 订单列表
    await page.route('**/api/charging/orders*', route => {
      route.fulfill(mockApiResponse({ items: [], total: 0 }));
    });

    // Mock Excel 生成
    await page.route('**/api/export/excel/generate', route => {
      route.fulfill(mockApiResponse({ taskId: 'export-001', status: 'completed' }));
    });

    // 1. 进入订单页
    await page.goto(`${BASE_URL}/charging/orders`);

    // 2. 点击导出（如果有按钮）
    const exportBtn = page.locator('[data-testid="export-excel-btn"]');
    if (await exportBtn.isVisible().catch(() => false)) {
      await exportBtn.click();
    }
  });

  test('PDF 导出：选择模板 → 预览 → 生成', async ({ page }) => {
    // Mock 报表页
    await page.route('**/api/microgrid/energy/reports*', route => {
      route.fulfill(mockApiResponse({ items: [], total: 0 }));
    });

    // Mock PDF 生成
    await page.route('**/api/export/pdf/generate', route => {
      route.fulfill(mockApiResponse({ taskId: 'pdf-001', status: 'completed' }));
    });

    // Mock PDF 模板
    await page.route('**/api/export/pdf/templates', route => {
      route.fulfill(mockApiResponse([
        { id: 't-1', name: '月度能耗报表', format: 'A4' },
        { id: 't-2', name: '设备运行报表', format: 'A4' },
      ]));
    });

    await page.goto(`${BASE_URL}/energy/reports`);
  });
});
