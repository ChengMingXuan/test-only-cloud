// ========================================
// 场景脚本 05 - 设备管理
// ========================================
// 测试流程：注册设备 → 配置设备 → 绑定站点 → 监控状态 → 设备退役

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testDeviceData;

test.describe('设备管理工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '🔌 设备管理场景开始',
      '本场景将引导您完成：\n1. 注册新设备\n2. 配置设备参数\n3. 绑定到站点\n4. 监控设备状态\n5. 设备退役',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：注册新设备', async () => {
    testDeviceData = TestData.generateDevice();
    
    await helper.navigate('/device/list');
    helper.logStep('已进入设备管理页面');
    
    await helper.showPrompt('📝 注册设备', '请点击"新建设备"按钮', 0);
    await helper.highlightElement('button:has-text("新建设备"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('请点击新建设备按钮，然后按回车继续');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .device-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写设备信息',
      `请填写：\n
设备名称：${testDeviceData.name}
设备编码：${testDeviceData.code}
设备类型：${testDeviceData.type}
制造商：${testDeviceData.manufacturer}
型号：${testDeviceData.model}
SN：${testDeviceData.sn}
额定功率：${testDeviceData.power} kW
安装位置：${testDeviceData.location}
安装日期：${testDeviceData.installDate}`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="设备名称"], input[name="name"]', 2000);
    await helper.waitForUserAction(60000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存设备', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, button[type="submit"]', 3000);
    await helper.waitForUserConfirm('保存设备后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功提示');
    helper.logStep('设备注册成功');
    
    await helper.takeScreenshot('device-registered');
  });

  test('步骤2：配置设备参数', async () => {
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '🔍 搜索设备',
      `请搜索：${testDeviceData ? testDeviceData.name : '刚创建的设备'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('⚙️ 配置设备', '请点击"配置"或"参数设置"按钮', 0);
    await helper.highlightElement('button:has-text("配置"), button:has-text("参数")', 3000);
    await helper.waitForUserConfirm('点击配置按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .config-form', { timeout: 5000 });
    helper.logStep('已进入设备配置页面');
    
    await helper.showPrompt(
      '🎛️ 设备参数配置',
      '请根据需要配置以下参数：\n• 通讯协议\n• 采集频率\n• 告警阈值\n• 上报周期\n• 控制策略',
      0
    );
    
    await helper.highlightElement('.config-panel, .param-form', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存配置', '请保存参数配置', 0);
    await helper.highlightElement('button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示保存成功');
    helper.logStep('设备参数已配置');
    
    await helper.takeScreenshot('device-configured');
  });

  test('步骤3：绑定到站点', async () => {
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '🔍 查找设备',
      `请搜索：${testDeviceData ? testDeviceData.name : '测试设备'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('🏢 绑定站点', '请点击"绑定站点"按钮', 0);
    await helper.highlightElement('button:has-text("绑定站点"), button:has-text("绑定")', 3000);
    await helper.waitForUserConfirm('点击绑定站点按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .bind-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '🎯 选择站点',
      '请从下拉列表中选择一个站点，将设备绑定到该站点',
      0
    );
    
    await helper.highlightElement('.ant-select, select[name="stationId"]', 3000);
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    await helper.showPrompt('✅ 确认绑定', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认绑定后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示绑定成功');
    helper.logStep('设备已绑定到站点');
    
    await helper.takeScreenshot('device-bound');
  });

  test('步骤4：监控设备状态', async () => {
    await helper.navigate('/device/monitor');
    helper.logStep('已进入设备监控页面');
    
    await helper.showPrompt(
      '📊 实时监控',
      `请查找：${testDeviceData ? testDeviceData.name : '测试设备'}\n并观察其实时状态`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    await helper.showPrompt('🔍 查看详情', '请点击设备卡片或"详情"按钮', 0);
    await helper.highlightElement('.device-card, button:has-text("详情")', 3000);
    await helper.waitForUserConfirm('查看详情后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForLoadState('networkidle');
    
    // 监控 API
    const apiRequests = await helper.monitorAPI('/api/device/status');
    
    await helper.showPrompt(
      '📈 实时数据',
      '请观察设备的实时数据：\n• 运行状态\n• 功率曲线\n• 温度\n• 电压/电流\n• 告警信息',
      0
    );
    
    await helper.highlightElement('.device-status, .realtime-data', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    helper.logStep(`监控到 ${apiRequests.length} 次状态更新`);
    await helper.takeScreenshot('device-monitoring');
  });

  test('步骤5：设备退役', async () => {
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '🔍 查找设备',
      `请搜索测试设备：${testDeviceData ? testDeviceData.name : '测试设备'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('🛑 设备退役', '请点击"退役"或"停用"按钮', 0);
    await helper.highlightElement('button:has-text("退役"), button:has-text("停用")', 3000);
    await helper.waitForUserConfirm('点击退役按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .ant-popconfirm', { timeout: 5000 });
    
    await helper.showPrompt(
      '⚠️ 确认退役',
      '设备退役后将无法使用，请在确认弹窗中点击"确定"',
      0
    );
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, .ant-popconfirm button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('确认退役后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示退役成功');
    helper.logStep('设备已退役');
    
    await helper.takeScreenshot('device-retired');
  });

  test.afterEach(async () => {
    await helper.generateReport('device-management', {
      scenario: '设备管理',
      deviceData: testDeviceData,
      timestamp: new Date().toISOString()
    });
  });
});
