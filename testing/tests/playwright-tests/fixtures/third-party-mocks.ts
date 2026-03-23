/**
 * Playwright 第三方服务 Mock — 仅 Mock 支付/短信等外部网关
 *
 * 平台内部 API 禁止 Mock（必须真实调用）。
 */
import { Page } from '@playwright/test';

/** 拦截第三方支付回调（模拟支付成功） */
export async function mockPaymentGateway(page: Page) {
  await page.route('**/api.alipay.com/**', (route) =>
    route.fulfill({ status: 200, body: JSON.stringify({ code: 'SUCCESS' }) }),
  );
  await page.route('**/api.mch.weixin.qq.com/**', (route) =>
    route.fulfill({ status: 200, body: JSON.stringify({ return_code: 'SUCCESS' }) }),
  );
}

/** 拦截短信网关（避免真实发送） */
export async function mockSmsGateway(page: Page) {
  await page.route('**/sms.tencentcloudapi.com/**', (route) =>
    route.fulfill({ status: 200, body: JSON.stringify({ SendStatusSet: [{ Code: 'Ok' }] }) }),
  );
}

/** 拦截邮件服务（避免真实发送） */
export async function mockEmailService(page: Page) {
  await page.route('**/email.tencentcloudapi.com/**', (route) =>
    route.fulfill({ status: 200, body: JSON.stringify({ RequestId: 'mock' }) }),
  );
}
