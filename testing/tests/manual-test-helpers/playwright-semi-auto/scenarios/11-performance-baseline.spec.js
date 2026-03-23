// ========================================
// 场景脚本 11 - 性能基线测试
// ========================================
// 测试流程：加载页面 → 测量指标 → 对比基线 → 生成报告 → 性能优化建议

import { test, expect } from '@playwright/test';
import { SemiAutoHelper } from '../helpers/semi-auto-helper.js';

let helper;
let performanceMetrics = {};

test.describe('性能基线测试工作流', () => {
  test.beforeEach(async ({ page }) => {
    helper = new SemiAutoHelper(page);
    
    await helper.showPrompt(
      '⚡ 性能基线测试场景开始',
      '本场景将引导您完成：\n1. 测试关键页面加载性能\n2. 测量交互响应时间\n3. API 响应时间统计\n4. 对比性能基线\n5. 生成性能报告',
      3000
    );
    
    await helper.login('admin');
    helper.logStep('已登录');
  });

  test('步骤1：测试首页加载性能', async () => {
    await helper.showPrompt(
      '🏠 测试首页性能',
      '我们将测量首页加载的各项性能指标',
      2000
    );
    
    const startTime = Date.now();
    
    // 导航到首页并等待加载完成
    await helper.navigate('/dashboard');
    
    const loadTime = Date.now() - startTime;
    
    // 获取性能指标
    const metrics = await helper.page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0];
      const paintData = performance.getEntriesByType('paint');
      
      return {
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
        firstPaint: paintData.find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paintData.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        domInteractive: perfData.domInteractive - perfData.fetchStart,
        totalLoadTime: perfData.loadEventEnd - perfData.fetchStart
      };
    });
    
    performanceMetrics.homepage = {
      ...metrics,
      measuredLoadTime: loadTime
    };
    
    helper.logStep(`首页加载完成，总耗时：${loadTime}ms`);
    
    await helper.showPrompt(
      '📊 首页性能指标',
      `测量结果：\n
• 总加载时间：${loadTime}ms
• DOM 内容加载：${metrics.domContentLoaded.toFixed(0)}ms
• 首次绘制(FP)：${metrics.firstPaint.toFixed(0)}ms
• 首次内容绘制(FCP)：${metrics.firstContentfulPaint.toFixed(0)}ms
• DOM 可交互：${metrics.domInteractive.toFixed(0)}ms
• 完全加载：${metrics.totalLoadTime.toFixed(0)}ms\n
基线标准：\n✅ 总加载 < 3000ms\n✅ FCP < 1500ms\n✅ DOM可交互 < 2000ms`,
      0
    );
    
    await helper.waitForUserConfirm('查看性能指标后按回车');
    await helper.closePrompt();
    
    await helper.takeScreenshot('homepage-performance');
  });

  test('步骤2：测试设备列表页加载性能', async () => {
    await helper.showPrompt(
      '📦 测试设备列表性能',
      '我们将测量设备列表页的加载和渲染性能',
      2000
    );
    
    const startTime = Date.now();
    
    // 监控 API 请求
    const apiRequests = await helper.monitorAPI('/api/device');
    
    await helper.navigate('/device/list');
    
    // 等待表格渲染完成
    await helper.page.waitForSelector('.ant-table', { timeout: 10000 });
    
    const loadTime = Date.now() - startTime;
    
    // 统计页面元素
    const elementCount = await helper.page.evaluate(() => {
      return {
        totalElements: document.querySelectorAll('*').length,
        tableRows: document.querySelectorAll('.ant-table-row').length,
        images: document.querySelectorAll('img').length,
        scripts: document.querySelectorAll('script').length
      };
    });
    
    performanceMetrics.deviceList = {
      loadTime,
      apiCalls: apiRequests.length,
      elementCount
    };
    
    helper.logStep(`设备列表加载完成，耗时：${loadTime}ms`);
    
    await helper.showPrompt(
      '📊 设备列表性能指标',
      `测量结果：\n
• 页面加载时间：${loadTime}ms
• API 调用次数：${apiRequests.length}
• 表格行数：${elementCount.tableRows}
• 总 DOM 元素：${elementCount.totalElements}
• 图片数量：${elementCount.images}\n
基线标准：\n✅ 加载时间 < 2000ms\n✅ API < 5 次\n✅ 100 行数据渲染 < 1000ms`,
      0
    );
    
    await helper.waitForUserConfirm('查看性能指标后按回车');
    await helper.closePrompt();
    
    await helper.takeScreenshot('device-list-performance');
  });

  test('步骤3：测试交互响应性能', async () => {
    await helper.navigate('/device/list');
    
    await helper.showPrompt(
      '🖱️ 测试交互响应',
      '我们将测量搜索、筛选等交互操作的响应时间',
      2000
    );
    
    // 测试搜索响应时间
    await helper.highlightElement('input[placeholder*="搜索"]', 2000);
    
    await helper.showPrompt(
      '🔍 搜索性能测试',
      '请在搜索框中输入任意关键词\n我们将测量搜索响应时间',
      0
    );
    
    const searchStartTime = Date.now();
    
    await helper.waitForUserAction(15000);
    await helper.closePrompt();
    
    // 等待搜索结果
    await helper.page.waitForTimeout(500);
    
    const searchTime = Date.now() - searchStartTime;
    
    performanceMetrics.searchResponse = searchTime;
    
    helper.logStep(`搜索响应时间：${searchTime}ms`);
    
    // 测试表格排序
    await helper.showPrompt(
      '🔢 排序性能测试',
      '请点击表格的任意列标题进行排序\n我们将测量排序响应时间',
      0
    );
    
    await helper.highlightElement('.ant-table-column-sorters', 2000);
    
    const sortStartTime = Date.now();
    
    await helper.waitForUserConfirm('点击排序后按回车');
    await helper.closePrompt();
    
    const sortTime = Date.now() - sortStartTime;
    
    performanceMetrics.sortResponse = sortTime;
    
    helper.logStep(`排序响应时间：${sortTime}ms`);
    
    await helper.showPrompt(
      '📊 交互性能指标',
      `测量结果：\n
• 搜索响应时间：${searchTime}ms
• 排序响应时间：${sortTime}ms\n
基线标准：\n✅ 搜索响应 < 500ms\n✅ 排序响应 < 300ms\n✅ 点击响应 < 200ms`,
      0
    );
    
    await helper.waitForUserConfirm('查看后按回车');
    await helper.closePrompt();
    
    await helper.takeScreenshot('interaction-performance');
  });

  test('步骤4：测试 API 响应性能', async () => {
    await helper.showPrompt(
      '🌐 API 性能测试',
      '我们将测量关键 API 接口的响应时间',
      2000
    );
    
    // 监控多个 API
    const apiMetrics = [];
    
    // 测试用户列表 API
    await helper.navigate('/user/list');
    const userApiStart = Date.now();
    await helper.page.waitForLoadState('networkidle');
    const userApiTime = Date.now() - userApiStart;
    apiMetrics.push({ api: '/api/user/list', time: userApiTime });
    
    helper.logStep(`用户列表 API：${userApiTime}ms`);
    
    // 测试设备列表 API
    await helper.navigate('/device/list');
    const deviceApiStart = Date.now();
    await helper.page.waitForLoadState('networkidle');
    const deviceApiTime = Date.now() - deviceApiStart;
    apiMetrics.push({ api: '/api/device/list', time: deviceApiTime });
    
    helper.logStep(`设备列表 API：${deviceApiTime}ms`);
    
    // 测试工单列表 API
    await helper.navigate('/workorder/list');
    const workorderApiStart = Date.now();
    await helper.page.waitForLoadState('networkidle');
    const workorderApiTime = Date.now() - workorderApiStart;
    apiMetrics.push({ api: '/api/workorder/list', time: workorderApiTime });
    
    helper.logStep(`工单列表 API：${workorderApiTime}ms`);
    
    performanceMetrics.apiResponses = apiMetrics;
    
    const avgApiTime = (userApiTime + deviceApiTime + workorderApiTime) / 3;
    
    await helper.showPrompt(
      '📊 API 性能指标',
      `测量结果：\n
• 用户列表 API：${userApiTime}ms
• 设备列表 API：${deviceApiTime}ms
• 工单列表 API：${workorderApiTime}ms
• 平均响应时间：${avgApiTime.toFixed(0)}ms\n
基线标准：\n✅ 查询 API < 500ms\n✅ 创建 API < 1000ms\n✅ 批量操作 < 2000ms`,
      0
    );
    
    await helper.waitForUserConfirm('查看后按回车');
    await helper.closePrompt();
    
    await helper.takeScreenshot('api-performance');
  });

  test('步骤5：生成性能报告', async () => {
    await helper.showPrompt(
      '📄 生成性能报告',
      '我们将汇总所有性能指标并生成报告',
      2000
    );
    
    // 计算总体评分
    const scores = {
      homepage: performanceMetrics.homepage?.measuredLoadTime < 3000 ? 100 : 70,
      deviceList: performanceMetrics.deviceList?.loadTime < 2000 ? 100 : 70,
      interaction: (performanceMetrics.searchResponse < 500 && performanceMetrics.sortResponse < 300) ? 100 : 70,
      api: performanceMetrics.apiResponses?.every(a => a.time < 500) ? 100 : 70
    };
    
    const averageScore = Object.values(scores).reduce((a, b) => a + b, 0) / Object.keys(scores).length;
    
    const performanceReport = {
      测试时间: new Date().toISOString(),
      性能指标: performanceMetrics,
      分项评分: scores,
      总体评分: averageScore.toFixed(0),
      评级: averageScore >= 90 ? '优秀' : averageScore >= 75 ? '良好' : averageScore >= 60 ? '及格' : '需优化',
      建议: [
        performanceMetrics.homepage?.measuredLoadTime > 3000 ? '⚠️ 首页加载过慢，建议优化资源加载' : '✅ 首页加载性能良好',
        performanceMetrics.deviceList?.loadTime > 2000 ? '⚠️ 列表页加载较慢，建议实现虚拟滚动' : '✅ 列表页加载性能良好',
        performanceMetrics.searchResponse > 500 ? '⚠️ 搜索响应较慢，建议优化查询逻辑' : '✅ 搜索响应速度良好',
        performanceMetrics.apiResponses?.some(a => a.time > 500) ? '⚠️ 部分 API 响应较慢，建议优化查询或添加缓存' : '✅ API 响应速度良好'
      ]
    };
    
    helper.logStep('性能报告已生成');
    
    await helper.showPrompt(
      '🎯 性能测试报告',
      `━━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 AIOPS 系统性能测试报告\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n
【总体评分】${performanceReport.总体评分} 分 - ${performanceReport.评级}\n
【分项评分】
• 首页加载：${scores.homepage} 分
• 列表页面：${scores.deviceList} 分
• 交互响应：${scores.interaction} 分
• API 性能：${scores.api} 分\n
【优化建议】
${performanceReport.建议.join('\n')}\n
━━━━━━━━━━━━━━━━━━━━━━━━━━`,
      0
    );
    
    await helper.waitForUserConfirm('查看完整报告后按回车');
    await helper.closePrompt();
    
    await helper.takeScreenshot('performance-report');
    
    // 保存详细报告
    console.log('\n📊 详细性能报告：\n', JSON.stringify(performanceReport, null, 2));
    
    helper.logStep('性能报告已输出到控制台');
  });

  test.afterEach(async () => {
    await helper.generateReport('performance-baseline', {
      scenario: '性能基线测试',
      metrics: performanceMetrics,
      timestamp: new Date().toISOString()
    });
  });
});
