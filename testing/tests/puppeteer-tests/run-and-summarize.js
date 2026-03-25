const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

process.chdir(path.join(__dirname));

try {
  console.log('Running tests...');
  const result = execSync(
    'npx jest tests/generated --testTimeout=30000 --forceExit --no-coverage --maxWorkers=4 --json',
    { encoding: 'utf8', maxBuffer: 100 * 1024 * 1024, timeout: 600000, stdio: ['pipe', 'pipe', 'pipe'] }
  );
  fs.writeFileSync('test-results.json', result);
} catch (e) {
  // Jest exits with code 1 when there are failures, but stdout still has JSON
  if (e.stdout) {
    fs.writeFileSync('test-results.json', e.stdout);
  }
}

try {
  const r = JSON.parse(fs.readFileSync('test-results.json', 'utf8'));
  const summary = [
    '=== TEST RESULTS ===',
    `Pass: ${r.numPassedTests} Fail: ${r.numFailedTests} Total: ${r.numTotalTests}`,
    `Suites Pass: ${r.numPassedTestSuites} Fail: ${r.numFailedTestSuites}`,
  ];

  if (r.numFailedTests > 0) {
    summary.push('\n--- FAILURES ---');
    r.testResults.filter(s => s.numFailingTests > 0).forEach(s => {
      const fname = s.testFilePath.split(/[/\\]/).pop();
      summary.push(`\nFAIL: ${fname} (${s.numFailingTests} failures)`);
      s.testResults
        .filter(t => t.status === 'failed')
        .forEach(t => {
          const msg = (t.failureMessages[0] || '').split('\n')[0].slice(0, 150);
          summary.push(`  - ${t.title}: ${msg}`);
        });
    });
  }

  summary.push('\n=== END ===');
  const text = summary.join('\n');
  fs.writeFileSync('test-summary.txt', text);
  console.log(text);
} catch (parseErr) {
  console.error('Failed to parse results:', parseErr.message);
}
