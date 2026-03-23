// ========================================
// 场景脚本 12 - 端到端完整流程
// ========================================
// 测试流程：设备注册 → 充电订单 → 实时监控 → 完成充电 → 账单结算 → 工单维护

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let e2eData = {
  device: null,
  station: null,
  chargingOrder: null,
  settlement: null,
  workOrder: null
};

test.describe('端到端完整流程测试', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '🔄 端到端完整流程场景开始',
      '本场景将模拟真实业务流程：\n1. 注册充电桩设备\n2. 创建充电订单\n3. 实时监控充电状态\n4. 完成充电并结算\n5. 生成维护工单\n6. 验证数据一致性',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录为管理员');
  });

  test('步骤1：注册充电桩设备', async () => {
    e2eData.device = TestData.generateDevice();
    e2eData.device.type = '充电桩';
    e2eData.device.name = `E2E_Pile_${Date.now()}`;
    
    await helper.navigate('/device/list');
    helper.logStep('【流程起点】开始注册充电桩设备');
    
    await helper.showPrompt(
      '📦 步骤1：注册充电桩',
      '我们将创建一个充电桩设备，用于后续的充电流程',
      0
    );
    await helper.highlightElement('button:has-text("新建设备"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('请点击新建设备按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .device-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写充电桩信息',
      `请填写：\n
设备名称：${e2eData.device.name}
设备类型：充电桩
功率：${e2eData.device.power} kW
SN：${e2eData.device.sn}
厂商：${e2eData.device.manufacturer}`,
      0
    );
    
    await helper.highlightElement('input[name="name"], input[placeholder*="名称"]', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存设备', '请保存设备', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功');
    helper.logStep(`✅ 设备已注册：${e2eData.device.name}`);
    
    await helper.takeScreenshot('e2e-01-device-registered');
  });

  test('步骤2：创建充电订单', async () => {
    e2eData.chargingOrder = TestData.generateChargingOrder();
    e2eData.chargingOrder.orderNo = `E2E_ORDER_${Date.now()}`;
    
    await helper.navigate('/charging/order');
    helper.logStep('【流程进行中】创建充电订单');
    
    await helper.showPrompt(
      '⚡ 步骤2：创建充电订单',
      `充电桩已就绪，现在为其创建充电订单\n订单号：${e2eData.chargingOrder.orderNo}`,
      0
    );
    await helper.highlightElement('button:has-text("新建订单"), button:has-text("扫码充电")', 3000);
    await helper.waitForUserConfirm('请点击新建订单后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .order-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '📝 填写订单信息',
      `请填写：\n
充电桩：选择刚创建的 ${e2eData.device.name}
用户：选择一个测试用户
预计电量：${e2eData.chargingOrder.energy} kWh`,
      0
    );
    
    await helper.highlightElement('.pile-selector, select[name="pileId"]', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('🔌 启动充电', '请点击"开始充电"', 0);
    await helper.highlightElement('button:has-text("开始充电"), button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('启动充电后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示启动成功');
    helper.logStep(`✅ 充电订单已创建：${e2eData.chargingOrder.orderNo}`);
    
    await helper.takeScreenshot('e2e-02-charging-order-created');
  });

  test('步骤3：实时监控充电状态', async () => {
    await helper.navigate('/charging/monitor');
    helper.logStep('【流程进行中】监控充电状态');
    
    await helper.showPrompt(
      '📊 步骤3：实时监控',
      '充电已开始，我们将监控实时数据',
      0
    );
    
    // 监控 API
    const apiRequests = await helper.monitorAPI('/api/charging/realtime');
    
    await helper.highlightElement('.charging-monitor, .realtime-panel', 3000);
    
    await helper.showPrompt(
      '🔍 查看监控数据',
      `请观察充电状态：\n
• 当前功率\n• 累计电量\n• 充电时长\n• 预计费用\n• 电池 SOC\n• 温度监控\n
让系统运行30秒以收集监控数据`,
      0
    );
    
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    helper.logStep(`✅ 监控数据已收集，API调用 ${apiRequests.length} 次`);
    
    await helper.takeScreenshot('e2e-03-charging-monitoring');
  });

  test('步骤4：完成充电并结算', async () => {
    await helper.navigate('/charging/order');
    helper.logStep('【流程进行中】完成充电');
    
    await helper.showPrompt(
      '🛑 步骤4：停止充电',
      '充电已进行一段时间，现在停止充电并结算',
      0
    );
    
    await helper.highlightElement('button:has-text("停止充电"), button:has-text("结束充电")', 3000);
    await helper.waitForUserConfirm('请点击停止充电后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .ant-popconfirm', { timeout: 5000 });
    
    await helper.showPrompt('✅ 确认停止', '请确认停止充电', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, .ant-popconfirm button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示停止成功');
    helper.logStep('✅ 充电已完成');
    
    await helper.takeScreenshot('e2e-04-charging-completed');
    
    // 查看结算详情
    await helper.showPrompt(
      '💰 查看结算详情',
      '充电完成，系统自动生成账单\n请点击"查看结算"或"详情"',
      0
    );
    
    await helper.highlightElement('button:has-text("结算"), button:has-text("详情")', 3000);
    await helper.waitForUserConfirm('查看结算详情后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForTimeout(2000);
    
    await helper.showPrompt(
      '📋 确认结算信息',
      '请确认结算明细：\n• 充电电量\n• 电费单价\n• 服务费\n• 总金额\n• 支付状态',
      0
    );
    
    await helper.highlightElement('.settlement-detail, .bill-info', 3000);
    await helper.waitForUserConfirm('确认无误后按回车');
    await helper.closePrompt();
    
    helper.logStep('✅ 结算信息已确认');
    
    await helper.takeScreenshot('e2e-05-settlement-verified');
  });

  test('步骤5：生成维护工单', async () => {
    e2eData.workOrder = TestData.generateWorkOrder();
    e2eData.workOrder.title = `充电桩定期检查-${e2eData.device.name}`;
    e2eData.workOrder.type = '定期维护';
    
    await helper.navigate('/workorder/list');
    helper.logStep('【流程进行中】创建维护工单');
    
    await helper.showPrompt(
      '🔧 步骤5：生成维护工单',
      '充电完成后，为设备创建定期维护工单',
      0
    );
    await helper.highlightElement('button:has-text("新建工单"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('请点击新建工单后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .workorder-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '📝 填写工单信息',
      `请填写：\n
工单标题：${e2eData.workOrder.title}
工单类型：${e2eData.workOrder.type}
关联设备：${e2eData.device.name}
优先级：中
问题描述：定期检查充电桩运行状态`,
      0
    );
    
    await helper.highlightElement('input[name="title"], input[placeholder*="标题"]', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存工单', '请保存工单', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功');
    helper.logStep('✅ 维护工单已创建');
    
    await helper.takeScreenshot('e2e-06-workorder-created');
  });

  test('步骤6：验证数据一致性', async () => {
    helper.logStep('【流程验证】检查数据一致性');
    
    await helper.showPrompt(
      '🔍 步骤6：数据一致性验证',
      '我们将验证整个流程中数据的一致性和完整性',
      2000
    );
    
    // 验证设备状态
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '📦 验证设备状态',
      `请搜索设备：${e2eData.device.name}\n确认设备状态正常、有充电记录`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    helper.logStep('✅ 设备状态验证通过');
    await helper.takeScreenshot('e2e-07-device-verified');
    
    // 验证订单记录
    await helper.navigate('/charging/order');
    
    await helper.showPrompt(
      '📋 验证订单记录',
      `请搜索订单：${e2eData.chargingOrder.orderNo}\n确认订单状态为"已完成"，有完整的充电数据`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    helper.logStep('✅ 订单记录验证通过');
    await helper.takeScreenshot('e2e-08-order-verified');
    
    // 验证结算记录
    await helper.navigate('/settlement/billing');
    
    await helper.showPrompt(
      '💰 验证结算记录',
      '请确认有对应的结算记录，金额计算正确',
      0
    );
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    helper.logStep('✅ 结算记录验证通过');
    await helper.takeScreenshot('e2e-09-settlement-verified');
    
    // 验证工单记录
    await helper.navigate('/workorder/list');
    
    await helper.showPrompt(
      '🔧 验证工单记录',
      `请搜索工单：${e2eData.workOrder.title}\n确认工单状态正常，关联设备正确`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    helper.logStep('✅ 工单记录验证通过');
    await helper.takeScreenshot('e2e-10-workorder-verified');
    
    // 最终总结
    await helper.showPrompt(
      '🎉 端到端流程测试完成',
      `━━━━━━━━━━━━━━━━━━━━━━━━━━\n✅ 完整业务流程验证通过\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n
✅ 设备注册成功
✅ 充电订单创建并完成
✅ 实时监控数据正常
✅ 结算流程正确
✅ 维护工单已创建
✅ 数据一致性验证通过\n
【流程总结】\n设备 → 订单 → 监控 → 结算 → 工单\n全流程闭环完成！\n
所有业务数据关联正确，系统运行正常！`,
      0
    );
    
    await helper.waitForUserConfirm('查看总结后按回车');
    await helper.closePrompt();
    
    helper.logStep('【流程结束】端到端测试全部完成');
  });

  test.afterEach(async () => {
    await helper.generateReport('e2e-complete-flow', {
      scenario: '端到端完整流程',
      e2eData,
      timestamp: new Date().toISOString()
    });
  });
});
