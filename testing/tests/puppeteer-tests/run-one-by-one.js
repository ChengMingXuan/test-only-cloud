/**
 * 逐个运行 Puppeteer 测试文件，结果保存到 JSON
 * 用法: node run-one-by-one.js [startIndex] [endIndex]
 */
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const genDir = path.join(__dirname, 'tests', 'generated');
const suppDir = path.join(genDir, 'supplement');

const mainFiles = fs.readdirSync(genDir)
  .filter(f => f.endsWith('.test.js'))
  .sort()
  .map(f => path.join('tests', 'generated', f));

const suppFiles = fs.existsSync(suppDir)
  ? fs.readdirSync(suppDir)
      .filter(f => f.endsWith('.test.js'))
      .sort()
      .map(f => path.join('tests', 'generated', 'supplement', f))
  : [];

const allFiles = [...mainFiles, ...suppFiles];

const startIdx = parseInt(process.argv[2]) || 0;
const endIdx = parseInt(process.argv[3]) || allFiles.length;

const results = [];
const resultFile = path.join(__dirname, 'one-by-one-results.json');

if (fs.existsSync(resultFile)) {
  try {
    const existing = JSON.parse(fs.readFileSync(resultFile, 'utf8'));
    results.push(...existing);
  } catch(e) {}
}

const alreadyTested = new Set(results.map(r => r.file));

console.log(`总共 ${allFiles.length} 个文件, 运行 [${startIdx}-${endIdx})`);
console.log(`已有结果: ${results.length} 个\n`);

for (let i = startIdx; i < endIdx && i < allFiles.length; i++) {
  const file = allFiles[i];
  const shortName = path.basename(file);
  
  if (alreadyTested.has(file)) {
    console.log(`[${i+1}/${allFiles.length}] SKIP ${shortName}`);
    continue;
  }

  process.stdout.write(`[${i+1}/${allFiles.length}] ${shortName} ... `);
  
  const jsonOutFile = path.join(__dirname, `_tmp_jest_result.json`);
  try { fs.unlinkSync(jsonOutFile); } catch(e) {}
  
  try {
    execFileSync('npx.cmd', [
      'jest', file,
      '--testTimeout=30000',
      '--forceExit',
      '--no-coverage',
      '--maxWorkers=1',
      '--json',
      '--outputFile=' + jsonOutFile
    ], {
      timeout: 180000,
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'pipe'],
      encoding: 'utf8'
    });
  } catch(e) {
    // Jest exit code != 0 但 outputFile 仍然写入
  }
  
  if (fs.existsSync(jsonOutFile)) {
    try {
      const json = JSON.parse(fs.readFileSync(jsonOutFile, 'utf8'));
      const passed = json.numPassedTests || 0;
      const failed = json.numFailedTests || 0;
      const total = json.numTotalTests || 0;
      const success = json.success;
      
      const failedNames = [];
      if (json.testResults) {
        for (const tr of json.testResults) {
          for (const tc of (tr.testResults || tr.assertionResults || [])) {
            if (tc.status === 'failed') {
              failedNames.push(tc.fullName || tc.title || 'unknown');
            }
          }
        }
      }
      
      results.push({ file, passed, failed, total, success, failedNames });
      
      if (success) {
        console.log(`PASS ${passed}/${total}`);
      } else {
        console.log(`FAIL ${passed}/${total} (${failed} failed)`);
        failedNames.forEach(n => console.log(`    X ${n}`));
      }
      
      try { fs.unlinkSync(jsonOutFile); } catch(e) {}
    } catch(e) {
      results.push({ file, passed: 0, failed: 50, total: 50, success: false, failedNames: ['json-parse-error'] });
      console.log('JSON-ERROR');
    }
  } else {
    results.push({ file, passed: 0, failed: 50, total: 50, success: false, failedNames: ['timeout-crash'] });
    console.log('TIMEOUT');
  }
  
  fs.writeFileSync(resultFile, JSON.stringify(results, null, 2));
}

// 汇总
const totalPassed = results.reduce((s, r) => s + r.passed, 0);
const totalFailed = results.reduce((s, r) => s + r.failed, 0);
const totalTests = results.reduce((s, r) => s + r.total, 0);
const failedFiles = results.filter(r => !r.success);

console.log('\n========== 汇总 ==========');
console.log(`文件: ${results.length}/${allFiles.length}`);
console.log(`用例: ${totalPassed}/${totalTests} 通过, ${totalFailed} 失败`);
console.log(`通过率: ${totalTests > 0 ? (totalPassed/totalTests*100).toFixed(1) : 0}%`);

if (failedFiles.length > 0) {
  console.log(`\n失败文件 (${failedFiles.length}):`);
  failedFiles.forEach(f => {
    console.log(`  ${path.basename(f.file)}: ${f.passed}/${f.total}`);
    f.failedNames.forEach(n => console.log(`    X ${n}`));
  });
}
