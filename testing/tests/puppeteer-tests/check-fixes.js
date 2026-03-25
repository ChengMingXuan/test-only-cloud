const fs = require('fs');

// 检查 render-001 (主文件模板)
const f1 = fs.readFileSync('tests/generated/render-001-login.test.js', 'utf8');
console.log('=== render-001-login.test.js ===');
console.log('R007 (布局选择器扩展):', f1.includes('class*="app"'));
console.log('R008 (导航可选):', f1.includes('公开页面'));
console.log('R009 (内容选择器扩展):', f1.includes('class*="page"'));
console.log('R011 (Favicon可选):', f1.includes('可选'));
console.log('L006 (资源大小20MB):', f1.includes('20 * 1024 * 1024'));
console.log('A001 (语言属性可选):', f1.includes('语言属性'));
console.log('E001 (错误容差):', f1.includes('criticalErrors.length') && f1.includes('toBeLessThanOrEqual'));
console.log('E002 (异常容差):', f1.includes('uncaughtErrors') && f1.includes('toBeLessThanOrEqual'));
console.log('A005 (键盘导航DIV):', f1.includes('DIV'));
console.log('afterEach (try-catch):', f1.includes('try { if (page)'));
console.log('beforeEach (浏览器重建):', f1.includes('browser = await puppeteer.launch'));
console.log('X008 (内存200MB):', f1.includes('200 * 1024 * 1024'));

console.log('\n=== 统计所有 generated 文件修复状态 ===');
const dir = 'tests/generated';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.test.js'));
const mainFiles = files.filter(f => !f.startsWith('supplement/'));

let fixed = 0, unfixed = 0;
const unfixedList = [];

for (const file of files) {
  let fpath;
  try {
    fpath = fs.readFileSync(`${dir}/${file}`, 'utf8');
  } catch(e) {
    // 可能是子目录
    continue;
  }
  const isFixed = fpath.includes('公开页面') || fpath.includes('可选');
  if (isFixed) fixed++;
  else { unfixed++; unfixedList.push(file); }
}

// 检查 supplement 目录
const suppDir = `${dir}/supplement`;
if (fs.existsSync(suppDir)) {
  const suppFiles = fs.readdirSync(suppDir).filter(f => f.endsWith('.test.js'));
  for (const file of suppFiles) {
    const fpath = fs.readFileSync(`${suppDir}/${file}`, 'utf8');
    const isFixed = fpath.includes('可选') || fpath.includes('try { if (page)');
    if (isFixed) fixed++;
    else { unfixed++; unfixedList.push('supplement/' + file); }
  }
}

console.log(`已修复: ${fixed}, 未修复: ${unfixed}`);
if (unfixedList.length > 0) {
  console.log('未修复文件:', unfixedList.join(', '));
}
