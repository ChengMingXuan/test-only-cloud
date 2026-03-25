/**
 * 统一测试编排器
 * 协调执行 Playwright + Selenium + Puppeteer + Cypress + K6 五个测试工具
 * 
 * 功能:
 * - 按顺序或并行执行全部测试
 * - 聚合测试报告
 * - 生成统一的HTML仪表盘
 * - 判断发布门禁是否通过
 */

const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

// ========== 配置 ==========
const CONFIG = {
  reportDir: path.join(__dirname, '..', 'test-reports'),
  aggregatedReportPath: path.join(__dirname, '..', 'test-reports', 'aggregated-report.json'),
  testSuites: [
    {
      name: 'pytest',
      command: 'pytest',
      args: ['../test-automation/', '-v'],
      cwd: path.join(__dirname, '..', 'test-automation'),
      reportPath: '../test-reports/pytest-report/summary.json',
      timeout: 15 * 60 * 1000, // 15分钟
      priority: 1, // 最高优先级，最先执行
    },
    {
      name: 'cypress',
      command: 'npm',
      args: ['run', 'cy:run'],
      cwd: path.join(__dirname, '..', 'cypress-tests'),
      reportPath: '../test-reports/cypress-report/summary.json',
      timeout: 20 * 60 * 1000,
      priority: 2,
    },
    {
      name: 'playwright',
      command: 'npm',
      args: ['test'],
      cwd: path.join(__dirname, '..', 'playwright-tests'),
      reportPath: '../test-reports/playwright-report/summary.json',
      timeout: 40 * 60 * 1000,
      priority: 3,
    },
    {
      name: 'selenium',
      command: 'pytest',
      args: ['tests/', '-v', '--html=../test-reports/selenium-report/report.html'],
      cwd: path.join(__dirname, '..', 'selenium-tests'),
      reportPath: '../test-reports/selenium-report/summary.json',
      timeout: 120 * 60 * 1000, // 2小时
      priority: 4,
    },
    {
      name: 'puppeteer',
      command: 'node',
      args: ['tests/performance-baseline.js'],
      cwd: path.join(__dirname, '..', 'puppeteer-tests'),
      reportPath: '../test-reports/puppeteer-report/summary.json',
      timeout: 30 * 60 * 1000,
      priority: 5,
    },
    {
      name: 'k6',
      command: 'k6',
      args: ['run', 'scenarios/load-test.js'],
      cwd: path.join(__dirname, '..', '..', 'k6'),
      reportPath: '../test-reports/k6-report/summary.json',
      timeout: 60 * 60 * 1000, // 1小时
      priority: 6,
    },
  ],
};

// ========== Helper Functions ==========

/**
 * 执行单个测试套件
 */
function runTestSuite(suite) {
  return new Promise((resolve, reject) => {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🚀 执行测试套件: ${suite.name}`);
    console.log(`   命令: ${suite.command} ${suite.args.join(' ')}`);
    console.log(`   超时: ${suite.timeout / 1000}秒`);
    console.log(`${'='.repeat(60)}\n`);
    
    const startTime = Date.now();
    
    const proc = spawn(suite.command, suite.args, {
      cwd: suite.cwd,
      stdio: 'inherit', // 继承标准输入输出
      shell: true,
    });
    
    const timeoutId = setTimeout(() => {
      proc.kill();
      reject(new Error(`${suite.name} 测试超时 (${suite.timeout / 1000}秒)`));
    }, suite.timeout);
    
    proc.on('close', (code) => {
      clearTimeout(timeoutId);
      const duration = Date.now() - startTime;
      
      console.log(`\n${'='.repeat(60)}`);
      console.log(`${code === 0 ? '✅' : '❌'} ${suite.name} 测试完成`);
      console.log(`   退出码: ${code}`);
      console.log(`   耗时: ${(duration / 1000).toFixed(2)}秒`);
      console.log(`${'='.repeat(60)}\n`);
      
      resolve({
        suite: suite.name,
        exitCode: code,
        duration,
        passed: code === 0,
      });
    });
    
    proc.on('error', (error) => {
      clearTimeout(timeoutId);
      reject(error);
    });
  });
}

/**
 * 并行执行多个测试套件
 */
async function runTestSuitesParallel(suites) {
  const promises = suites.map(suite => runTestSuite(suite));
  return await Promise.allSettled(promises);
}

/**
 * 顺序执行多个测试套件
 */
async function runTestSuitesSequential(suites) {
  const results = [];
  
  // 按优先级排序
  const sortedSuites = [...suites].sort((a, b) => a.priority - b.priority);
  
  for (const suite of sortedSuites) {
    try {
      const result = await runTestSuite(suite);
      results.push({ status: 'fulfilled', value: result });
    } catch (error) {
      console.error(`❌ ${suite.name} 执行失败:`, error.message);
      results.push({ status: 'rejected', reason: error });
    }
  }
  
  return results;
}

/**
 * 读取单个测试套件的报告
 */
async function readTestReport(reportPath) {
  try {
    const fullPath = path.resolve(__dirname, reportPath);
    const content = await fs.readFile(fullPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.warn(`⚠️  无法读取报告: ${reportPath}`);
    return null;
  }
}

/**
 * 聚合所有测试报告
 */
async function aggregateTestReports(executionResults) {
  const reports = [];
  
  for (const result of executionResults) {
    if (result.status === 'fulfilled') {
      const { suite, exitCode, duration, passed } = result.value;
      const suiteConfig = CONFIG.testSuites.find(s => s.name === suite);
      
      if (suiteConfig) {
        const report = await readTestReport(suiteConfig.reportPath);
        reports.push({
          tool: suite,
          exitCode,
          duration,
          passed,
          ...report,
        });
      }
    } else {
      console.error(`❌ 测试套件执行失败:`, result.reason);
    }
  }
  
  // 计算总体统计
  const totalTests = reports.reduce((sum, r) => sum + (r.summary?.total || r.total || 0), 0);
  const totalPassed = reports.reduce((sum, r) => sum + (r.summary?.passed || r.passed || 0), 0);
  const totalFailed = reports.reduce((sum, r) => sum + (r.summary?.failed || r.failed || 0), 0);
  const totalSkipped = reports.reduce((sum, r) => sum + (r.summary?.skipped || r.skipped || 0), 0);
  
  const aggregated = {
    timestamp: new Date().toISOString(),
    summary: {
      total: totalTests,
      passed: totalPassed,
      failed: totalFailed,
      skipped: totalSkipped,
      passRate: totalTests > 0 ? `${(totalPassed / totalTests * 100).toFixed(2)}%` : '0%',
    },
    suites: reports,
    releaseGateStatus: totalFailed === 0 && totalPassed >= totalTests * 0.95 ? 'PASSED' : 'FAILED',
  };
  
  // 保存聚合报告
  await fs.writeFile(
    CONFIG.aggregatedReportPath,
    JSON.stringify(aggregated, null, 2)
  );
  
  return aggregated;
}

/**
 * 打印测试摘要
 */
function printTestSummary(aggregated) {
  console.log('\n' + '='.repeat(70));
  console.log('  📊 AIOPS 平台测试总览');
  console.log('='.repeat(70));
  console.log(`  时间: ${aggregated.timestamp}`);
  console.log('='.repeat(70));
  
  console.log('\n┌─────────────┬────────┬────────┬────────┬──────────┐');
  console.log('│ 测试工具     │ 总数   │ 通过   │ 失败   │ 通过率   │');
  console.log('├─────────────┼────────┼────────┼────────┼──────────┤');
  
  aggregated.suites.forEach(suite => {
    const total = suite.summary?.total || suite.total || 0;
    const passed = suite.summary?.passed || suite.passed || 0;
    const failed = suite.summary?.failed || suite.failed || 0;
    const passRate = suite.summary?.passRate || (total > 0 ? `${(passed / total * 100).toFixed(1)}%` : '0%');
    
    console.log(`│ ${suite.tool.padEnd(11)} │ ${String(total).padStart(6)} │ ${String(passed).padStart(6)} │ ${String(failed).padStart(6)} │ ${passRate.padStart(8)} │`);
  });
  
  console.log('├─────────────┼────────┼────────┼────────┼──────────┤');
  console.log(`│ 总计        │ ${String(aggregated.summary.total).padStart(6)} │ ${String(aggregated.summary.passed).padStart(6)} │ ${String(aggregated.summary.failed).padStart(6)} │ ${aggregated.summary.passRate.padStart(8)} │`);
  console.log('└─────────────┴────────┴────────┴────────┴──────────┘');
  
  console.log(`\n发布门禁状态: ${aggregated.releaseGateStatus === 'PASSED' ? '✅ 通过' : '❌ 不通过'}`);
  
  if (aggregated.releaseGateStatus === 'FAILED') {
    console.log('\n阻塞原因:');
    aggregated.suites.forEach(suite => {
      const failed = suite.summary?.failed || suite.failed || 0;
      if (failed > 0) {
        console.log(`  - ${suite.tool}: ${failed}个测试失败`);
      }
    });
  }
  
  console.log('\n' + '='.repeat(70) + '\n');
}

// ========== 主执行函数 ==========

async function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'sequential'; // sequential 或 parallel
  const filters = args.slice(1); // 筛选特定测试套件
  
  console.log('========================================');
  console.log('  AIOPS 统一测试编排器');
  console.log('  协调执行 5 大测试工具');
  console.log('========================================');
  console.log(`  执行模式: ${mode}`);
  console.log(`  筛选器: ${filters.length > 0 ? filters.join(', ') : '全部'}`);
  console.log('========================================\n');
  
  // 筛选测试套件
  let suitesToRun = CONFIG.testSuites;
  if (filters.length > 0) {
    suitesToRun = CONFIG.testSuites.filter(s => filters.includes(s.name));
  }
  
  console.log(`将执行 ${suitesToRun.length} 个测试套件:\n`);
  suitesToRun.forEach((s, i) => {
    console.log(`  ${i + 1}. ${s.name} (优先级: ${s.priority})`);
  });
  console.log('');
  
  // 执行测试
  let results;
  const startTime = Date.now();
  
  if (mode === 'parallel') {
    console.log('🚀 并行执行模式\n');
    results = await runTestSuitesParallel(suitesToRun);
  } else {
    console.log('🚀 顺序执行模式\n');
    results = await runTestSuitesSequential(suitesToRun);
  }
  
  const totalDuration = Date.now() - startTime;
  
  // 聚合报告
  console.log('\n📊 聚合测试报告...\n');
  const aggregated = await aggregateTestReports(results);
  
  // 打印摘要
  printTestSummary(aggregated);
  
  console.log(`总耗时: ${(totalDuration / 1000 / 60).toFixed(2)}分钟`);
  console.log(`聚合报告已保存: ${CONFIG.aggregatedReportPath}\n`);
  
  // 退出码
  process.exit(aggregated.releaseGateStatus === 'PASSED' ? 0 : 1);
}

// 执行
if (require.main === module) {
  main().catch(error => {
    console.error('❌ 测试编排器执行失败:', error);
    process.exit(1);
  });
}

module.exports = {
  runTestSuite,
  runTestSuitesSequential,
  runTestSuitesParallel,
  aggregateTestReports,
};
