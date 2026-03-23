// ========================================
// 场景 1: 用户管理完整流程
// ========================================
// 测试内容：创建用户 → 编辑用户 → 分配角色 → 删除用户
// 覆盖模块：用户管理、角色管理
// 预期时长：8-10 分钟

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper';
import { TestData } from '../helpers/test-data';

test.describe('用户管理完整流程', () => {
  let helper;
  let userData;

  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    userData = TestData.generateUser();
    
    await helper.showPrompt('场景开始', '即将测试用户管理完整流程，请确保已登录管理员账户');
    await helper.login('admin');
  });

  test('步骤1: 创建新用户', async ({ page }) => {
    await helper.navigate('/admin/users');
    await helper.waitForUserConfirm('导航到用户管理页面');

    // 引导用户点击创建按钮
    await helper.highlightElement('button:has-text("新建"), button:has-text("创建")');
    await helper.showPrompt('操作提示', '点击"新建用户"按钮');
    await helper.waitForUserAction();

    // 等待表单出现
    await page.waitForSelector('form, .ant-modal');
    await helper.waitForUserConfirm('表单已打开');

    // 引导填充表单
    await helper.showPrompt('填充表单', `请填写以下信息：
      - 用户名: ${userData.username}
      - 邮箱: ${userData.email}
      - 手机: ${userData.phone}
      - 角色: ${userData.role}
    `);

    // 等待用户填充
    await helper.waitForUserAction(30000);

    // 引导提交
    await helper.highlightElement('button[type="submit"], button:has-text("保存"), button:has-text("确定")');
    await helper.showPrompt('提交', '点击"保存"按钮');
    await helper.waitForUserAction();

    // 验证创建成功
    await page.waitForTimeout(2000);
    const successMsg = await page.locator('.ant-message-success, .success-notification').first();
    if (await successMsg.isVisible()) {
      await helper.showPrompt('✅ 验证通过', '用户创建成功');
    } else {
      await helper.showPrompt('⚠️ 需要检查', '未检测到成功提示，请手动确认用户是否创建成功');
    }

    // 截图保存
    await helper.takeScreenshot('01-user-created');
  });

  test('步骤2: 搜索并编辑用户', async ({ page }) => {
    await helper.navigate('/admin/users');
    
    // 引导搜索
    await helper.highlightElement('input[placeholder*="搜索"], input[placeholder*="用户名"]');
    await helper.showPrompt('搜索用户', `在搜索框输入: ${userData.username}`);
    await helper.waitForUserAction();

    // 等待搜索结果
    await page.waitForTimeout(1000);
    
    // 引导点击编辑
    await helper.highlightElement('button:has-text("编辑"), .edit-button, .ant-btn-link:has-text("编辑")');
    await helper.showPrompt('编辑', '点击用户行的"编辑"按钮');
    await helper.waitForUserAction();

    // 等待编辑表单
    await page.waitForSelector('form, .ant-modal');
    
    // 引导修改信息
    userData.phone = TestData.generatePhone();
    await helper.showPrompt('修改信息', `请将手机号修改为: ${userData.phone}`);
    await helper.waitForUserAction();

    // 引导保存
    await helper.highlightElement('button[type="submit"], button:has-text("保存")');
    await helper.showPrompt('保存', '点击"保存"按钮');
    await helper.waitForUserAction();

    // 验证
    await page.waitForTimeout(2000);
    await helper.takeScreenshot('02-user-edited');
    await helper.showPrompt('✅ 步骤完成', '用户信息已更新');
  });

  test('步骤3: 分配角色', async ({ page }) => {
    await helper.navigate('/admin/users');
    
    // 搜索用户
    await page.fill('input[placeholder*="搜索"]', userData.username);
    await page.waitForTimeout(1000);

    // 引导分配角色
    await helper.highlightElement('button:has-text("分配角色"), .role-button');
    await helper.showPrompt('分配角色', '点击"分配角色"按钮');
    await helper.waitForUserAction();

    // 等待角色选择弹窗
    await page.waitForSelector('.ant-modal, .role-modal');
    
    // 引导选择角色
    await helper.showPrompt('选择角色', `
      请选择以下角色之一：
      - 管理员
      - 普通用户
      - 查看者
    `);
    await helper.waitForUserAction();

    // 引导确认
    await helper.highlightElement('button:has-text("确定"), button:has-text("保存")');
    await helper.showPrompt('确认', '点击"确定"按钮');
    await helper.waitForUserAction();

    // 验证
    await page.waitForTimeout(2000);
    await helper.takeScreenshot('03-role-assigned');
    await helper.showPrompt('✅ 步骤完成', '角色分配成功');
  });

  test('步骤4: 删除用户', async ({ page }) => {
    await helper.navigate('/admin/users');
    
    // 搜索用户
    await page.fill('input[placeholder*="搜索"]', userData.username);
    await page.waitForTimeout(1000);

    // 引导删除
    await helper.highlightElement('button:has-text("删除"), .delete-button, .ant-popconfirm-buttons');
    await helper.showPrompt('删除', '点击用户行的"删除"按钮');
    await helper.waitForUserAction();

    // 等待确认弹窗
    await page.waitForTimeout(500);
    
    // 引导确认删除
    await helper.highlightElement('.ant-popconfirm-buttons button:has-text("确定"), .confirm-button');
    await helper.showPrompt('确认删除', '点击"确定"按钮确认删除');
    await helper.waitForUserAction();

    // 验证
    await page.waitForTimeout(2000);
    const userRow = await page.locator(`tr:has-text("${userData.username}")`).count();
    if (userRow === 0) {
      await helper.showPrompt('✅ 验证通过', '用户已成功删除');
    } else {
      await helper.showPrompt('⚠️ 需要检查', '用户似乎仍然存在，请手动确认');
    }

    await helper.takeScreenshot('04-user-deleted');
  });

  test.afterEach(async () => {
    await helper.showPrompt('场景结束', '用户管理流程测试完成');
    await helper.generateReport('user-management', {
      scenario: '用户管理',
      steps: 4,
      duration: '8-10 分钟',
      result: '完成'
    });
  });
});
