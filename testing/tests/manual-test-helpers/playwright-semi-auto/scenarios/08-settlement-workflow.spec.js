// ========================================
// 场景脚本 08 - 结算工作流
// ========================================
// 测试流程：生成账单 → 审核费用 → 批准结算 → 导出报表 → 归档

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testSettlementData;

test.describe('结算工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '💰 结算工作流场景开始',
      '本场景将引导您完成：\n1. 生成账单\n2. 审核费用明细\n3. 批准结算\n4. 导出财务报表\n5. 归档记录',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：生成账单', async () => {
    testSettlementData = TestData.generateSettlement();
    
    await helper.navigate('/settlement/billing');
    helper.logStep('已进入结算管理页面');
    
    await helper.showPrompt('📝 生成账单', '请点击"生成账单"按钮', 0);
    await helper.highlightElement('button:has-text("生成账单"), button:has-text("生成")', 3000);
    await helper.waitForUserConfirm('请点击生成账单按钮，然后按回车继续');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .billing-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '📅 选择结算周期',
      `请选择结算周期：\n
• 结算周期：${testSettlementData.period}（年-月）
• 租户：选择要结算的租户
• 计费类型：电费/服务费/全部
• 结算方式：预付/后付`,
      0
    );
    
    await helper.highlightElement('.date-picker, input[placeholder*="周期"]', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('🔄 开始生成', '请点击"开始生成"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, button:has-text("生成")', 3000);
    await helper.waitForUserConfirm('开始生成后按回车');
    await helper.closePrompt();
    
    // 等待生成完成
    await helper.showPrompt(
      '⏳ 正在生成账单',
      '系统正在计算费用，请稍候...\n这可能需要几秒到几分钟',
      0
    );
    
    await helper.page.waitForTimeout(5000);
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示生成成功提示');
    helper.logStep('账单生成成功');
    
    await helper.takeScreenshot('billing-generated');
  });

  test('步骤2：审核费用明细', async () => {
    await helper.navigate('/settlement/billing');
    
    await helper.showPrompt(
      '🔍 查找账单',
      `请搜索刚生成的账单\n周期：${testSettlementData ? testSettlementData.period : '当前月份'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('📋 查看详情', '请点击账单的"详情"按钮', 0);
    await helper.highlightElement('button:has-text("详情"), a:has-text("详情")', 3000);
    await helper.waitForUserConfirm('查看详情后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForLoadState('networkidle');
    helper.logStep('已进入账单详情页');
    
    await helper.showPrompt(
      '💳 审核费用明细',
      '请仔细核对以下信息：\n
• 基本信息：租户名称、结算周期、账单号
• 电量统计：总用电量、峰谷平分布
• 费用计算：电费、服务费、优惠、税费
• 总金额：应收金额
• 附件：用电记录、计费规则',
      0
    );
    
    await helper.highlightElement('.billing-detail, .fee-breakdown', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    // 查看费用明细表
    await helper.showPrompt(
      '📊 查看明细表',
      '请切换到"费用明细"标签，查看详细计费项',
      0
    );
    
    await helper.highlightElement('.ant-tabs-tab:has-text("明细"), button:has-text("明细")', 3000);
    await helper.waitForUserConfirm('查看明细后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForTimeout(2000);
    
    helper.logStep('费用明细已审核');
    await helper.takeScreenshot('billing-reviewed');
  });

  test('步骤3：批准结算', async () => {
    await helper.navigate('/settlement/billing');
    
    await helper.showPrompt(
      '🔍 查找待批准账单',
      '请筛选状态为"待审核"或"待批准"的账单',
      0
    );
    await helper.highlightElement('.status-filter, select[name="status"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('✅ 批准结算', '请点击"批准"或"审核通过"按钮', 0);
    await helper.highlightElement('button:has-text("批准"), button:has-text("审核通过")', 3000);
    await helper.waitForUserConfirm('点击批准按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .approve-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '📝 填写审批意见',
      '请填写：\n
• 审批意见：例如"账单核对无误，同意结算"
• 审批人：自动填充当前用户
• 审批时间：自动填充',
      0
    );
    
    await helper.highlightElement('textarea[placeholder*="意见"], textarea[name="comment"]', 3000);
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    await helper.showPrompt('✅ 确认批准', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认批准后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示批准成功');
    helper.logStep('结算已批准');
    
    await helper.takeScreenshot('settlement-approved');
  });

  test('步骤4：导出财务报表', async () => {
    await helper.navigate('/settlement/report');
    helper.logStep('已进入财务报表页面');
    
    await helper.showPrompt(
      '📊 生成报表',
      '请配置报表参数并导出',
      0
    );
    
    await helper.highlightElement('button:has-text("导出报表"), button:has-text("导出")', 3000);
    await helper.waitForUserConfirm('点击导出按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .export-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '⚙️ 配置导出选项',
      `请配置：\n
• 报表类型：汇总表/明细表/对账单
• 时间范围：选择报表周期
• 数据维度：按租户/按站点/按设备
• 导出格式：Excel/PDF/CSV
• 包含内容：勾选需要导出的数据项`,
      0
    );
    
    await helper.highlightElement('.export-options, .report-config', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 开始导出', '请点击"确定"开始导出', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('开始导出后按回车');
    await helper.closePrompt();
    
    // 等待导出完成
    await helper.page.waitForTimeout(3000);
    
    await helper.showPrompt(
      '📥 下载报表',
      '报表已生成，请点击下载链接保存到本地',
      0
    );
    
    await helper.highlightElement('button:has-text("下载"), a:has-text("下载")', 3000);
    await helper.waitForUserConfirm('下载完成后按回车');
    await helper.closePrompt();
    
    helper.logStep('财务报表已导出');
    await helper.takeScreenshot('report-exported');
  });

  test('步骤5：归档记录', async () => {
    await helper.navigate('/settlement/archive');
    helper.logStep('已进入归档管理页面');
    
    await helper.showPrompt(
      '🗂️ 归档结算记录',
      '请选择需要归档的已完成结算记录',
      0
    );
    
    await helper.highlightElement('.settlement-list, table', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    await helper.showPrompt('📦 批量归档', '请勾选记录，然后点击"归档"按钮', 0);
    await helper.highlightElement('button:has-text("归档"), button:has-text("批量归档")', 3000);
    await helper.waitForUserConfirm('点击归档按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .ant-popconfirm', { timeout: 5000 });
    
    await helper.showPrompt(
      '⚠️ 确认归档',
      '归档后记录将移至归档库，不可编辑\n请在确认弹窗中点击"确定"',
      0
    );
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, .ant-popconfirm button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认归档后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示归档成功');
    helper.logStep('结算记录已归档');
    
    await helper.takeScreenshot('records-archived');
    
    // 验证归档记录
    await helper.showPrompt(
      '🔍 查看归档记录',
      '请切换到"已归档"标签页，验证记录已归档',
      0
    );
    
    await helper.highlightElement('.ant-tabs-tab:has-text("已归档"), button:has-text("归档")', 3000);
    await helper.waitForUserConfirm('验证完成后按回车');
    await helper.closePrompt();
    
    helper.logStep('归档记录已验证');
    await helper.takeScreenshot('archived-verified');
  });

  test.afterEach(async () => {
    await helper.generateReport('settlement-workflow', {
      scenario: '结算工作流',
      settlementData: testSettlementData,
      timestamp: new Date().toISOString()
    });
  });
});
