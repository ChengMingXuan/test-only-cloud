// ========================================
// 场景脚本 04 - 充电工作流
// ========================================
// 测试流程：创建充电桩 → 启动充电 → 监控状态 → 完成充电 → 结算

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testPileData;
let testOrderData;

test.describe('充电工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '⚡ 充电工作流场景开始',
      '本场景将引导您完成：\n1. 创建充电桩\n2. 启动充电订单\n3. 监控充电状态\n4. 完成充电\n5. 查看结算',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：创建充电桩', async () => {
    testPileData = {
      name: `充电桩_${Date.now()}`,
      code: `PILE${Math.floor(Math.random() * 10000)}`,
      type: '快充',
      power: 120,
      location: '测试站点A区',
      manufacturer: '特来电',
      model: 'TLD-120kW'
    };
    
    await helper.navigate('/charging/pile');
    helper.logStep('已进入充电桩管理页面');
    
    await helper.showPrompt('📝 创建充电桩', '请点击"新建充电桩"按钮', 0);
    await helper.highlightElement('button:has-text("新建"), button:has-text("新建充电桩")', 3000);
    await helper.waitForUserConfirm('请点击新建按钮，然后按回车继续');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .pile-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写充电桩信息',
      `请填写：\n
名称：${testPileData.name}
编码：${testPileData.code}
类型：${testPileData.type}
功率：${testPileData.power} kW
位置：${testPileData.location}
厂商：${testPileData.manufacturer}
型号：${testPileData.model}`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="名称"]', 2000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存充电桩', '请保存', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, button[type="submit"]', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功提示');
    helper.logStep('充电桩创建成功');
    
    await helper.takeScreenshot('pile-created');
  });

  test('步骤2：启动充电订单', async () => {
    await helper.navigate('/charging/order');
    helper.logStep('已进入充电订单管理');
    
    await helper.showPrompt('🚗 创建充电订单', '请点击"新建订单"或"扫码充电"', 0);
    await helper.highlightElement('button:has-text("新建订单"), button:has-text("扫码充电")', 3000);
    await helper.waitForUserConfirm('请点击后按回车');
    await helper.closePrompt();
    
    testOrderData = TestData.generateChargingOrder();
    
    await helper.page.waitForSelector('.ant-modal, .order-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '⚡ 填写充电订单',
      `请填写：\n
充电桩：选择刚创建的充电桩
用户：选择一个用户（或模拟扫码）
充电类型：${testOrderData.energy > 30 ? '快充' : '慢充'}
预计电量：${testOrderData.energy} kWh`,
      0
    );
    
    await helper.highlightElement('.pile-selector, select[name="pileId"]', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt('🔌 启动充电', '请点击"开始充电"', 0);
    await helper.highlightElement('button:has-text("开始充电"), button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('启动充电后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示启动成功');
    helper.logStep('充电订单已启动');
    
    await helper.takeScreenshot('charging-started');
  });

  test('步骤3：监控充电状态', async () => {
    await helper.navigate('/charging/order');
    
    await helper.showPrompt(
      '📊 实时监控',
      '请查看充电订单的实时状态：\n• 当前功率\n• 累计电量\n• 充电时长\n• 预计费用',
      0
    );
    
    await helper.highlightElement('.order-status, .charging-monitor', 3000);
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    // 查看详情
    await helper.showPrompt('🔍 查看详情', '请点击订单的"详情"按钮', 0);
    await helper.highlightElement('button:has-text("详情"), a:has-text("详情")', 3000);
    await helper.waitForUserConfirm('查看详情后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForLoadState('networkidle');
    helper.logStep('已进入订单详情页');
    
    // 监控 API
    const apiRequests = await helper.monitorAPI('/api/charging/order/status');
    
    await helper.showPrompt(
      '🔄 实时刷新',
      '请观察页面上的实时数据：\n• 电压/电流曲线\n• SOC 变化\n• 温度监控\n• 异常告警',
      0
    );
    
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    helper.logStep(`监控到 ${apiRequests.length} 次状态更新请求`);
    await helper.takeScreenshot('charging-monitoring');
  });

  test('步骤4：完成充电', async () => {
    await helper.navigate('/charging/order');
    
    // 模拟充电完成或手动停止
    await helper.showPrompt(
      '🛑 停止充电',
      '请找到正在充电的订单，点击"停止充电"按钮',
      0
    );
    
    await helper.highlightElement('button:has-text("停止充电"), button:has-text("结束充电")', 3000);
    await helper.waitForUserConfirm('停止充电后按回车');
    await helper.closePrompt();
    
    // 确认弹窗
    await helper.page.waitForSelector('.ant-modal, .ant-popconfirm', { timeout: 5000 });
    
    await helper.showPrompt('✅ 确认停止', '请在确认弹窗中点击"确定"', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, .ant-popconfirm button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示停止成功');
    helper.logStep('充电已完成');
    
    await helper.takeScreenshot('charging-completed');
  });

  test('步骤5：查看结算', async () => {
    await helper.navigate('/charging/settlement');
    helper.logStep('已进入结算页面');
    
    await helper.showPrompt(
      '💰 查看结算',
      '请搜索并查看刚完成的充电订单的结算信息',
      0
    );
    
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    // 查看详细结算
    await helper.showPrompt('📋 结算详情', '请点击"查看详情"', 0);
    await helper.highlightElement('button:has-text("详情"), a:has-text("详情")', 3000);
    await helper.waitForUserConfirm('查看后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForLoadState('networkidle');
    
    // 显示结算项说明
    await helper.showPrompt(
      '💳 结算明细',
      '请确认以下信息：\n• 充电电量（kWh）\n• 电费单价\n• 服务费\n• 总金额\n• 支付状态',
      0
    );
    
    await helper.highlightElement('.settlement-detail, .bill-info', 3000);
    await helper.waitForUserConfirm('确认无误后按回车');
    await helper.closePrompt();
    
    helper.logStep('结算信息已确认');
    await helper.takeScreenshot('settlement-verified');
  });

  test.afterEach(async () => {
    await helper.generateReport('charging-workflow', {
      scenario: '充电工作流',
      pileData: testPileData,
      orderData: testOrderData,
      timestamp: new Date().toISOString()
    });
  });
});
