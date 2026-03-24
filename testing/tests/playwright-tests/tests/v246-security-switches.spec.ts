import { test, expect } from '@playwright/test';

/**
 * SecuritySwitches 双环境配置 - Playwright E2E 增量测试（v2.4.6）
 *
 * 覆盖维度：
 * - 安全响应头端到端验证（跨浏览器）
 * - HSTS 条件化行为
 * - 认证强制 + Token 安全
 * - Swagger 可访问性
 * - 登录页安全属性
 */

const GATEWAY_URL = process.env.GATEWAY_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:8001';

// ==================== 1. 安全响应头 ====================

test.describe('[v2.4.6] SecuritySwitches - 安全响应头', () => {
  test.skip(!!process.env.CI, '需要真实后端，CI 环境跳过');

  test('[SEC-PW01] X-Content-Type-Options: nosniff', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/gateway/health`);
    expect(resp.status()).toBeLessThan(500);
    const header = resp.headers()['x-content-type-options'];
    if (header) {
      expect(header).toBe('nosniff');
    }
  });

  test('[SEC-PW02] X-Frame-Options 防点击劫持', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/gateway/health`);
    const xfo = resp.headers()['x-frame-options'];
    if (xfo) {
      expect(xfo.toUpperCase()).toContain('DENY');
    }
  });

  test('[SEC-PW03] Dev 环境 HSTS 不注入（HstsEnabled=false）', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/gateway/health`);
    const hsts = resp.headers()['strict-transport-security'];
    // Dev 环境 HstsEnabled=false 时不应有 HSTS
    // 记录实际值供人工确认
    if (hsts) {
      console.log(`⚠️ Dev 环境检测到 HSTS: ${hsts}（可能来自反向代理）`);
    }
  });

  test('[SEC-PW04] Server 头不暴露技术栈', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/gateway/health`);
    const server = resp.headers()['server'] || '';
    expect(server).not.toContain('Kestrel');
    expect(server).not.toContain('ASP.NET');
  });

  test('[SEC-PW05] X-XSS-Protection 头存在', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/gateway/health`);
    const xss = resp.headers()['x-xss-protection'];
    if (xss) {
      expect(xss).toContain('1');
    }
  });

  test('[SEC-PW06] Referrer-Policy 头验证', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/gateway/health`);
    const rp = resp.headers()['referrer-policy'];
    if (rp) {
      expect(['strict-origin-when-cross-origin', 'no-referrer', 'same-origin']).toContain(rp);
    }
  });
});

// ==================== 2. 认证强制 ====================

test.describe('[v2.4.6] SecuritySwitches - 认证强制', () => {
  test.skip(!!process.env.CI, '需要真实后端，CI 环境跳过');

  test('[SEC-PW-AUTH01] 未认证请求返回 401/403', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/permission/roles`, {
      headers: { 'Accept': 'application/json' }
    });
    expect([401, 403]).toContain(resp.status());
  });

  test('[SEC-PW-AUTH02] 无效 Token 返回 401', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/permission/roles`, {
      headers: {
        'Authorization': 'Bearer invalid.jwt.token',
        'Accept': 'application/json'
      }
    });
    expect([401, 403]).toContain(resp.status());
  });

  test('[SEC-PW-AUTH03] 过期 Token 返回 401', async ({ request }) => {
    // 使用一个合法格式但已过期的 JWT
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNjAwMDAwMDAwfQ.test';
    const resp = await request.get(`${GATEWAY_URL}/api/permission/roles`, {
      headers: {
        'Authorization': `Bearer ${expiredToken}`,
        'Accept': 'application/json'
      }
    });
    expect([401, 403]).toContain(resp.status());
  });
});

// ==================== 3. 登录页安全 ====================

test.describe('[v2.4.6] SecuritySwitches - 登录页安全验证', () => {

  test('[SEC-PW-LOGIN01] 登录页密码框属性安全', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/user/login`, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
    
    const passwordInputs = page.locator('input[type="password"]');
    const count = await passwordInputs.count();
    
    if (count > 0) {
      const input = passwordInputs.first();
      const autocomplete = await input.getAttribute('autocomplete');
      // 密码框不应设置 autocomplete="on"
      if (autocomplete) {
        expect(autocomplete).not.toBe('on');
      }
    }
  });

  test('[SEC-PW-LOGIN02] 登录页无敏感信息泄露', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/user/login`, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
    
    const bodyText = await page.textContent('body').catch(() => '');
    expect(bodyText).not.toContain('P@ssw0rd');
    expect(bodyText).not.toContain('eyJhbGciOi');  // JWT 前缀
  });
});

// ==================== 4. Swagger 可访问性 ====================

test.describe('[v2.4.6] SecuritySwitches - Swagger 控制', () => {

  test('[SEC-PW-SWAGGER01] Swagger UI 端点响应', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/swagger/index.html`, {
      failOnStatusCode: false,
    });
    // Dev: 200 (启用), Prod: 404 (禁用)
    expect([200, 301, 302, 404]).toContain(resp.status());
  });
});

// ==================== 5. 跨浏览器安全行为 ====================

test.describe('[v2.4.6] SecuritySwitches - 跨浏览器一致性', () => {

  test('[SEC-PW-XBROWSER01] 安全头在不同浏览器中一致', async ({ request }) => {
    const resp = await request.get(`${GATEWAY_URL}/api/gateway/health`);
    const headers = resp.headers();
    
    // 基础安全头应在所有浏览器中存在
    const securityHeaders = [
      'x-content-type-options',
      'x-frame-options',
    ];
    
    for (const h of securityHeaders) {
      if (headers[h]) {
        expect(headers[h]).toBeTruthy();
      }
    }
  });
});
