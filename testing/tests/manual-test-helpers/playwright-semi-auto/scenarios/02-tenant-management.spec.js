// ========================================
// 场景脚本 02 - 租户管理
// ========================================
// 测试流程：创建租户 → 配置租户 → 数据隔离验证 → 删除租户

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testTenantData;

test.describe('租户管理工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    // 显示场景介绍
    await helper.showPrompt(
      '🏢 租户管理场景开始',
      '本场景将引导您完成：\n1. 创建新租户\n2. 配置租户信息\n3. 验证多租户数据隔离\n4. 删除测试租户',
      3000
    );
    
    // 登录为超级管理员
    await helper.login('admin');
    helper.logStep('已登录为超级管理员');
  });

  test('步骤1：创建新租户', async () => {
    // 生成测试数据
    testTenantData = TestData.generateTenant();
    
    // 导航到租户管理页面
    await helper.navigate('/tenant/list');
    helper.logStep('已进入租户管理页面');
    
    // 高亮并引导点击"新建租户"按钮
    await helper.showPrompt(
      '📝 准备创建租户',
      '请点击"新建租户"按钮',
      0
    );
    await helper.highlightElement('button:has-text("新建租户")', 3000);
    await helper.waitForUserConfirm('请点击新建租户按钮，然后按回车继续');
    await helper.closePrompt();
    
    // 等待表单弹窗出现
    await helper.page.waitForSelector('.ant-modal', { timeout: 5000 });
    helper.logStep('租户创建表单已打开');
    
    // 显示要填写的测试数据
    await helper.showPrompt(
      '✍️ 填写租户信息',
      `请按以下信息填写表单：\n
租户名称：${testTenantData.name}
租户编码：${testTenantData.code}
联系人：${testTenantData.contact}
联系电话：${testTenantData.phone}
邮箱：${testTenantData.email}
地址：${testTenantData.address}
备注：${testTenantData.description}`,
      0
    );
    
    // 高亮表单字段
    await helper.highlightElement('input[placeholder*="租户名称"]', 2000);
    await helper.page.waitForTimeout(500);
    await helper.highlightElement('input[placeholder*="租户编码"]', 2000);
    await helper.page.waitForTimeout(500);
    await helper.highlightElement('input[placeholder*="联系人"]', 2000);
    
    // 等待用户填写表单
    await helper.waitForUserAction(45000);
    await helper.closePrompt();
    
    // 高亮并引导点击保存按钮
    await helper.showPrompt('💾 保存租户', '请点击"确定"按钮保存租户', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('请点击确定按钮，然后按回车继续');
    await helper.closePrompt();
    
    // 验证成功消息
    await helper.assertVisible('.ant-message-success', '应显示创建成功的提示');
    helper.logStep('租户创建成功');
    
    // 截图保存
    await helper.takeScreenshot('tenant-created');
  });

  test('步骤2：配置租户信息', async () => {
    await helper.navigate('/tenant/list');
    
    // 搜索刚创建的租户
    await helper.showPrompt(
      '🔍 搜索租户',
      `请在搜索框中输入：${testTenantData.name || '刚创建的租户名称'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    // 高亮并引导点击"配置"按钮
    await helper.showPrompt('⚙️ 配置租户', '请点击租户行的"配置"按钮', 0);
    await helper.highlightElement('button:has-text("配置")', 3000);
    await helper.waitForUserConfirm('请点击配置按钮，然后按回车继续');
    await helper.closePrompt();
    
    // 等待配置页面加载
    await helper.page.waitForLoadState('networkidle');
    helper.logStep('已进入租户配置页面');
    
    // 显示配置项说明
    await helper.showPrompt(
      '🎛️ 配置项说明',
      `请根据需要调整以下配置：\n
1. 存储配额：设置租户的存储空间限制
2. 用户数限制：设置最大用户数
3. 设备数限制：设置最大设备数
4. 功能模块：勾选该租户可使用的功能模块
5. API 调用限制：设置 API 调用频率限制`,
      0
    );
    
    // 高亮配置区域
    await helper.highlightElement('.config-panel', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    // 提示保存配置
    await helper.showPrompt('💾 保存配置', '请点击"保存"按钮', 0);
    await helper.highlightElement('button:has-text("保存")', 3000);
    await helper.waitForUserConfirm('请保存配置后按回车继续');
    await helper.closePrompt();
    
    // 验证保存成功
    await helper.assertVisible('.ant-message-success', '应显示保存成功的提示');
    helper.logStep('租户配置已保存');
    
    await helper.takeScreenshot('tenant-configured');
  });

  test('步骤3：验证多租户数据隔离', async () => {
    // 在租户 A 创建测试数据
    await helper.showPrompt(
      '🔐 数据隔离测试 - 阶段 1',
      '我们将在租户 A 创建一些测试数据，然后切换到租户 B 验证数据隔离',
      3000
    );
    
    // 切换到租户 A
    await helper.navigate('/tenant/switch');
    await helper.showPrompt('🏢 切换到租户 A', '请选择并切换到第一个测试租户', 0);
    await helper.highlightElement('.tenant-selector', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    helper.logStep('已切换到租户 A');
    
    // 创建测试设备
    await helper.navigate('/device/list');
    await helper.showPrompt(
      '📋 创建测试设备',
      '请在租户 A 中创建一个测试设备，记住设备名称',
      0
    );
    await helper.highlightElement('button:has-text("新建设备")', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    helper.logStep('在租户 A 创建了测试设备');
    await helper.takeScreenshot('tenant-a-data');
    
    // 切换到租户 B
    await helper.navigate('/tenant/switch');
    await helper.showPrompt(
      '🏢 切换到租户 B',
      '现在请切换到另一个测试租户（租户 B）',
      0
    );
    await helper.highlightElement('.tenant-selector', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    helper.logStep('已切换到租户 B');
    
    // 验证看不到租户 A 的设备
    await helper.navigate('/device/list');
    await helper.showPrompt(
      '🔍 验证数据隔离',
      '请确认：在租户 B 的设备列表中看不到刚才在租户 A 创建的设备\n这证明多租户数据隔离正常工作',
      0
    );
    await helper.waitForUserConfirm('确认数据隔离无问题后按回车继续');
    await helper.closePrompt();
    
    helper.logStep('已验证租户数据隔离');
    await helper.takeScreenshot('tenant-b-isolation');
  });

  test('步骤4：删除测试租户', async () => {
    await helper.navigate('/tenant/list');
    
    // 搜索要删除的租户
    await helper.showPrompt(
      '🔍 搜索测试租户',
      `请搜索并找到测试租户：${testTenantData ? testTenantData.name : '测试租户'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    // 高亮删除按钮
    await helper.showPrompt('⚠️ 删除租户', '请点击"删除"按钮', 0);
    await helper.highlightElement('button:has-text("删除")', 3000);
    await helper.waitForUserConfirm('请点击删除按钮，然后按回车继续');
    await helper.closePrompt();
    
    // 等待确认弹窗
    await helper.page.waitForSelector('.ant-popconfirm', { timeout: 5000 });
    
    // 引导确认删除
    await helper.showPrompt(
      '❗ 确认删除',
      '请在确认弹窗中点击"确定"以永久删除此租户',
      0
    );
    await helper.highlightElement('.ant-popconfirm button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认删除后按回车继续');
    await helper.closePrompt();
    
    // 验证删除成功
    await helper.assertVisible('.ant-message-success', '应显示删除成功的提示');
    helper.logStep('租户已删除');
    
    await helper.takeScreenshot('tenant-deleted');
  });

  test.afterEach(async () => {
    // 生成测试报告
    await helper.generateReport('tenant-management', {
      scenario: '租户管理',
      testData: testTenantData,
      timestamp: new Date().toISOString()
    });
  });
});
