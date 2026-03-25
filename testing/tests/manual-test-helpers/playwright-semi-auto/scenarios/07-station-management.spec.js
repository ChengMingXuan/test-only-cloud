// ========================================
// 场景脚本 07 - 站点管理
// ========================================
// 测试流程：创建站点 → 添加设备 → 配置监控 → 查看统计 → 维护

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testStationData;
let testDeviceData;

test.describe('站点管理工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '🏢 站点管理场景开始',
      '本场景将引导您完成：\n1. 创建新站点\n2. 添加设备到站点\n3. 配置站点参数\n4. 监控站点运营\n5. 站点维护管理',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：创建新站点', async () => {
    testStationData = TestData.generateStation();
    
    await helper.navigate('/station/list');
    helper.logStep('已进入站点管理页面');
    
    await helper.showPrompt('📝 创建站点', '请点击"新建站点"按钮', 0);
    await helper.highlightElement('button:has-text("新建站点"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('请点击新建站点按钮，然后按回车继续');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .station-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写站点信息',
      `请填写：\n
站点名称：${testStationData.name}
站点编码：${testStationData.code}
站点类型：${testStationData.type}
详细地址：${testStationData.address}
经度：${testStationData.longitude}
纬度：${testStationData.latitude}
设备容量：${testStationData.capacity} kW
运营商：${testStationData.operator}
联系电话：${testStationData.contactPhone}`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="站点名称"], input[name="name"]', 2000);
    await helper.waitForUserAction(60000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存站点', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, button[type="submit"]', 3000);
    await helper.waitForUserConfirm('保存站点后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功提示');
    helper.logStep('站点创建成功');
    
    await helper.takeScreenshot('station-created');
  });

  test('步骤2：添加设备到站点', async () => {
    await helper.navigate('/station/list');
    
    await helper.showPrompt(
      '🔍 搜索站点',
      `请搜索：${testStationData ? testStationData.name : '刚创建的站点'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('📦 添加设备', '请点击"设备管理"或"添加设备"按钮', 0);
    await helper.highlightElement('button:has-text("设备管理"), button:has-text("添加设备"), a:has-text("设备")', 3000);
    await helper.waitForUserConfirm('点击后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForTimeout(2000);
    
    await helper.showPrompt(
      '🔧 选择设备',
      '请从设备列表中选择要添加到此站点的设备\n可以是充电桩、储能柜、光伏板等',
      0
    );
    
    await helper.highlightElement('.device-selector, .device-list, button:has-text("选择设备")', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt('✅ 确认添加', '请确认添加设备', 0);
    await helper.highlightElement('button.ant-btn-primary, button:has-text("确定")', 3000);
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示添加成功');
    helper.logStep('设备已添加到站点');
    
    await helper.takeScreenshot('devices-added');
  });

  test('步骤3：配置站点参数', async () => {
    await helper.navigate('/station/list');
    
    await helper.showPrompt(
      '🔍 查找站点',
      `请搜索：${testStationData ? testStationData.name : '测试站点'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('⚙️ 站点配置', '请点击"配置"或"参数设置"按钮', 0);
    await helper.highlightElement('button:has-text("配置"), button:has-text("参数")', 3000);
    await helper.waitForUserConfirm('点击配置按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .config-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '🎛️ 配置参数',
      `请配置站点参数：\n
• 运营时间：设置开放时间段
• 功率调度策略：峰谷平调度规则
• 告警阈值：温度、功率等告警限值
• 接入协议：Modbus/MQTT/OPC-UA
• 数据上报周期：实时数据上报频率
• 安全策略：访问控制、应急处理`,
      0
    );
    
    await helper.highlightElement('.config-panel, .param-form', 3000);
    await helper.waitForUserAction(50000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存配置', '请保存配置', 0);
    await helper.highlightElement('button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示保存成功');
    helper.logStep('站点参数已配置');
    
    await helper.takeScreenshot('station-configured');
  });

  test('步骤4：监控站点运营', async () => {
    await helper.navigate('/station/monitor');
    helper.logStep('已进入站点监控页面');
    
    await helper.showPrompt(
      '📊 选择站点',
      `请在监控大屏中找到：${testStationData ? testStationData.name : '测试站点'}`,
      0
    );
    
    await helper.highlightElement('.station-selector, input[placeholder*="站点"]', 3000);
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    // 监控 API
    const apiRequests = await helper.monitorAPI('/api/station/realtime');
    
    await helper.showPrompt(
      '🔍 查看监控数据',
      '请点击站点卡片或"详情"按钮查看实时监控',
      0
    );
    await helper.highlightElement('.station-card, button:has-text("详情")', 3000);
    await helper.waitForUserConfirm('查看详情后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForLoadState('networkidle');
    
    await helper.showPrompt(
      '📈 实时监控指标',
      '请观察以下监控数据：\n• 总发电量/用电量\n• 设备在线率\n• 实时功率曲线\n• 收益统计\n• 告警列表\n• 设备状态分布',
      0
    );
    
    await helper.highlightElement('.monitor-panel, .realtime-data', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    helper.logStep(`监控到 ${apiRequests.length} 次数据更新`);
    await helper.takeScreenshot('station-monitoring');
  });

  test('步骤5：站点维护管理', async () => {
    await helper.navigate('/station/maintenance');
    helper.logStep('已进入站点维护管理');
    
    await helper.showPrompt(
      '🔧 创建维护计划',
      `为站点 ${testStationData ? testStationData.name : '测试站点'} 创建维护计划`,
      0
    );
    
    await helper.highlightElement('button:has-text("创建计划"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('点击创建计划按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .maintenance-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '📝 填写维护计划',
      `请填写：\n
• 计划名称：例如"定期巡检"
• 维护类型：日常巡检/设备保养/故障抢修
• 计划周期：每周/每月/每季度
• 负责人：选择维护工程师
• 维护内容：检查项目清单
• 预计用时：小时数`,
      0
    );
    
    await helper.highlightElement('input[name="name"], input[placeholder*="名称"]', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存计划', '请保存维护计划', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功');
    helper.logStep('维护计划已创建');
    
    await helper.takeScreenshot('maintenance-plan-created');
    
    // 查看维护记录
    await helper.showPrompt(
      '📋 查看维护记录',
      '请切换到"维护记录"标签页，查看历史维护记录',
      0
    );
    
    await helper.highlightElement('.ant-tabs-tab:has-text("维护记录"), a:has-text("记录")', 3000);
    await helper.waitForUserConfirm('查看记录后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForTimeout(2000);
    
    await helper.showPrompt(
      '✅ 验证完成',
      '请确认能看到维护记录列表，包括：\n• 维护时间\n• 维护人员\n• 维护内容\n• 维护结果',
      0
    );
    
    await helper.waitForUserConfirm('确认无误后按回车');
    await helper.closePrompt();
    
    helper.logStep('站点维护管理已验证');
    await helper.takeScreenshot('maintenance-records');
  });

  test.afterEach(async () => {
    await helper.generateReport('station-management', {
      scenario: '站点管理',
      stationData: testStationData,
      timestamp: new Date().toISOString()
    });
  });
});
