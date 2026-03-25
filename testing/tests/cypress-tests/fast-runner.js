/**
 * Cypress 快速测试运行器
 * 特性：进度实时输出、跳过UI加载、纯逻辑测试
 */
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

const BATCH_SIZE = 10;
const REPORTS_DIR = path.join(__dirname, 'reports');

// 确保reports目录存在
if (!fs.existsSync(REPORTS_DIR)) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

// 获取所有测试文件
const e2eDir = path.join(__dirname, 'e2e');
const testFiles = fs.readdirSync(e2eDir)
  .filter(f => f.endsWith('.cy.js'))
  .sort();

console.log('='.repeat(60));
console.log(`🚀 Cypress 快速测试运行器`);
console.log(`📁 测试文件: ${testFiles.length} 个`);
console.log(`📊 每 ${BATCH_SIZE} 个文件输出进度`);
console.log('='.repeat(60));
console.log();

let totalPassed = 0;
let totalFailed = 0;
let totalTests = 0;
let processedFiles = 0;
const startTime = Date.now();
const failedSpecs = [];

// 分批运行
async function runBatch(files, batchNum) {
  const batchStart = Date.now();
  
  for (const file of files) {
    processedFiles++;
    const specPath = path.join('e2e', file);
    
    try {
      // 运行单个spec
      const result = execSync(
        `npx cypress run --spec "${specPath}" --config-file cypress.fast.config.js --reporter json --quiet`,
        { 
          cwd: __dirname,
          timeout: 60000,
          encoding: 'utf8',
          stdio: ['pipe', 'pipe', 'pipe']
        }
      );
      
      // 解析结果
      const jsonMatch = result.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const json = JSON.parse(jsonMatch[0]);
        totalPassed += json.stats?.passes || 0;
        totalFailed += json.stats?.failures || 0;
        totalTests += json.stats?.tests || 0;
      }
    } catch (err) {
      // 测试失败也要统计
      if (err.stdout) {
        const jsonMatch = err.stdout.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          try {
            const json = JSON.parse(jsonMatch[0]);
            totalPassed += json.stats?.passes || 0;
            totalFailed += json.stats?.failures || 0;
            totalTests += json.stats?.tests || 0;
            if (json.stats?.failures > 0) {
              failedSpecs.push(file);
            }
          } catch {}
        }
      }
    }
    
    // 每N个文件输出进度
    if (processedFiles % BATCH_SIZE === 0) {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      const pct = ((processedFiles / testFiles.length) * 100).toFixed(1);
      console.log(`[${elapsed}s] 📊 文件: ${processedFiles}/${testFiles.length} (${pct}%) | ✅${totalPassed} ❌${totalFailed} | 总${totalTests}`);
    }
  }
}

// 主函数
async function main() {
  // 分批处理
  for (let i = 0; i < testFiles.length; i += BATCH_SIZE) {
    const batch = testFiles.slice(i, i + BATCH_SIZE);
    await runBatch(batch, Math.floor(i / BATCH_SIZE) + 1);
  }
  
  // 最终报告
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log();
  console.log('='.repeat(60));
  console.log(`📊 测试完成！耗时: ${elapsed}s`);
  console.log(`✅ 通过: ${totalPassed}`);
  console.log(`❌ 失败: ${totalFailed}`);
  console.log(`📝 总计: ${totalTests}`);
  console.log('='.repeat(60));
  
  if (failedSpecs.length > 0) {
    console.log(`\n❌ 失败的用例文件:`);
    failedSpecs.forEach(f => console.log(`  - ${f}`));
  }
  
  // 保存报告
  const report = {
    timestamp: new Date().toISOString(),
    duration: elapsed,
    totalFiles: testFiles.length,
    passed: totalPassed,
    failed: totalFailed,
    total: totalTests,
    failedSpecs
  };
  
  fs.writeFileSync(
    path.join(REPORTS_DIR, `fast-test-report-${Date.now()}.json`),
    JSON.stringify(report, null, 2)
  );
  
  console.log(`\n📄 报告已保存到 reports/ 目录`);
}

main().catch(console.error);
