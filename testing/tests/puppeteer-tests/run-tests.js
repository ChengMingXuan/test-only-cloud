// 运行 Jest 测试并保存结果
const { execSync } = require('child_process');
const fs = require('fs');

process.chdir(__dirname);

try {
  console.log('Starting tests at', new Date().toLocaleTimeString());
  const result = execSync(
    'npx jest tests/generated --testTimeout=30000 --forceExit --no-coverage --maxWorkers=4 --json',
    { 
      encoding: 'utf8', 
      maxBuffer: 200 * 1024 * 1024,
      timeout: 1800000, // 30分钟超时
      stdio: ['pipe', 'pipe', 'pipe']
    }
  );
  fs.writeFileSync('test-results.json', result, 'utf8');
  console.log('Tests completed successfully');
} catch (e) {
  if (e.stdout) {
    fs.writeFileSync('test-results.json', e.stdout, 'utf8');
    console.log('Tests completed with failures');
  } else {
    console.error('Tests failed without output:', e.message);
    process.exit(1);
  }
}

// 解析结果
const r = JSON.parse(fs.readFileSync('test-results.json', 'utf8'));
console.log('=== RESULTS ===');
console.log(`Pass: ${r.numPassedTests} | Fail: ${r.numFailedTests} | Total: ${r.numTotalTests}`);
console.log(`Suites: ${r.numPassedTestSuites} pass / ${r.numFailedTestSuites} fail`);

if (r.numFailedTests > 0) {
  console.log('\n--- FAILURES ---');
  r.testResults.filter(s => s.numFailingTests > 0).forEach(s => {
    const fname = s.testFilePath.split(/[/\\]/).pop();
    console.log(`\n${fname} (${s.numFailingTests} failures):`);
    s.testResults
      .filter(t => t.status === 'failed')
      .forEach(t => {
        const msg = (t.failureMessages[0] || '').split('\n')[0].slice(0, 150);
        console.log(`  - ${t.title}`);
        console.log(`    ${msg}`);
      });
  });
}

// 保存摘要
const summary = {
  pass: r.numPassedTests,
  fail: r.numFailedTests,
  total: r.numTotalTests,
  failures: r.testResults
    .filter(s => s.numFailingTests > 0)
    .map(s => ({
      file: s.testFilePath.split(/[/\\]/).pop(),
      tests: s.testResults
        .filter(t => t.status === 'failed')
        .map(t => ({ name: t.title, msg: (t.failureMessages[0] || '').split('\n')[0].slice(0, 200) }))
    }))
};
fs.writeFileSync('test-summary.json', JSON.stringify(summary, null, 2), 'utf8');
console.log('\n=== END ===');
console.log('Finished at', new Date().toLocaleTimeString());
