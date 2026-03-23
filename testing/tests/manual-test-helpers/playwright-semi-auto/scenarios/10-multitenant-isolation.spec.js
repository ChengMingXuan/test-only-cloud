// ========================================
// 场景脚本 10 - 多租户隔离验证
// ========================================
// 测试流程：租户A创建数据 → 切换租户B → 验证隔离 → 测试跨租户访问 → 权限验证

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let tenantAData;
let tenantBData;
let testDeviceDataA;
let testUserDataA;

test.describe('多租户隔离验证工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '🔐 多租户隔离验证场景开始',
      '本场景将引导您完成：\n1. 租户A创建测试数据\n2. 切换到租户B\n3. 验证数据隔离\n4. 测试跨租户访问（应失败）\n5. 验证租户级权限',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录为超级管理员');
  });

  test('步骤1：租户A创建测试数据', async () => {
    tenantAData = { name: '租户A', id: 'TENANT_A' };
    
    // 切换到租户A
    await helper.navigate('/tenant/switch');
    
    await helper.showPrompt(
      '🏢 切换到租户A',
      '请选择第一个测试租户作为"租户A"',
      0
    );
    await helper.highlightElement('.tenant-selector, select[name="tenantId"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    helper.logStep('已切换到租户A');
    await helper.takeScreenshot('switched-to-tenant-a');
    
    // 在租户A中创建设备
    testDeviceDataA = TestData.generateDevice();
    testDeviceDataA.name = `TenantA_Device_${Date.now()}`;
    
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '📦 创建租户A的设备',
      `请创建一个设备，记住设备名称：\n${testDeviceDataA.name}`,
      0
    );
    await helper.highlightElement('button:has-text("新建设备"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('点击新建设备后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .device-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写设备信息',
      `请填写：\n设备名称：${testDeviceDataA.name}\n设备编码：${testDeviceDataA.code}\n设备类型：${testDeviceDataA.type}`,
      0
    );
    
    await helper.highlightElement('input[name="name"], input[placeholder*="名称"]', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存设备', '请保存设备', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功');
    helper.logStep('租户A的设备已创建');
    await helper.takeScreenshot('tenant-a-device-created');
    
    // 在租户A中创建用户
    testUserDataA = TestData.generateUser();
    testUserDataA.username = `TenantA_User_${Date.now()}`;
    
    await helper.navigate('/user/list');
    
    await helper.showPrompt(
      '👤 创建租户A的用户',
      `请创建一个用户，记住用户名：\n${testUserDataA.username}`,
      0
    );
    await helper.highlightElement('button:has-text("新建用户"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('点击新建用户后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .user-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写用户信息',
      `请填写：\n用户名：${testUserDataA.username}\n邮箱：${testUserDataA.email}\n手机：${testUserDataA.phone}`,
      0
    );
    
    await helper.highlightElement('input[name="username"], input[placeholder*="用户名"]', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存用户', '请保存用户', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功');
    helper.logStep('租户A的用户已创建');
    await helper.takeScreenshot('tenant-a-user-created');
  });

  test('步骤2：切换到租户B', async () => {
    tenantBData = { name: '租户B', id: 'TENANT_B' };
    
    await helper.navigate('/tenant/switch');
    
    await helper.showPrompt(
      '🔄 切换到租户B',
      '请选择另一个测试租户作为"租户B"',
      0
    );
    await helper.highlightElement('.tenant-selector, select[name="tenantId"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    helper.logStep('已切换到租户B');
    await helper.takeScreenshot('switched-to-tenant-b');
    
    // 确认租户切换成功
    await helper.showPrompt(
      '✅ 确认切换',
      '请确认页面右上角或侧边栏显示的当前租户名称已变更为租户B',
      0
    );
    await helper.highlightElement('.tenant-name, .current-tenant', 3000);
    await helper.waitForUserConfirm('确认切换成功后按回车');
    await helper.closePrompt();
  });

  test('步骤3：验证数据隔离 - 设备', async () => {
    await helper.navigate('/device/list');
    helper.logStep('已进入设备列表页（租户B）');
    
    await helper.showPrompt(
      '🔍 搜索租户A的设备',
      `请在搜索框中输入租户A的设备名称：\n${testDeviceDataA ? testDeviceDataA.name : 'TenantA_Device_xxx'}\n
预期结果：应该搜索不到（数据隔离）`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证隔离结果',
      '请确认：\n• 搜索结果为空\n• 或显示"暂无数据"\n• 租户A的设备完全不可见\n
这证明设备数据在租户间是隔离的',
      0
    );
    
    await helper.waitForUserConfirm('确认数据隔离正常后按回车');
    await helper.closePrompt();
    
    helper.logStep('设备数据隔离验证通过');
    await helper.takeScreenshot('device-isolation-verified');
  });

  test('步骤4：验证数据隔离 - 用户', async () => {
    await helper.navigate('/user/list');
    helper.logStep('已进入用户列表页（租户B）');
    
    await helper.showPrompt(
      '🔍 搜索租户A的用户',
      `请在搜索框中输入租户A的用户名：\n${testUserDataA ? testUserDataA.username : 'TenantA_User_xxx'}\n
预期结果：应该搜索不到（数据隔离）`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证隔离结果',
      '请确认：\n• 搜索结果为空\n• 租户A的用户完全不可见\n• 租户B只能看到自己的用户\n
这证明用户数据在租户间是隔离的',
      0
    );
    
    await helper.waitForUserConfirm('确认数据隔离正常后按回车');
    await helper.closePrompt();
    
    helper.logStep('用户数据隔离验证通过');
    await helper.takeScreenshot('user-isolation-verified');
  });

  test('步骤5：测试跨租户访问（应失败）', async () => {
    await helper.showPrompt(
      '🚫 跨租户访问测试',
      '我们将尝试通过 URL 直接访问租户A的数据\n预期：应该被拒绝或返回 404',
      3000
    );
    
    // 假设租户A的设备ID
    const fakeDeviceId = '00000000-0000-0000-0000-000000000001';
    
    await helper.showPrompt(
      '🔗 尝试访问租户A的设备详情',
      `我们将导航到一个假定的租户A设备详情页\nURL: /device/detail/${fakeDeviceId}`,
      0
    );
    
    await helper.waitForUserConfirm('按回车继续');
    await helper.closePrompt();
    
    await helper.navigate(`/device/detail/${fakeDeviceId}`);
    
    await helper.page.waitForTimeout(2000);
    
    await helper.showPrompt(
      '🔒 验证访问控制',
      '请确认页面显示以下之一：\n• "权限不足"错误\n• "数据不存在"（404）\n• "无权访问此租户数据"\n• 自动跳转回列表页\n
这证明跨租户访问被正确拒绝',
      0
    );
    
    await helper.highlightElement('.error-message, .ant-result, .permission-denied', 3000);
    await helper.waitForUserConfirm('确认访问被拒绝后按回车');
    await helper.closePrompt();
    
    helper.logStep('跨租户访问已被正确拒绝');
    await helper.takeScreenshot('cross-tenant-access-denied');
  });

  test('步骤6：验证租户级权限', async () => {
    await helper.showPrompt(
      '🔐 租户级权限验证',
      '我们将验证租户B的用户无法执行以下操作：\n• 查看租户A的数据\n• 修改租户A的配置\n• 切换到租户A（普通用户）',
      0
    );
    
    await helper.waitForUserConfirm('按回车继续验证');
    await helper.closePrompt();
    
    // 验证租户切换权限
    await helper.navigate('/tenant/switch');
    
    await helper.showPrompt(
      '👥 验证租户切换权限',
      '请确认：\n• 普通用户只能看到自己所属的租户\n• 无法切换到其他租户\n• 或者切换选项被禁用\n
（超级管理员除外）',
      0
    );
    
    await helper.highlightElement('.tenant-selector', 3000);
    await helper.waitForUserConfirm('确认权限控制正确后按回车');
    await helper.closePrompt();
    
    helper.logStep('租户级权限验证通过');
    await helper.takeScreenshot('tenant-permission-verified');
    
    // 最终总结
    await helper.showPrompt(
      '🎉 多租户隔离验证完成',
      '验证总结：\n✅ 租户A和租户B的数据完全隔离\n✅ 设备、用户等业务数据无法跨租户访问\n✅ URL直接访问被正确拒绝\n✅ 租户级权限控制正常\n
多租户隔离功能运行正常！',
      5000
    );
    
    await helper.closePrompt();
  });

  test.afterEach(async () => {
    await helper.generateReport('multitenant-isolation', {
      scenario: '多租户隔离验证',
      tenantAData,
      tenantBData,
      testDeviceDataA,
      testUserDataA,
      timestamp: new Date().toISOString()
    });
  });
});
