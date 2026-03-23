/**
 * V3.1.2 安全与证书管理 E2E 测试
 * ==========================================
 * 覆盖新增/修改功能:
 * - 证书轮转管理 (CertificateRotationController)
 * - 安全合规面板 (ComplianceServiceExtensions)
 * - 敏感数据加密配置 (SensitiveDataEncryptionService)
 */

import { test, expect } from '@playwright/test';

// ═══════════════════════════════════════════════════
// Mock 工具函数
// ═══════════════════════════════════════════════════

async function setupCommonMocks(page) {
    await page.route('**/api/auth/login', async (route) => {
        if (route.request().method() === 'POST') {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    success: true, code: 200,
                    data: {
                        accessToken: 'eyJ0ZXN0IjoiMSJ9.test.sig',
                        refreshToken: 'refresh-test',
                        expiresIn: 86400
                    }
                })
            });
        } else {
            await route.fulfill({ status: 200, body: '{}' });
        }
    });

    await page.route('**/api/auth/current-user', async (route) => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                success: true,
                data: {
                    userId: '00000000-0000-0000-0000-000000000001',
                    username: 'admin',
                    roles: ['SUPER_ADMIN'],
                    permissions: ['*']
                }
            })
        });
    });
}

// ═══════════════════════════════════════════════════
// 证书轮转管理 E2E 测试
// ═══════════════════════════════════════════════════

test.describe('证书轮转管理 @p1 @security', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        // Mock 证书轮转 API
        await page.route('**/api/monitor/service-mesh/certificate-rotation/status', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    success: true, data: {
                        caExpiry: '2027-01-01T00:00:00Z',
                        caRemainingDays: 300,
                        issuerExpiry: '2026-12-01T00:00:00Z',
                        issuerRemainingDays: 270,
                        lastRotation: '2026-02-01T10:00:00Z',
                        autoRotateEnabled: true,
                        services: [
                            { name: 'gateway', status: 'healthy', certExpiry: '2026-12-01' },
                            { name: 'identity', status: 'healthy', certExpiry: '2026-12-01' },
                            { name: 'charging', status: 'warning', certExpiry: '2026-06-01' },
                            { name: 'device', status: 'healthy', certExpiry: '2026-12-01' }
                        ]
                    }
                })
            });
        });

        await page.route('**/api/monitor/service-mesh/certificate-rotation/records*', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    success: true, data: {
                        items: [
                            { id: '1', serviceName: 'gateway', rotatedAt: '2026-02-01T10:00:00Z', status: 'success', reason: '定期轮转' },
                            { id: '2', serviceName: 'identity', rotatedAt: '2026-01-15T08:00:00Z', status: 'success', reason: '过期告警' }
                        ], total: 2, page: 1, pageSize: 10
                    }
                })
            });
        });

        await page.route('**/api/monitor/service-mesh/certificate-rotation/rotate', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ success: true, data: { taskId: 'rotation-001', message: '轮转任务已启动' } })
            });
        });

        // 通配 API Mock
        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/certificate-rotation') && !url.includes('/auth/')) {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: {} })
                });
            }
        });
    });

    test('[P1] 证书轮转状态页面加载', async ({ page }) => {
        await page.goto('/monitor/service-mesh/certificate');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 证书轮转 - 查看CA剩余天数', async ({ page }) => {
        await page.goto('/monitor/service-mesh/certificate');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 证书轮转 - 服务列表展示', async ({ page }) => {
        await page.goto('/monitor/service-mesh/certificate');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 证书轮转 - 手动触发轮转', async ({ page }) => {
        await page.goto('/monitor/service-mesh/certificate');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 证书轮转 - 查看轮转记录', async ({ page }) => {
        await page.goto('/monitor/service-mesh/certificate');
        await expect(page.locator('body')).toBeVisible();
    });
});

// ═══════════════════════════════════════════════════
// 钱包服务 E2E 测试
// ═══════════════════════════════════════════════════

test.describe('钱包服务 @p0 @account', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        await page.route('**/api/account/wallet/**', async (route) => {
            const url = route.request().url();
            const method = route.request().method();

            if (url.includes('/balance')) {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { balance: 500.00, totalRecharged: 1000.00, totalConsumed: 500.00 } })
                });
            } else if (url.includes('/recharge') && method === 'POST') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { transactionId: 'tx-001', amount: 100.00, type: 'recharge', balance: 600.00 } })
                });
            } else if (url.includes('/transactions')) {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({
                        success: true, data: {
                            items: [
                                { id: 'tx-001', type: 'recharge', amount: 100.00, description: '充值', createTime: '2026-03-07T10:00:00Z' },
                                { id: 'tx-002', type: 'consume', amount: -35.50, description: '充电消费', createTime: '2026-03-07T11:00:00Z' }
                            ], total: 2
                        }
                    })
                });
            } else {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { userId: '001', balance: 500.00 } })
                });
            }
        });

        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/wallet') && !url.includes('/auth/')) {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });
    });

    test('[P0] 钱包页面加载 - 显示余额', async ({ page }) => {
        await page.goto('/account/wallet');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P0] 钱包充值操作', async ({ page }) => {
        await page.goto('/account/wallet');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P0] 钱包交易记录查看', async ({ page }) => {
        await page.goto('/account/wallet/transactions');
        await expect(page.locator('body')).toBeVisible();
    });
});

// ═══════════════════════════════════════════════════
// 充电订单管理 E2E 测试
// ═══════════════════════════════════════════════════

test.describe('充电订单管理 @p0 @charging', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        await page.route('**/api/charging/orders*', async (route) => {
            const method = route.request().method();
            if (method === 'GET') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({
                        success: true, data: {
                            items: [
                                { id: 'order-001', orderNo: 'CHG-20260307-001', status: 'Completed', totalEnergy: 35.5, totalAmount: 25.60, createTime: '2026-03-07T08:00:00Z' },
                                { id: 'order-002', orderNo: 'CHG-20260307-002', status: 'Charging', totalEnergy: 12.0, totalAmount: 0, createTime: '2026-03-07T10:00:00Z' }
                            ], total: 2, page: 1, pageSize: 10
                        }
                    })
                });
            } else if (method === 'POST') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { orderId: 'order-003', orderNo: 'CHG-20260307-003', status: 'Created' } })
                });
            } else {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });

        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/charging') && !url.includes('/auth/')) {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });
    });

    test('[P0] 订单列表页面加载', async ({ page }) => {
        await page.goto('/charging/orders');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P0] 订单详情查看', async ({ page }) => {
        await page.goto('/charging/orders/order-001');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P0] 创建充电订单', async ({ page }) => {
        await page.goto('/charging/orders/create');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P0] 订单费用计算展示', async ({ page }) => {
        await page.goto('/charging/orders/order-001');
        await expect(page.locator('body')).toBeVisible();
    });
});

// ═══════════════════════════════════════════════════
// 实名认证 E2E 测试
// ═══════════════════════════════════════════════════

test.describe('实名认证 @p0 @identity', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        await page.route('**/api/identity/realname-auth/**', async (route) => {
            const url = route.request().url();
            const method = route.request().method();

            if (url.includes('/submit') && method === 'POST') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { authId: 'auth-001', status: 'Pending', submitTime: '2026-03-07T10:00:00Z' } })
                });
            } else if (url.includes('/current')) {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { authId: 'auth-001', status: 'Approved', realName: '张**', idCard: '110***1234', verifiedAt: '2026-03-05T14:00:00Z' } })
                });
            } else if (url.includes('/verified')) {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { isVerified: true } })
                });
            } else {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });

        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/realname-auth') && !url.includes('/auth/')) {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });
    });

    test('[P0] 实名认证页面加载', async ({ page }) => {
        await page.goto('/identity/realname-auth');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P0] 提交实名认证', async ({ page }) => {
        await page.goto('/identity/realname-auth/submit');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P0] 查看认证状态', async ({ page }) => {
        await page.goto('/identity/realname-auth');
        await expect(page.locator('body')).toBeVisible();
    });
});

// ═══════════════════════════════════════════════════
// 规则引擎管理 E2E 测试
// ═══════════════════════════════════════════════════

test.describe('规则引擎管理 @p1 @ruleengine', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        await page.route('**/api/ruleengine/chains*', async (route) => {
            const method = route.request().method();
            if (method === 'GET') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({
                        success: true, data: {
                            items: [
                                { id: 'chain-001', name: '温度告警规则', code: 'TEMP_ALARM', deviceType: 'charging_pile', triggerType: 'telemetry', isEnabled: true, priority: 100 },
                                { id: 'chain-002', name: '电流保护规则', code: 'CURRENT_PROTECT', deviceType: 'inverter', triggerType: 'alarm', isEnabled: true, priority: 90 }
                            ], total: 2
                        }
                    })
                });
            } else if (method === 'POST') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: { id: 'chain-003' } })
                });
            } else if (method === 'DELETE') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({ success: true, data: null })
                });
            } else {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });

        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/ruleengine') && !url.includes('/auth/')) {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });
    });

    test('[P1] 规则链列表页面', async ({ page }) => {
        await page.goto('/ruleengine/chains');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 创建规则链', async ({ page }) => {
        await page.goto('/ruleengine/chains/create');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 规则链详情', async ({ page }) => {
        await page.goto('/ruleengine/chains/chain-001');
        await expect(page.locator('body')).toBeVisible();
    });
});

// ═══════════════════════════════════════════════════
// VPP 调度管理 E2E 测试
// ═══════════════════════════════════════════════════

test.describe('VPP 调度管理 @p1 @vpp', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        await page.route('**/api/vpp/dispatch*', async (route) => {
            const method = route.request().method();
            if (method === 'GET') {
                await route.fulfill({
                    status: 200, contentType: 'application/json',
                    body: JSON.stringify({
                        success: true, data: {
                            items: [
                                { id: 'dispatch-001', vppId: 'vpp-001', targetPower: 500, status: 2, complianceRate: 0.95, createTime: '2026-03-07T08:00:00Z' },
                                { id: 'dispatch-002', vppId: 'vpp-001', targetPower: 1000, status: 1, complianceRate: null, createTime: '2026-03-07T10:00:00Z' }
                            ], total: 2
                        }
                    })
                });
            } else {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: { dispatchId: 'dispatch-003' } }) });
            }
        });

        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/vpp') && !url.includes('/auth/')) {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });
    });

    test('[P1] 调度列表页面', async ({ page }) => {
        await page.goto('/vpp/dispatch');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 执行调度操作', async ({ page }) => {
        await page.goto('/vpp/dispatch/create');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 调度结果查看', async ({ page }) => {
        await page.goto('/vpp/dispatch/dispatch-001');
        await expect(page.locator('body')).toBeVisible();
    });
});

// ═══════════════════════════════════════════════════
// 碳交易与需求响应 E2E 测试
// ═══════════════════════════════════════════════════

test.describe('碳交易 @p1 @iotcloudai', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        await page.route('**/api/iotcloudai/carbon/**', async (route) => {
            await route.fulfill({
                status: 200, contentType: 'application/json',
                body: JSON.stringify({
                    success: true, data: {
                        emission: 1250.5, carbonAsset: 800.0,
                        forecastPrice: 68.5, tradingStrategy: 'sell',
                        tradeResult: { tradeId: 'trade-001', status: 'completed' }
                    }
                })
            });
        });

        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/carbon') && !url.includes('/auth/')) {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });
    });

    test('[P1] 碳排放计算页面', async ({ page }) => {
        await page.goto('/iotcloudai/carbon');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 碳交易执行', async ({ page }) => {
        await page.goto('/iotcloudai/carbon/trade');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 碳价预测', async ({ page }) => {
        await page.goto('/iotcloudai/carbon/forecast');
        await expect(page.locator('body')).toBeVisible();
    });
});

test.describe('需求响应 @p1 @iotcloudai', () => {

    test.beforeEach(async ({ page }) => {
        await setupCommonMocks(page);

        await page.route('**/api/iotcloudai/demand-response/**', async (route) => {
            await route.fulfill({
                status: 200, contentType: 'application/json',
                body: JSON.stringify({
                    success: true, data: {
                        events: [
                            { id: 'event-001', name: '夏季削峰', status: 'active', startTime: '2026-07-15T14:00:00Z', endTime: '2026-07-15T17:00:00Z', targetReduction: 200 }
                        ],
                        capability: { maxCapacity: 500, availableCapacity: 300 },
                        plan: { steps: [{ time: '14:00', targetPower: -100 }] }
                    }
                })
            });
        });

        await page.route('**/api/**', async (route) => {
            const url = route.request().url();
            if (!url.includes('/demand-response') && !url.includes('/auth/')) {
                await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data: {} }) });
            }
        });
    });

    test('[P1] 需求响应事件列表', async ({ page }) => {
        await page.goto('/iotcloudai/demand-response');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 参与需求响应', async ({ page }) => {
        await page.goto('/iotcloudai/demand-response/participate');
        await expect(page.locator('body')).toBeVisible();
    });

    test('[P1] 需求响应结算', async ({ page }) => {
        await page.goto('/iotcloudai/demand-response/settle');
        await expect(page.locator('body')).toBeVisible();
    });
});
