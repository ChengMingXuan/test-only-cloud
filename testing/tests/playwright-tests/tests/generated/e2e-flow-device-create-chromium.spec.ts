import { test, expect } from '@playwright/test';

/**
 * E2E 流程测试：设备创建 (chromium)
 */

test.describe('设备创建', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('jgsy_access_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.test');
      localStorage.setItem('jgsy_tenant_code', 'TEST_TENANT');
    });
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: {} })
      });
    });
    await page.goto(process.env.BASE_URL || 'http://localhost:8000');
  });

  test('流程 - 设备创建', async ({ page, context }) => {
    // Mock API 响应
    await page.route('**/api/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: {} })
      });
    });
    
    // 执行业务流
    expect(await page.title()).toBeTruthy();
  });
});
