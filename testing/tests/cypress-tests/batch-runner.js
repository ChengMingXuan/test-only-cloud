#!/usr/bin/env node
/**
 * Cypress 批量测试运行器
 * 每 10 个 spec 文件输出一次进度
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const E2E_DIR = path.join(__dirname, 'e2e');
const REPORTS_DIR = path.join(__dirname, 'reports');

// 确保目录存在
if (!fs.existsSync(REPORTS_DIR)) fs.mkdirSync(REPORTS_DIR, { recursive: true });

// 获取所有测试文件
const specs = fs.readdirSync(E2E_DIR)
  .filter(f => f.endsWith('.cy.js'))
  .sort();

console.log('='.repeat(60));
console.log(`🚀 Cypress 批量测试运行器`);
console.log(`📁 测试文件: ${specs.length} 个`);
console.log(`⏱️  开始时间: ${new Date().toLocaleString('zh-CN')}`);
console.log('='.repeat(60));

let passed = 0, failed = 0, total = 0;
const startTime = Date.now();
const failedSpecs = [];

for (let i = 0; i < specs.length; i++) {
  const spec = specs[i];
  const specPath = `e2e/${spec}`;
  
  try {
    const output = execSync(
      `npx cypress run --config-file cypress.fast.config.js --spec "${specPath}" --quiet`,
      { cwd: __dirname, timeout: 120000, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }
    );
    
    // 解析通过/失败数
    const passMatch = output.match(/Passing:\s*(\d+)/);
    const failMatch = output.match(/Failing:\s*(\d+)/);
    if (passMatch) passed += parseInt(passMatch[1]);
    if (failMatch) failed += parseInt(failMatch[1]);
    total += (parseInt(passMatch?.[1] || 0) + parseInt(failMatch?.[1] || 0));
    
  } catch (err) {
    // 测试失败
    if (err.stdout) {
      const passMatch = err.stdout.match(/Passing:\s*(\d+)/);
      const failMatch = err.stdout.match(/Failing:\s*(\d+)/);
      if (passMatch) passed += parseInt(passMatch[1]);
      if (failMatch) {
        const f = parseInt(failMatch[1]);
        failed += f;
        if (f > 0) failedSpecs.push(spec);
      }
      total += (parseInt(passMatch?.[1] || 0) + parseInt(failMatch?.[1] || 0));
    }
  }
  
  // 每 10 个文件输出进度
  if ((i + 1) % 10 === 0 || i === specs.length - 1) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(0);
    const pct = (((i + 1) / specs.length) * 100).toFixed(1);
    console.log(`[${elapsed}s] 📊 文件 ${i+1}/${specs.length} (${pct}%) | ✅${passed} ❌${failed} | 总${total}`);
  }
}

// 最终报告
const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
console.log('\n' + '='.repeat(60));
console.log(`📊 测试完成！耗时: ${elapsed}s`);
console.log(`✅ 通过: ${passed}`);
console.log(`❌ 失败: ${failed}`);
console.log(`📝 总计: ${total}`);
console.log('='.repeat(60));

if (failedSpecs.length > 0) {
  console.log(`\n❌ 失败的文件 (${failedSpecs.length}):`);
  failedSpecs.slice(0, 20).forEach(f => console.log(`  - ${f}`));
  if (failedSpecs.length > 20) console.log(`  ... 还有 ${failedSpecs.length - 20} 个`);
}

// 保存报告
const report = {
  timestamp: new Date().toISOString(),
  duration: `${elapsed}s`,
  totalFiles: specs.length,
  passed, failed, total,
  passRate: total > 0 ? ((passed / total) * 100).toFixed(2) + '%' : 'N/A',
  failedSpecs
};

const reportPath = path.join(REPORTS_DIR, `batch-report-${Date.now()}.json`);
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`\n📄 报告已保存: ${reportPath}`);

// 退出码
process.exit(failed > 0 ? 1 : 0);
