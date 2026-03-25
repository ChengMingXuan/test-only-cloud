// ========================================
// 场景脚本 13 - 异常场景处理
// ========================================
// 测试流程：边界值测试 → 非法输入验证 → 并发操作 → 网络故障恢复 → 数据一致性验证

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';
import { TestData } from '../helpers/test-data.js';

let helper;

test.describe('异常场景测试', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '⚠️ 异常场景测试开始',
      '本场景将引导您测试异常情况：\n1. 边界值验证\n2. 非法输入处理\n3. 并发操作\n4. 网络故障恢复\n5. 数据一致性检查',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：边界值验证', async () => {
    await helper.navigate('/user/list');
    
    await helper.showPrompt(
      '📏 边界值测试',
      '本步骤将测试各种边界条件',
      0
    );
    
    // 测试1：创建用户名过长
    await helper.showPrompt(
      '✍️ 测试1：用户名超长',
      '请创建用户时输入超长用户名（>255字符），系统应提示长度限制',
      0
    );
    
    await helper.highlightElement('button:has-text("新建用户"), button:has-text("新建")', 3000);
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.page.waitForSelector('.ant-modal', { timeout: 5000 });
    
    // 输入超长字符串（让用户操作）
    await helper.showPrompt(
      '✅ 验证提示',
      '请观察系统是否显示长度限制提示。\n预期：显示"用户名长度不能超过X字符"',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('用户名长度限制验证完成');
    
    // 测试2：特殊字符输入
    await helper.showPrompt(
      '✍️ 测试2：特殊字符',
      '尝试输入特殊字符（如 ><script>、\'"\\ 等）\n系统应进行 HTML 转义',
      0
    );
    
    await helper.waitForUserAction(20000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证结果',
      '特殊字符应被安全处理，不应执行脚本',
      0
    );
    await helper.waitForUserConfirm('确认处理正确后按回车');
    await helper.closePrompt();
    
    helper.logStep('特殊字符处理验证完成');
    
    await helper.takeScreenshot('boundary-tests');
  });

  test('步骤2：非法输入处理', async () => {
    await helper.navigate('/charging/order');
    
    await helper.showPrompt(
      '❌ 非法输入测试',
      '本步骤测试非法数据的处理',
      0
    );
    
    // 测试1：负数功率
    await helper.showPrompt(
      '📊 测试1：负数输入',
      '尝试在功率/电量字段输入负数\n预期：系统拒绝或提示错误',
      0
    );
    
    await helper.highlightElement('button:has-text("新建訂單"), input[type="number"]', 3000);
    await helper.waitForUserAction(25000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '验证系统是否拒绝负数输入',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('负数验证完成');
    
    // 测试2：日期时间错误
    await helper.showPrompt(
      '📅 测试2：日期异常',
      '尝试输入结束时间早于开始时间\n预期：系统提示日期范围错误',
      0
    );
    
    await helper.highlightElement('input[type="date"], .ant-picker', 3000);
    await helper.waitForUserAction(25000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '验证系统是否拒绝非法日期范围',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('日期范围验证完成');
    
    await helper.takeScreenshot('invalid-input-tests');
  });

  test('步骤3：并发操作', async () => {
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '⚡ 并发操作测试',
      '本步骤测试高并发场景',
      0
    );
    
    await helper.showPrompt(
      '🔄 测试1：快速创建',
      '请快速创建多个设备（连续点击保存，不等待响应）\n系统应正确处理队列',
      0
    );
    
    await helper.highlightElement('button:has-text("新建设备")', 3000);
    await helper.waitForUserAction(35000);
    await helper.closePrompt();
    
    // 监控 API 来看是否有正确的队列处理
    const apiRequests = await helper.monitorAPI('/api/device/create');
    
    await helper.showPrompt(
      '✅ 验证',
      `并发请求已监控。\n系统应正确处理 ${apiRequests.length} 个并发请求，无数据丢失`,
      0
    );
    
    await helper.waitForUserConfirm('确认处理正确后按回车');
    await helper.closePrompt();
    
    helper.logStep(`已验证 ${apiRequests.length} 个并发请求处理`);
    
    // 测试2：重复删除
    await helper.showPrompt(
      '🗑️ 测试2：重复删除',
      '尝试快速重复删除同一个设备\n系统应提示"记录不存在"或返回 404',
      0
    );
    
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '验证系统的幂等性和错误处理',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('并发删除验证完成');
    
    await helper.takeScreenshot('concurrency-tests');
  });

  test('步骤4：网络故障恢复', async () => {
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '🌐 网络故障恢复测试',
      '本步骤测试网络异常情况下的恢复能力',
      0
    );
    
    // 测试1：请求超时
    await helper.showPrompt(
      '⏱️ 测试1：请求超时',
      '打开开发者工具（F12），使用网络限流：\n1. 降速至 2G（极限）\n2. 创建设备并保存\n3. 等待 30+ 秒\n系统应显示超时提示或自动重试',
      0
    );
    
    await helper.highlightElement('button:has-text("新建设备")', 3000);
    await helper.waitForUserAction(60000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '验证超时处理：是否显示"请求超时"或自动重试',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('超时重试验证完成');
    
    // 测试2：离线模式
    await helper.showPrompt(
      '📴 测试2：离线模式',
      '打开开发工具，设置网络为"Offline"（断网）\n尝试执行操作，系统应显示离线提示',
      0
    );
    
    await helper.waitForUserAction(25000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '验证离线检测：应显示"网络连接失败"等提示',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('离线模式验证完成');
    
    // 恢复网络
    await helper.showPrompt(
      '🔌 恢复网络',
      '请恢复网络连接（设置回 Normal）\n系统应自动重新连接，缓冲的操作应继续处理',
      0
    );
    
    await helper.waitForUserConfirm('网络已恢复后按回车');
    await helper.closePrompt();
    
    helper.logStep('网络恢复验证完成');
    
    await helper.takeScreenshot('network-recovery-tests');
  });

  test('步骤5：数据一致性验证', async () => {
    await helper.navigate('/tenant/list');
    
    await helper.showPrompt(
      '🔍 数据一致性验证',
      '本步骤验证在异常情况下的数据完整性',
      0
    );
    
    // 测试1：创建後立即刷新
    await helper.showPrompt(
      '📝 测试1：创建後立即刷新',
      '1. 创建租户\n2. 保存时按 F5 刷新页面\n系统应正确保存数据，刷新后仍可见',
      0
    );
    
    await helper.highlightElement('button:has-text("新建租户")', 3000);
    await helper.waitForUserAction(40000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '页面刷新后，新建的租户应仍在列表中',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('创建後刷新验证完成');
    
    // 测试2：并发更新
    await helper.showPrompt(
      '🔄 测试2：并发更新',
      '1. 在多个标签页打开同一租户\n2. 同时修改相同字段\n3. 验证最后一个保存被采用或冲突提示',
      0
    );
    
    await helper.waitForUserAction(35000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '验证是否正确处理并发更新冲突',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('并发更新验证完成');
    
    // 测试3：部分更新失败
    await helper.showPrompt(
      '❌ 测试3：部分字段更新失败',
      '尝试更新一个字段为非法值（如重复的编码）\n系统应拒绝，其他字段保持原值',
      0
    );
    
    await helper.waitForUserAction(30000);
    await helper.closePrompt();
    
    await helper.showPrompt(
      '✅ 验证',
      '验证事务完整性：失败的更新不应导致部分修改',
      0
    );
    await helper.waitForUserConfirm('确认后按回车');
    await helper.closePrompt();
    
    helper.logStep('数据一致性验证完成');
    
    await helper.takeScreenshot('data-consistency-tests');
  });

  test.afterEach(async () => {
    await helper.generateReport('error-scenarios', {
      scenario: '异常场景处理',
      testCategories: ['边界值', '非法输入', '并发', '网络故障', '数据一致性'],
      timestamp: new Date().toISOString()
    });
  });
});
