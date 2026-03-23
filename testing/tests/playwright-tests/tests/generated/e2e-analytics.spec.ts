import { test, expect } from '@playwright/test';

test.describe('analytics', () => {
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
  });

  test('load', async ({ page }) => {
    await page.goto('/analytics');
    await expect(page.locator('body')).toBeVisible();
  });
});
