const r = require('./test-results.json');
console.log('=== RESULTS ===');
console.log('Pass:', r.numPassedTests, 'Fail:', r.numFailedTests, 'Total:', r.numTotalTests);
console.log('Suites Pass:', r.numPassedTestSuites, 'Fail:', r.numFailedTestSuites);
r.testResults.filter(s => s.numFailingTests > 0).forEach(s => {
  console.log('\nFAIL:', s.testFilePath.split(/[/\\]/).pop());
  s.testResults.filter(t => t.status === 'failed').forEach(t => {
    const msg = (t.failureMessages[0] || '').split('\n')[0].slice(0, 120);
    console.log('  -', t.title, ':', msg);
  });
});
console.log('=== END ===');
