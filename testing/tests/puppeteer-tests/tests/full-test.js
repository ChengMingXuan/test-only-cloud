/**
 * Puppeteer 全面性能监控测试
 * 包裹: 性能基准测试 + 视觉回归测试 + 全页面渲染检查 + 全页面性能批量
 * 生成: 完整性能分析报告 + 视觉差异报告 + 页面健康报告
 */

const fs = require('fs').promises;
const path = require('path');
const { spawnSync } = require('child_process');

const CONFIG = {
  reportDir: path.join(__dirname, '..', 'test-reports', 'puppeteer-report'),
};

/**
 * 创建报告目录
 */
async function ensureDirectories() {
  await fs.mkdir(CONFIG.reportDir, { recursive: true });
}

/**
 * 运行性能基准测试
 */
async function runPerformanceTest() {
  console.log('\n' + '='.repeat(50));
  console.log('🚀 开始: Puppeteer 性能基准测试');
  console.log('='.repeat(50));

  const result = spawnSync('node', [path.join(__dirname, 'performance-baseline.js')], {
    cwd: path.dirname(__dirname),
    stdio: 'inherit',
    shell: true,
  });

  return result.status === 0;
}

/**
 * 运行视觉回归测试
 */
async function runVisualTest() {
  console.log('\n' + '='.repeat(50));
  console.log('🎨 开始: Puppeteer 视觉回归测试');
  console.log('='.repeat(50));

  const result = spawnSync('node', [path.join(__dirname, 'visual-regression.js')], {
    cwd: path.dirname(__dirname),
    stdio: 'inherit',
    shell: true,
  });

  return result.status === 0;
}

/**
 * 运行全页面渲染健康检查（~300 页）
 */
async function runPagesRenderTest() {
  console.log('\n' + '='.repeat(50));
  console.log('🌐 开始: 全页面渲染健康检查');
  console.log('='.repeat(50));

  const result = spawnSync('node', [path.join(__dirname, 'pages-render.js')], {
    cwd: path.dirname(__dirname),
    stdio: 'inherit',
    shell: true,
    timeout: 50 * 60 * 1000, // 50 分钟超时（620 条路由扩展后）
  });

  return result.status === 0;
}

/**
 * 运行全页面性能批量测试（~65 个代表性页面）
 */
async function runPagesPerfBatchTest() {
  console.log('\n' + '='.repeat(50));
  console.log('⚡ 开始: 全页面性能批量测试');
  console.log('='.repeat(50));

  const result = spawnSync('node', [path.join(__dirname, 'pages-performance-batch.js')], {
    cwd: path.dirname(__dirname),
    stdio: 'inherit',
    shell: true,
    timeout: 30 * 60 * 1000, // 30 分钟超时
  });

  return result.status === 0;
}

/**
 * 合并四个JSON报告
 */
async function mergeReports() {
  console.log('\n' + '='.repeat(50));
  console.log('📊 生成综合测试报告');
  console.log('='.repeat(50));

  try {
    const files = {
      summary:      path.join(CONFIG.reportDir, 'summary.json'),
      visualSummary:path.join(CONFIG.reportDir, 'visual-summary.json'),
      pagesRender:  path.join(CONFIG.reportDir, 'pages-render-summary.json'),
      pagesPerfBatch: path.join(CONFIG.reportDir, 'pages-performance-batch-summary.json'),
    };

    const readJson = async (filePath) => {
      try {
        return JSON.parse(await fs.readFile(filePath, 'utf-8'));
      } catch (e) {
        console.warn(`⚠️  报告文件不存在: ${filePath}`);
        return {};
      }
    };

    const [performanceReport, visualReport, pagesRenderReport, pagesPerfBatchReport] =
      await Promise.all([readJson(files.summary), readJson(files.visualSummary), readJson(files.pagesRender), readJson(files.pagesPerfBatch)]);

    const merged = {
      tool: 'puppeteer-comprehensive',
      timestamp: new Date().toISOString(),
      summary: {
        performance: {
          total: performanceReport.total || 0,
          passed: performanceReport.passed || 0,
          failed: performanceReport.failed || 0,
          passRate: performanceReport.passRate || 'N/A',
        },
        visual: {
          total: visualReport.total || 0,
          passed: visualReport.passed || 0,
          failed: visualReport.failed || 0,
          passRate: visualReport.passRate || 'N/A',
        },
        pagesRender: {
          total: pagesRenderReport.total || 0,
          passed: pagesRenderReport.passed || 0,
          failed: pagesRenderReport.failed || 0,
          passRate: pagesRenderReport.passRate || 'N/A',
          skipped: pagesRenderReport.skipped || false,
        },
        pagesPerfBatch: {
          total: pagesPerfBatchReport.total || 0,
          passed: pagesPerfBatchReport.passed || 0,
          failed: pagesPerfBatchReport.failed || 0,
          passRate: pagesPerfBatchReport.passRate || 'N/A',
          p0PassRate: pagesPerfBatchReport.p0PassRate || 'N/A',
          skipped: pagesPerfBatchReport.skipped || false,
        },
      },
      detailedResults: {
        performance: performanceReport.results || [],
        visual: visualReport.results || [],
        pagesRender: pagesRenderReport.results || [],
        pagesPerfBatch: pagesPerfBatchReport.results || [],
      },
    };

    const mergedPath = path.join(CONFIG.reportDir, 'comprehensive-report.json');
    await fs.writeFile(mergedPath, JSON.stringify(merged, null, 2));

    return { mergedPath, report: merged };
  } catch (error) {
    console.error('❌ 报告合并失败:', error);
    throw error;
  }
}

/**
 * 生成HTML报告
 */
async function generateHTMLReport(report) {
  const performanceStats = report.summary.performance;
  const visualStats = report.summary.visual;
  const pagesRenderStats = report.summary.pagesRender || { total: 0, passed: 0, failed: 0, passRate: 'N/A' };
  const pagesPerfStats = report.summary.pagesPerfBatch || { total: 0, passed: 0, failed: 0, passRate: 'N/A', p0PassRate: 'N/A' };

  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Puppeteer 性能监控报告</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh; padding: 40px 20px;
    }
    .container { max-width: 1400px; margin: 0 auto; }
    header { text-align: center; color: white; margin-bottom: 40px; }
    header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    header p { font-size: 1.1em; opacity: 0.9; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 40px; }
    .card { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card h2 { color: #333; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
    .card-icon { font-size: 1.5em; }
    .stat { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee; }
    .stat:last-child { border-bottom: none; }
    .stat-label { color: #666; font-weight: 500; }
    .stat-value { font-size: 1.2em; font-weight: bold; color: #333; }
    .stat-value.passed { color: #22c55e; }
    .stat-value.failed { color: #ef4444; }
    .pass-rate { font-size: 2em; font-weight: bold; text-align: center; padding: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; margin-top: 16px; }
    .pass-rate.excellent { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
    .pass-rate.good { background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); }
    .pass-rate.warning { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
    .details { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 24px; }
    .details h3 { color: #333; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }
    .test-item { padding: 12px; margin: 8px 0; background: #f5f5f5; border-left: 4px solid #667eea; border-radius: 4px; }
    .test-item.passed { background: #f0fdf4; border-left-color: #22c55e; }
    .test-item.failed { background: #fef2f2; border-left-color: #ef4444; }
    .test-name { font-weight: bold; color: #333; margin-bottom: 4px; }
    .test-message { color: #666; font-size: 0.9em; }
    footer { text-align: center; color: white; margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
    @media (max-width: 768px) { header h1 { font-size: 1.8em; } .summary-grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🚀 Puppeteer 全面测试报告</h1>
      <p>AIOPS 平台 — 性能基准 + 视觉回归 + 全页面渲染 + 批量性能 | ${new Date(report.timestamp).toLocaleString('zh-CN')}</p>
    </header>

    <div class="summary-grid">
      <div class="card">
        <h2><span class="card-icon">📊</span> 性能基准测试</h2>
        <div class="stat"><span class="stat-label">总测试数</span><span class="stat-value">${performanceStats.total}</span></div>
        <div class="stat"><span class="stat-label">通过</span><span class="stat-value passed">${performanceStats.passed} ✓</span></div>
        <div class="stat"><span class="stat-label">失败</span><span class="stat-value failed">${performanceStats.failed}</span></div>
        <div class="pass-rate ${getPassRateClass(performanceStats.passRate)}">${performanceStats.passRate}</div>
      </div>
      <div class="card">
        <h2><span class="card-icon">🎨</span> 视觉回归测试</h2>
        <div class="stat"><span class="stat-label">总测试数</span><span class="stat-value">${visualStats.total}</span></div>
        <div class="stat"><span class="stat-label">通过</span><span class="stat-value passed">${visualStats.passed} ✓</span></div>
        <div class="stat"><span class="stat-label">失败</span><span class="stat-value failed">${visualStats.failed}</span></div>
        <div class="pass-rate ${getPassRateClass(visualStats.passRate)}">${visualStats.passRate}</div>
      </div>
      <div class="card">
        <h2><span class="card-icon">🌐</span> 全页面渲染检查</h2>
        <div class="stat"><span class="stat-label">覆盖页面数</span><span class="stat-value">${pagesRenderStats.total}</span></div>
        <div class="stat"><span class="stat-label">渲染正常</span><span class="stat-value passed">${pagesRenderStats.passed} ✓</span></div>
        <div class="stat"><span class="stat-label">渲染异常</span><span class="stat-value failed">${pagesRenderStats.failed}</span></div>
        <div class="pass-rate ${getPassRateClass(pagesRenderStats.passRate)}">${pagesRenderStats.passRate}</div>
      </div>
      <div class="card">
        <h2><span class="card-icon">⚡</span> 批量性能测试</h2>
        <div class="stat"><span class="stat-label">代表性页面</span><span class="stat-value">${pagesPerfStats.total}</span></div>
        <div class="stat"><span class="stat-label">性能达标</span><span class="stat-value passed">${pagesPerfStats.passed} ✓</span></div>
        <div class="stat"><span class="stat-label">性能超标</span><span class="stat-value failed">${pagesPerfStats.failed}</span></div>
        <div class="stat"><span class="stat-label">P0关键通过率</span><span class="stat-value">${pagesPerfStats.p0PassRate}</span></div>
        <div class="pass-rate ${getPassRateClass(pagesPerfStats.passRate)}">${pagesPerfStats.passRate}</div>
      </div>
    </div>

    <div class="details">
      <h3>📈 性能基准测试详情</h3>
      ${generateTestItems(report.detailedResults.performance)}
    </div>
    <div class="details">
      <h3>🎨 视觉回归测试详情</h3>
      ${generateTestItems(report.detailedResults.visual)}
    </div>
    <div class="details">
      <h3>🌐 全页面渲染检查（失败页面）</h3>
      ${generateTestItems((report.detailedResults.pagesRender || []).filter(r => !r.passed))}
    </div>
    <div class="details">
      <h3>⚡ 批量性能测试（性能超标页面）</h3>
      ${generateTestItems((report.detailedResults.pagesPerfBatch || []).filter(r => !r.passed))}
    </div>

    <footer><p>AIOPS 平台自动化测试系统 | Puppeteer 全面测试套件</p></footer>
  </div>
</body>
</html>`;

  const htmlPath = path.join(CONFIG.reportDir, 'index.html');
  await fs.writeFile(htmlPath, html);
  console.log(`✅ HTML报告已生成: ${htmlPath}`);
  return htmlPath;
}

/**
 * 生成测试项HTML
 */
function generateTestItems(results) {
  if (!results || results.length === 0) {
    return '<div class="test-item passed">✓ 无失败项</div>';
  }
  return results.map(item => {
    const status = item.passed ? 'passed' : 'failed';
    const icon = item.passed ? '✓' : '✗';
    const name = item.pageName || item.name || '未知';
    const msg = Array.isArray(item.failures) ? item.failures.join('; ') : (item.warnings || []).join('; ');
    return `<div class="test-item ${status}">
      <div class="test-name">${icon} ${name}${item.path ? ' <small style="font-weight:normal;color:#888">' + item.path + '</small>' : ''}</div>
      ${msg ? `<div class="test-message">${msg}</div>` : ''}
    </div>`;
  }).join('');
}

/**
 * 获取通过率样式
 */
function getPassRateClass(passRate) {
  const rate = parseFloat(passRate);
  if (rate >= 95) return 'excellent';
  if (rate >= 80) return 'good';
  return 'warning';
}

/**
 * 生成测试摘要
 */
async function generateSummary(report) {
  const s = report.summary;
  const perf = s.performance;
  const vis  = s.visual;
  const pRender = s.pagesRender || { total: 0, passed: 0, failed: 0, passRate: 'N/A', skipped: false };
  const pPerf   = s.pagesPerfBatch || { total: 0, passed: 0, failed: 0, passRate: 'N/A', p0PassRate: 'N/A', skipped: false };

  const totalTests  = perf.total + vis.total + pRender.total + pPerf.total;
  const totalPassed = perf.passed + vis.passed + pRender.passed + pPerf.passed;
  const totalFailed = perf.failed + vis.failed + pRender.failed + pPerf.failed;
  const overallRate = totalTests > 0 ? (totalPassed / totalTests * 100).toFixed(2) : '100.00';

  const summary = `
════════════════════════════════════════════════════════════════════
  Puppeteer 全面测试 - 测试总结
════════════════════════════════════════════════════════════════════

📊 性能基准测试 (4个核心场景):
  • 总计: ${perf.total}  通过: ${perf.passed} ✓  失败: ${perf.failed} ✗  通过率: ${perf.passRate}

🎨 视觉回归测试 (4个视觉场景):
  • 总计: ${vis.total}  通过: ${vis.passed} ✓  失败: ${vis.failed} ✗  通过率: ${vis.passRate}

🌐 全页面渲染健康检查 (~300页全覆盖):
  • 总计: ${pRender.total}${pRender.skipped ? ' (服务离线-跳过)' : ''}
  • 通过: ${pRender.passed} ✓  失败: ${pRender.failed} ✗  通过率: ${pRender.passRate}

⚡ 全页面性能批量测试 (~65代表性页面):
  • 总计: ${pPerf.total}${pPerf.skipped ? ' (服务离线-跳过)' : ''}
  • 通过: ${pPerf.passed} ✓  失败: ${pPerf.failed} ✗  通过率: ${pPerf.passRate}
  • P0关键页面通过率: ${pPerf.p0PassRate}

📈 综合统计:
  • 总体通过率: ${overallRate}%  总测试数: ${totalTests}
  • 通过: ${totalPassed} ✓  失败: ${totalFailed} ✗

${totalFailed === 0 ? '✅ 全部测试通过! 平台健康状态良好!' : '⚠️  存在失败测试，请查阅 comprehensive-report.json 详情。'}

📁 报告位置:
  • JSON报告: ${path.join(CONFIG.reportDir, 'comprehensive-report.json')}
  • HTML报告: ${path.join(CONFIG.reportDir, 'index.html')}
  • 截图: ${path.join(CONFIG.reportDir, 'screenshots')}

════════════════════════════════════════════════════════════════════
`;

  console.log(summary);
  const summaryPath = path.join(CONFIG.reportDir, 'SUMMARY.txt');
  await fs.writeFile(summaryPath, summary);
  return summaryPath;
}

/**
 * 主执行函数
 */
async function main() {
  const mode = process.env.PUPPETEER_MODE || 'full';
  console.log('\n');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║  Puppeteer 全面测试套件  (4个子套件)                        ║');
  console.log('║  性能基准 + 视觉回归 + 全页渲染检查 + 批量性能               ║');
  console.log(`║  模式: ${mode.padEnd(52)}║`);
  console.log('╚════════════════════════════════════════════════════════════╝');

  await ensureDirectories();

  const startTime = Date.now();

  try {
    // 第一步: 性能基准测试
    const performancePass = await runPerformanceTest();

    // 第二步: 视觉回归测试
    const visualPass = await runVisualTest();

    // 第三步: 全页面渲染健康检查（mode=quick 时跳过）
    let pagesRenderPass = true;
    if (mode !== 'quick') {
      pagesRenderPass = await runPagesRenderTest();
    } else {
      console.log('\n⏭️  快速模式：跳过全页面渲染检查');
    }

    // 第四步: 全页面性能批量测试（mode=quick 时跳过）
    let pagesPerfPass = true;
    if (mode !== 'quick') {
      pagesPerfPass = await runPagesPerfBatchTest();
    } else {
      console.log('⏭️  快速模式：跳过全页面性能批量测试');
    }

    // 第五步: 合并报告
    const { report } = await mergeReports();

    // 第六步: 生成HTML报告
    await generateHTMLReport(report);

    // 第七步: 生成测试摘要
    await generateSummary(report);

    const duration = ((Date.now() - startTime) / 1000).toFixed(2);

    console.log('\n' + '='.repeat(60));
    console.log('✅ 全面测试已完成! 所有报告已生成。');
    console.log(`⏱️  总耗时: ${duration}秒`);
    console.log('='.repeat(60));

    // 核心套件全绿才算通过（全页面渲染/性能批量允许部分失败不阻断）
    const allPassed = performancePass && visualPass;
    process.exit(allPassed ? 0 : 1);
  } catch (error) {
    console.error('\n❌ 测试执行失败:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { runPerformanceTest, runVisualTest, runPagesRenderTest, runPagesPerfBatchTest, mergeReports, generateHTMLReport };

