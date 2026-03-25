// ========================================
// 场景脚本 09 - 规则引擎
// ========================================
// 测试流程：创建规则 → 配置条件 → 测试触发 → 监控执行 → 规则调试

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;
let testRuleData;

test.describe('规则引擎工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '⚙️ 规则引擎场景开始',
      '本场景将引导您完成：\n1. 创建规则链\n2. 配置规则节点\n3. 测试规则触发\n4. 监控规则执行\n5. 调试与优化',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：创建规则链', async () => {
    testRuleData = TestData.generateRule();
    
    await helper.navigate('/rule/chains');
    helper.logStep('已进入规则引擎页面');
    
    await helper.showPrompt('📝 创建规则链', '请点击"新建规则链"按钮', 0);
    await helper.highlightElement('button:has-text("新建规则链"), button:has-text("新建")', 3000);
    await helper.waitForUserConfirm('请点击新建按钮，然后按回车继续');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .rule-form', { timeout: 5000 });
    
    await helper.showPrompt(
      '✍️ 填写规则信息',
      `请填写：\n
规则名称：${testRuleData.name}
规则编码：${testRuleData.code}
规则类型：${testRuleData.type}
优先级：${testRuleData.priority}
描述：${testRuleData.description}
启用状态：勾选"立即启用"`,
      0
    );
    
    await helper.highlightElement('input[placeholder*="规则名称"], input[name="name"]', 2000);
    await helper.waitForUserAction(35000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存规则链', '请点击"确定"按钮', 0);
    await helper.highlightElement('.ant-modal-footer button.ant-btn-primary, button[type="submit"]', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示创建成功提示');
    helper.logStep('规则链创建成功');
    
    await helper.takeScreenshot('rule-chain-created');
  });

  test('步骤2：配置规则节点', async () => {
    await helper.navigate('/rule/chains');
    
    await helper.showPrompt(
      '🔍 查找规则链',
      `请搜索：${testRuleData ? testRuleData.name : '刚创建的规则链'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('🎨 打开编辑器', '请点击"编辑"或"设计器"按钮', 0);
    await helper.highlightElement('button:has-text("编辑"), button:has-text("设计器"), a:has-text("编辑")', 3000);
    await helper.waitForUserConfirm('点击编辑按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForLoadState('networkidle');
    helper.logStep('已进入规则设计器');
    
    await helper.showPrompt(
      '🧩 添加规则节点',
      '规则设计器说明：\n
1. 从左侧节点库拖拽节点到画布
2. 常用节点类型：\n   • 输入节点：设备数据、定时触发\n   • 过滤节点：条件判断、数据筛选\n   • 转换节点：数据转换、计算\n   • 动作节点：告警、通知、控制\n   • 输出节点：保存数据、发送消息\n
请创建一个简单的规则流程',
      0
    );
    
    await helper.highlightElement('.node-palette, .node-library', 3000);
    await helper.waitForUserAction(60000);
    await helper.closePrompt();
    
    // 配置节点属性
    await helper.showPrompt(
      '⚙️ 配置节点属性',
      '请依次点击每个节点，配置其属性：\n
• 输入节点：选择数据源（设备/传感器）\n• 过滤节点：设置条件（如 temperature > 40）\n• 动作节点：配置告警/通知方式',
      0
    );
    
    await helper.waitForUserAction(50000);
    await helper.closePrompt();
    
    // 连接节点
    await helper.showPrompt(
      '🔗 连接节点',
      '请拖拽节点之间的连接线，建立数据流向',
      0
    );
    
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存规则', '请点击"保存"按钮', 0);
    await helper.highlightElement('button:has-text("保存"), button.save-btn', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示保存成功');
    helper.logStep('规则节点已配置');
    
    await helper.takeScreenshot('rule-nodes-configured');
  });

  test('步骤3：测试规则触发', async () => {
    await helper.navigate('/rule/chains');
    
    await helper.showPrompt(
      '🔍 查找规则',
      `请搜索：${testRuleData ? testRuleData.name : '测试规则'}`,
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('🧪 测试规则', '请点击"测试"或"调试"按钮', 0);
    await helper.highlightElement('button:has-text("测试"), button:has-text("调试")', 3000);
    await helper.waitForUserConfirm('点击测试按钮后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal, .test-panel', { timeout: 5000 });
    
    await helper.showPrompt(
      '📥 输入测试数据',
      '请输入测试数据模拟规则触发：\n
• 方式1：手动输入 JSON 数据\n• 方式2：选择历史数据\n• 方式3：使用数据模板\n
示例数据：\n{\n  "deviceId": "DEV001",\n  "temperature": 45,\n  "timestamp": "2026-03-05T10:00:00Z"\n}',
      0
    );
    
    await helper.highlightElement('textarea, .json-editor, .test-input', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('▶️ 执行测试', '请点击"执行"按钮', 0);
    await helper.highlightElement('button:has-text("执行"), button.run-btn', 3000);
    await helper.waitForUserConfirm('执行测试后按回车');
    await helper.closePrompt();
    
    // 等待执行完成
    await helper.page.waitForTimeout(3000);
    
    await helper.showPrompt(
      '✅ 查看执行结果',
      '请查看测试结果：\n• 执行状态：成功/失败\n• 执行日志：每个节点的输入输出\n• 执行时间：耗时统计\n• 触发动作：是否发送了告警/通知',
      0
    );
    
    await helper.highlightElement('.test-result, .execution-log', 3000);
    await helper.waitForUserConfirm('确认结果后按回车');
    await helper.closePrompt();
    
    helper.logStep('规则测试完成');
    await helper.takeScreenshot('rule-test-result');
  });

  test('步骤4：监控规则执行', async () => {
    await helper.navigate('/rule/monitor');
    helper.logStep('已进入规则监控页面');
    
    await helper.showPrompt(
      '📊 选择规则',
      `请选择要监控的规则：${testRuleData ? testRuleData.name : '测试规则'}`,
      0
    );
    
    await helper.highlightElement('.rule-selector, select[name="ruleId"]', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    // 监控 API
    const apiRequests = await helper.monitorAPI('/api/rule/execution');
    
    await helper.showPrompt(
      '📈 实时监控指标',
      '请观察规则执行数据：\n
• 执行统计：总次数、成功率、失败率\n• 执行耗时：平均耗时、最大耗时\n• 触发频率：按时间段统计\n• 错误日志：失败原因分析\n• 性能曲线：执行趋势图',
      0
    );
    
    await helper.highlightElement('.monitor-panel, .execution-stats', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    // 查看执行历史
    await helper.showPrompt(
      '📋 查看执行历史',
      '请切换到"执行历史"标签页，查看详细记录',
      0
    );
    
    await helper.highlightElement('.ant-tabs-tab:has-text("执行历史"), a:has-text("历史")', 3000);
    await helper.waitForUserConfirm('查看历史后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForTimeout(2000);
    
    helper.logStep(`监控到 ${apiRequests.length} 次规则执行`);
    await helper.takeScreenshot('rule-monitoring');
  });

  test('步骤5：调试与优化', async () => {
    await helper.navigate('/rule/chains');
    
    await helper.showPrompt(
      '🔍 查找需要优化的规则',
      '请筛选执行耗时较长或失败率较高的规则',
      0
    );
    await helper.highlightElement('input[placeholder*="搜索"], .filter-panel', 3000);
    await helper.waitForUserAction(10000);
    await helper.closePrompt();
    
    await helper.showPrompt('🐛 打开调试器', '请点击"调试"按钮', 0);
    await helper.highlightElement('button:has-text("调试"), button:has-text("Debug")', 3000);
    await helper.waitForUserConfirm('打开调试器后按回车');
    await helper.closePrompt();
    
    await helper.page.waitForLoadState('networkidle');
    
    await helper.showPrompt(
      '🔍 分析问题',
      '调试器功能说明：\n
• 断点设置：在节点上设置断点\n• 单步执行：逐节点查看数据流\n• 变量查看：查看每个节点的输入输出\n• 性能分析：查看每个节点的耗时\n• 日志输出：实时查看执行日志\n
请设置断点并单步执行规则',
      0
    );
    
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '🔧 优化规则',
      '根据调试结果优化规则：\n
• 简化复杂条件\n• 减少不必要的节点\n• 优化数据查询\n• 添加缓存机制\n• 调整执行顺序',
      0
    );
    
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt('💾 保存优化', '请保存优化后的规则', 0);
    await helper.highlightElement('button:has-text("保存"), button.save-btn', 3000);
    await helper.waitForUserConfirm('保存后按回车');
    await helper.closePrompt();
    
    await helper.assertVisible('.ant-message-success', '应显示保存成功');
    helper.logStep('规则已优化');
    
    await helper.takeScreenshot('rule-optimized');
  });

  test.afterEach(async () => {
    await helper.generateReport('rule-engine', {
      scenario: '规则引擎',
      ruleData: testRuleData,
      timestamp: new Date().toISOString()
    });
  });
});
