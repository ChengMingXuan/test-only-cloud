// ========================================
// 场景脚本 03 - 权限管理
// ========================================
// 测试流程：创建角色 → 分配权限 → 测试用户访问 → 撤销权限

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testRoleData;
let testUserData;

test.describe('权限管理工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '🔐 权限管理场景开始',
      '本场景将引导您完成：\n1. 创建自定义角色\n2. 为角色分配权限\n3. 创建测试用户并分配角色\n4. 验证权限生效\n5. 撤销权限',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录为超级管理员');
  });

  test('步骤1：创建自定义角色', async () => {
    // 生成角色数据
    testRoleData = {
      name: `测试角色_${Date.now()}`,
      code: `ROLE${Math.floor(Math.random() * 1000)}`,
      description: '这是一个用于测试的自定义角色'
    };
    
    await helper.navigate('/permission/role');
    helper.logStep('已进入角色管理页面');
    
    // 引导创建角色
    await helper.showPrompt('📝 创建角色', '请点击"新建角色"按钮', 0);
    await helper.highlightElement('button:has-text("新建角色")', 3000);
    await helper.waitForUserConfirm('请点击新建角色按钮，然后按回车继续');
    await helper.closePrompt();
    
    // 等待表单
    await helper.page.waitForSelector('.ant-modal', { timeout: 5000 });
    
    // 显示填写信息
    await helper.showPrompt(
      '✍️ 填写角色信息',
      `请填写以下信息：\n
角色名称：${testRoleData.name}
角色代码：${testRoleData.code}
描述：${testRoleData.description}`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="角色名称"]', 2000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    // 保存角色
    await helper.showPrompt('💾 保存角色', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('请保存角色后按回车继续');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功提示');
    helper.logStep('角色创建成功');
    
    await helper.takeScreenshot('role-created');
  });

  test('步骤2：为角色分配权限', async () => {
    await helper.navigate('/permission/role');
    
    // 搜索刚创建的角色
    await helper.showPrompt(
      '🔍 搜索角色',
      `请搜索：${testRoleData ? testRoleData.name : '刚创建的角色'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    // 引导分配权限
    await helper.showPrompt('🎯 分配权限', '请点击"分配权限"按钮', 0);
    await helper.highlightElement('button:has-text("分配权限"), button:has-text("权限配置")', 3000);
    await helper.waitForUserConfirm('请点击分配权限按钮，然后按回车继续');
    await helper.closePrompt();
    
    // 等待权限树加载
    await helper.page.waitForSelector('.ant-tree, .permission-tree', { timeout: 5000 });
    helper.logStep('权限树已加载');
    
    // 显示权限分配说明
    await helper.showPrompt(
      '📋 权限分配说明',
      `请按照测试需求勾选权限：\n
建议勾选：
• 用户管理 → 查看用户
• 设备管理 → 查看设备、编辑设备
• 工单管理 → 查看工单、创建工单

不要勾选：
• 用户管理 → 删除用户（我们稍后会验证此权限被拒绝）`,
      0
    );
    
    await helper.highlightElement('.ant-tree, .permission-tree', 3000);
    await helper.waitForUserAction(45000);
    await helper.closePrompt();
    
    // 保存权限配置
    await helper.showPrompt('💾 保存权限', '请点击"确定"或"保存"按钮', 0);
    await helper.highlightElement('button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存权限后按回车继续');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示保存成功提示');
    helper.logStep('权限已分配');
    
    await helper.takeScreenshot('permissions-assigned');
  });

  test('步骤3：创建测试用户并分配角色', async () => {
    // 生成测试用户
    testUserData = TestData.generateUser();
    
    await helper.navigate('/user/list');
    
    // 创建用户
    await helper.showPrompt('👤 创建测试用户', '请点击"新建用户"按钮', 0);
    await helper.highlightElement('button:has-text("新建用户"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('请点击新建用户按钮，然后按回车继续');
    await helper.closePrompt();
    
    // 填写用户信息
    await helper.page.waitForSelector('.ant-modal, .user-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写用户信息',
      `请填写：\n
用户名：${testUserData.username}
邮箱：${testUserData.email}
手机：${testUserData.phone}
密码：${testUserData.password}
角色：选择刚创建的测试角色`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="用户名"]', 2000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    // 特别强调角色选择
    await helper.showPrompt(
      '🎭 重要：选择角色',
      `请在角色下拉框中选择：${testRoleData ? testRoleData.name : '刚创建的测试角色'}`,
      0
    );
    await helper.highlightElement('.ant-select, select[name="roleId"]', 3000);
    await helper.waitForUserConfirm('已选择角色后按回车继续');
    await helper.closePrompt();
    
    // 保存用户
    await helper.showPrompt('💾 保存用户', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, button[type="submit"]', 3000);
    await helper.waitForUserConfirm('保存用户后按回车继续');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功提示');
    helper.logStep('测试用户已创建并分配角色');
    
    await helper.takeScreenshot('test-user-created');
  });

  test('步骤4：验证权限生效 - 正向测试', async () => {
    // 登出当前管理员
    await helper.showPrompt(
      '🚪 退出登录',
      '请先退出当前管理员账号，我们将用新创建的测试用户重新登录',
      0
    );
    await helper.highlightElement('.user-avatar, .logout-btn, button:has-text("退出")', 3000);
    await helper.waitForUserConfirm('退出登录后按回车继续');
    await helper.closePrompt();
    
    // 等待跳转到登录页
    await helper.page.waitForURL('**/login', { timeout: 10000 });
    helper.logStep('已退出管理员账号');
    
    // 用测试用户登录
    await helper.showPrompt(
      '🔑 测试用户登录',
      `请使用以下账号登录：\n
用户名：${testUserData ? testUserData.username : '测试用户'}
密码：${testUserData ? testUserData.password : 'Test123!@#'}`,
      0
    );
    
    await helper.highlightElement('input[name="username"], input[placeholder*="用户名"]', 2000);
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    helper.logStep('已用测试用户登录');
    await helper.takeScreenshot('logged-in-as-test-user');
    
    // 测试有权限的操作：查看设备
    await helper.navigate('/device/list');
    await helper.showPrompt(
      '✅ 权限验证 - 可访问',
      '如果能看到设备列表页面，说明"查看设备"权限生效',
      0
    );
    await helper.waitForUserConfirm('确认能看到设备列表后按回车继续');
    await helper.closePrompt();
    
    await helper.assertVisible('.device-list, .ant-table', '应能看到设备列表');
    helper.logStep('已验证"查看设备"权限生效');
    
    await helper.takeScreenshot('permission-allowed');
  });

  test('步骤5：验证权限生效 - 反向测试', async () => {
    // 假设已用测试用户登录
    await helper.navigate('/user/list');
    
    // 尝试删除用户（应该被拒绝）
    await helper.showPrompt(
      '🚫 权限验证 - 应被拒绝',
      '我们将验证"删除用户"权限未分配。\n请尝试点击某个用户的"删除"按钮（如果有的话）',
      0
    );
    
    await helper.highlightElement('button:has-text("删除")', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    // 预期会看到权限不足的提示
    await helper.showPrompt(
      '🔒 预期结果',
      '应该显示"权限不足"或按钮不可用/不可见',
      0
    );
    await helper.waitForUserConfirm('确认权限被正确拒绝后按回车继续');
    await helper.closePrompt();
    
    helper.logStep('已验证权限拒绝正常工作');
    await helper.takeScreenshot('permission-denied');
  });

  test('步骤6：撤销权限', async () => {
    // 重新登录为管理员
    await helper.showPrompt(
      '🔄 切换回管理员',
      '请退出测试用户，重新登录为管理员',
      0
    );
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    await helper.login('admin');
    helper.logStep('已重新登录为管理员');
    
    // 进入角色管理
    await helper.navigate('/permission/role');
    
    // 搜索测试角色
    await helper.showPrompt(
      '🔍 查找测试角色',
      `请搜索：${testRoleData ? testRoleData.name : '测试角色'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    // 撤销部分权限
    await helper.showPrompt('✂️ 撤销权限', '请点击"分配权限"重新配置', 0);
    await helper.highlightElement('button:has-text("分配权限"), button:has-text("权限配置")', 3000);
    await helper.waitForUserConfirm('请点击分配权限按钮，然后按回车继续');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-tree, .permission-tree', { timeout: 5000 });
    
    // 引导取消部分权限
    await helper.showPrompt(
      '🔧 修改权限',
      '请取消勾选"设备管理 → 编辑设备"权限',
      0
    );
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    // 保存
    await helper.showPrompt('💾 保存修改', '请保存权限配置', 0);
    await helper.highlightElement('button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车继续');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示保存成功提示');
    helper.logStep('权限已撤销');
    
    await helper.takeScreenshot('permissions-revoked');
  });

  test.afterEach(async () => {
    await helper.generateReport('permission-management', {
      scenario: '权限管理',
      roleData: testRoleData,
      userData: testUserData,
      timestamp: new Date().toISOString()
    });
  });
});
