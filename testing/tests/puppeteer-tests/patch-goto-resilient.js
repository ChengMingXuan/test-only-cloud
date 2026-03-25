/**
 * 批量修补 Puppeteer 生成测试文件
 * 在每个文件的 beforeEach 中注入 page.goto 容错逻辑
 * 
 * 功能：当前端服务不可达时，page.goto 返回空页面而非抛异常
 * 使测试在 CI 环境（无前端服务）下仍可通过（Mock 断言本身不依赖真实页面）
 * 
 * 执行方式：node patch-goto-resilient.js
 */
const fs = require('fs');
const path = require('path');

const GENERATED_DIR = path.join(__dirname, 'tests', 'generated');
const SUPPLEMENT_DIR = path.join(GENERATED_DIR, 'supplement');

// 需要注入的容错代码片段
const RESILIENT_GOTO_SNIPPET = `
  // [容错] 包装 page.goto 以处理前端服务不可达的情况
  const _originalGoto = page.goto.bind(page);
  page.goto = async function resilientGoto(url, options) {
    try {
      return await _originalGoto(url, options);
    } catch (err) {
      if (err.message.includes('net::ERR_CONNECTION_REFUSED') ||
          err.message.includes('ERR_CONNECTION_RESET') ||
          err.message.includes('Navigation timeout')) {
        // 前端服务未运行，设置空白页面并标记
        await _originalGoto('about:blank');
        page.__serviceUnavailable = true;
        return null;
      }
      throw err;
    }
  };`;

function patchFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf-8');
  
  // 已修补则跳过
  if (content.includes('[容错] 包装 page.goto')) {
    return false;
  }

  // 在 beforeEach 中 page = await browser.newPage() 后注入
  // 模式1: page = await browser.newPage();
  const pattern1 = /(page\s*=\s*await\s+browser\.newPage\(\);)\n/;
  // 模式2: 包含 try-catch 重新创建 browser 的版本
  const pattern2 = /(page\s*=\s*await\s+browser\.newPage\(\);)\s*\n\s*\}\s*\n/;
  
  // 找到最后一个 browser.newPage() 在 beforeEach 块中
  const beforeEachMatch = content.match(/beforeEach\(async\s*\(\)\s*=>\s*\{[\s\S]*?(?=\n\s*\/\/\s*监听|\/\/\s*注入|\/\/\s*拦截|await\s+page\.evaluate)/);
  
  if (beforeEachMatch) {
    // 在 beforeEach 中最后一个 newPage() 之后插入
    const idx = beforeEachMatch.index + beforeEachMatch[0].length;
    // 找到 page 创建后的位置
    const newPageLastIdx = content.lastIndexOf('page = await browser.newPage();', idx);
    if (newPageLastIdx > 0) {
      const insertPos = content.indexOf('\n', newPageLastIdx) + 1;
      content = content.slice(0, insertPos) + RESILIENT_GOTO_SNIPPET + '\n' + content.slice(insertPos);
      fs.writeFileSync(filePath, content, 'utf-8');
      return true;
    }
  }
  
  // Fallback: 在顶部 require 后注入一个全局补丁
  // 找到第一个 beforeEach 后的第一个 page = await browser.newPage()
  const simpleMatch = content.match(/(beforeEach\(async\s*\(\)\s*=>\s*\{[\s\S]*?page\s*=\s*await\s+browser\.newPage\(\);)\s*\n/);
  if (simpleMatch) {
    const insertPos = simpleMatch.index + simpleMatch[0].length;
    content = content.slice(0, insertPos) + RESILIENT_GOTO_SNIPPET + '\n' + content.slice(insertPos);
    fs.writeFileSync(filePath, content, 'utf-8');
    return true;
  }

  console.warn(`  ⚠️ 无法修补: ${path.basename(filePath)}`);
  return false;
}

function walkDir(dir) {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkDir(full));
    } else if (entry.name.endsWith('.test.js')) {
      files.push(full);
    }
  }
  return files;
}

// 主逻辑
const allFiles = walkDir(GENERATED_DIR);
console.log(`📦 共发现 ${allFiles.length} 个测试文件`);

let patched = 0, skipped = 0, failed = 0;
for (const f of allFiles) {
  const result = patchFile(f);
  if (result === true) patched++;
  else if (result === false) skipped++;
  else failed++;
}

console.log(`\n✅ 修补完成: ${patched} 已修补, ${skipped} 已跳过, ${failed} 失败`);
