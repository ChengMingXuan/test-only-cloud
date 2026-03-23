// ========================================
// 场景脚本 06 - 工单管理
// ========================================
// 测试流程：创建工单 → 分配工程师 → 更新状态 → 添加备注 → 关闭工单

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testWorkOrderData;

test.describe('工单管理工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '📋 工单管理场景开始',
      '本场景将引导您完成：\n1. 创建工单\n2. 分配工程师\n3. 更新工单状态\n4. 添加处理备注\n5. 关闭工单',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：创建工单', async () => {
    testWorkOrderData = TestData.generateWorkOrder();
    
    await helper.navigate('/workorder/list');
    helper.logStep('已进入工单管理页面');
    
    await helper.showPrompt('📝 创建工单', '请点击"新建工单"按钮', 0);
    await helper.highlightElement('button:has-text("新建工单"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('请点击新建工单按钮，然后按回车继续');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .workorder-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写工单信息',
      `请填写：\n
工单标题：${testWorkOrderData.title}
工单类型：${testWorkOrderData.type}
优先级：${testWorkOrderData.priority}
关联设备：${testWorkOrderData.deviceId}
问题描述：${testWorkOrderData.description}
期望完成时间：${testWorkOrderData.expectedTime}`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="标题"], input[name="title"]', 2000);
    await helper.waitForUserAction(50000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存工单', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, button[type="submit"]', 3000);
    await helper.waitForUserConfirm('保存工单后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功提示');
    helper.logStep('工单创建成功');
    
    await helper.takeScreenshot('workorder-created');
  });

  test('步骤2：分配工程师', async () => {
    await helper.navigate('/workorder/list');
    
    await helper.showPrompt(
      '🔍 搜索工单',
      `请搜索：${testWorkOrderData ? testWorkOrderData.orderNo : '刚创建的工单'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('👷 分配工程师', '请点击"分配"或"指派"按钮', 0);
    await helper.highlightElement('button:has-text("分配"), button:has-text("指派")', 3000);
    await helper.waitForUserConfirm('点击分配按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .assign-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '👤 选择工程师',
      `请从下拉列表选择工程师（可以选择：${testWorkOrderData ? testWorkOrderData.assignee : '工程师'}）`,
      0
    );
    
    await helper.highlightElement('.ant-select, select[name="assignee"]', 3000);
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    await helper.showPrompt('✅ 确认分配', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认分配后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示分配成功');
    helper.logStep('工单已分配给工程师');
    
    await helper.takeScreenshot('workorder-assigned');
  });

  test('步骤3：更新工单状态', async () => {
    await helper.navigate('/workorder/list');
    
    await helper.showPrompt(
      '🔍 查找工单',
      `请搜索：${testWorkOrderData ? testWorkOrderData.orderNo : '测试工单'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('🔄 更新状态', '请点击"更新状态"或状态下拉框', 0);
    await helper.highlightElement('button:has-text("更新状态"), .status-select, button:has-text("状态")', 3000);
    await helper.waitForUserConfirm('点击更新状态后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .status-form, .ant-select-dropdown', { timeout: 5000 });
    
    await helper.showPrompt(
      '📝 选择新状态',
      '请选择新的工单状态：\n• 处理中\n• 待验证\n• 已完成\n• 已取消',
      0
    );
    
    await helper.highlightElement('.ant-select-item, .status-option', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    // 如果有确认按钮
    const hasConfirmButton = await helper.page.locator('.ant-modal-footer button.ant-btn-primary').isVisible().catch(() => false);
    if (hasConfirmButton) {
      await helper.showPrompt('✅ 确认更新', '请点击"确定"按钮', 0);
      await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
      await helper.waitForUserConfirm('确认更新后按回车');
      await helper.closePrompt();
    }
    
    await helper.assertVisible('.ant-message-success', '应显示更新成功');
    helper.logStep('工单状态已更新');
    
    await helper.takeScreenshot('workorder-status-updated');
  });

  test('步骤4：添加处理备注', async () => {
    await helper.navigate('/workorder/list');
    
    await helper.showPrompt(
      '🔍 查找工单',
      `请搜索：${testWorkOrderData ? testWorkOrderData.orderNo : '测试工单'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('📝 添加备注', '请点击"添加备注"或"详情"按钮', 0);
    await helper.highlightElement('button:has-text("备注"), button:has-text("详情"), a:has-text("详情")', 3000);
    await helper.waitForUserConfirm('点击后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForTimeout(2000);
    
    await helper.showPrompt(
      '✍️ 输入备注',
      '请在备注框中输入处理记录，例如：\n"已现场检查设备，发现电源模块异常，已更换新模块，设备恢复正常运行"',
      0
    );
    
    await helper.highlightElement('textarea[placeholder*="备注"], textarea[name="comment"], .comment-input', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存备注', '请点击"提交"或"保存"按钮', 0);
    await helper.highlightElement('button:has-text("提交"), button:has-text("保存"), button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存备注后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示添加成功');
    helper.logStep('工单备注已添加');
    
    await helper.takeScreenshot('workorder-comment-added');
  });

  test('步骤5：关闭工单', async () => {
    await helper.navigate('/workorder/list');
    
    await helper.showPrompt(
      '🔍 查找工单',
      `请搜索：${testWorkOrderData ? testWorkOrderData.orderNo : '测试工单'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('✅ 关闭工单', '请点击"关闭"或"完成"按钮', 0);
    await helper.highlightElement('button:has-text("关闭"), button:has-text("完成")', 3000);
    await helper.waitForUserConfirm('点击关闭按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .ant-popconfirm', { timeout: 5000 });
    
    await helper.showPrompt(
      '📝 确认关闭',
      '请确认工单已完成处理，点击"确定"关闭工单',
      0
    );
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, .ant-popconfirm button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认关闭后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示关闭成功');
    helper.logStep('工单已关闭');
    
    await helper.takeScreenshot('workorder-closed');
  });

  test.afterEach(async () => {
    await helper.generateReport('workorder-workflow', {
      scenario: '工单管理',
      workOrderData: testWorkOrderData,
      timestamp: new Date().toISOString()
    });
  });
});
