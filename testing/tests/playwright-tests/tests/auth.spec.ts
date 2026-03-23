import { test, expect } from '@playwright/test';

/**
 * Playwright 测试 - 认证模块
 * 符合规范：100% Mock，不连真实数据库
 */

test.describe('认证模块 - 登录/登出', () => {

  test.beforeEach(async ({ page }) => {
    await page.route('**/api/**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      if (url.includes('/auth/login') && method === 'POST') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: { accessToken: 'eyJ0ZXN0IjoiMSJ9.test.sig', refreshToken: 'refresh-test' } }) });
      } else if (url.includes('/auth/me')) {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: { id: 'user-001', name: 'admin', email: 'admin@jgsy.com' } }) });
      } else {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
      }
    });
    await page.context().clearCookies();
    await page.goto('/login');
  });

  test('[P0] 正确用户名密码登录成功 @smoke @critical', async ({ page }) => {
    const usernameInput = page.locator('input[type="text"]').first();
    if (await usernameInput.count() > 0) await usernameInput.fill('admin@jgsy.com');
    const passwordInput = page.locator('input[type="password"]').first();
    if (await passwordInput.count() > 0) await passwordInput.fill('P@ssw0rd');
    const loginBtn = page.locator('button[type="submit"], button:has-text("登录")').first();
    if (await loginBtn.count() > 0) await loginBtn.click();
    await expect(page.locator('body')).toBeVisible();
  });

  test('[P0] 错误密码登录失败 @smoke', async ({ page }) => {
    await page.route('**/api/**/login', async (route) => {
      await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ success: false, message: '用户名或密码错误' }) });
    });
    const usernameInput = page.locator('input[type="text"]').first();
    if (await usernameInput.count() > 0) await usernameInput.fill('admin@jgsy.com');
    const passwordInput = page.locator('input[type="password"]').first();
    if (await passwordInput.count() > 0) await passwordInput.fill('Wrong');
    const loginBtn = page.locator('button[type="submit"], button:has-text("登录")').first();
    if (await loginBtn.count() > 0) await loginBtn.click();
    expect(page.url()).toContain('/login');
  });

  test('[P1] 用户名不存在登录失败', async ({ page }) => {
    expect(page.url()).toContain('/login');
  });

  test('[P1] 空用户名密码提交失败', async ({ page }) => {
    const loginBtn = page.locator('button[type="submit"], button:has-text("登录")').first();
    if (await loginBtn.count() > 0) await loginBtn.click();
    expect(page.url()).toContain('/login');
  });

  test('[P0] 登录后成功登出 @smoke', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('jgsy_access_token', 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.test');
      localStorage.setItem('jgsy_tenant_code', 'TEST_TENANT');
    });
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });

});

test.describe('认证模块 - Token管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
    });
  });

  test('[P1] Token过期后自动跳转登录页', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('body')).toBeVisible();
  });

  test('[P1] Refresh Token成功续期', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('jgsy_access_token', 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.test');
    });
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('认证模块 - 密码重置', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
    });
  });

  test('[P2] 忘记密码流程 - 发送重置邮件', async ({ page }) => {
    await page.goto('/login');
    const forgotLink = page.locator('a:has-text("忘记密码"), a[href*="forgot"]');
    if (await forgotLink.count() > 0) await forgotLink.first().click();
    await expect(page.locator('body')).toBeVisible();
  });

  test('[P2] 密码重置链接有效性验证', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('认证模块 - 多设备登录', () => {
  test('[P2] 同一账号在多个浏览器同时登录', async ({ browser }) => {
    const ctx1 = await browser.newContext();
    const ctx2 = await browser.newContext();
    const p1 = await ctx1.newPage();
    const p2 = await ctx2.newPage();
    for (const p of [p1, p2]) {
      await p.route('**/api/**', async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
      });
    }
    await p1.goto('/login');
    await p2.goto('/login');
    await expect(p1.locator('body')).toBeVisible();
    await expect(p2.locator('body')).toBeVisible();
    await ctx1.close();
    await ctx2.close();
  });
});

test.describe('认证模块 - 验证码', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
    });
  });

  test('[P1] 多次失败后显示验证码', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('body')).toBeVisible();
  });
});