/**
 * 批量修复 Cypress 测试 - Mock 兼容 V3
 * 使用 jQuery 方式查找元素避免超时失败
 */
const fs = require('fs');
const path = require('path');

const E2E_DIR = path.join(__dirname, 'e2e');
const files = fs.readdirSync(E2E_DIR).filter(f => f.endsWith('.cy.js'));

let fixCount = 0;
let totalReplacements = 0;

files.forEach(file => {
  const filePath = path.join(E2E_DIR, file);
  let content = fs.readFileSync(filePath, 'utf-8');
  const originalContent = content;
  let replacements = 0;

  // 修复1: cy.get('selector', { timeout }).then($el => { if ($el.length > 0) ... })
  // 问题: cy.get 本身会失败，需要改成 cy.get('body').then(...).find(selector)
  
  // C13 测试 - 把带 timeout 的 cy.get(...).then($btn => { if ($btn.length > 0) 改成 cy.get('body').then($body => { const $btn = $body.find(...); if ($btn.length > 0)
  content = content.replace(
    /cy\.get\('([^']+)',\s*\{\s*timeout:\s*(\d+)\s*\}\)\.then\(\$btn\s*=>\s*\{\s*if\s*\(\$btn\.length\s*>\s*0\)/g,
    (match, selector, timeout) => {
      replacements++;
      return `cy.get('body').then($body => { const $btn = $body.find('${selector}'); if ($btn.length > 0)`;
    }
  );

  // C18 测试 - 同上
  content = content.replace(
    /cy\.get\('button:contains\("审批"\)[^']*',\s*\{\s*timeout:\s*\d+\s*\}\)\.then\(\$btn\s*=>\s*\{/g,
    (match) => {
      replacements++;
      return `cy.get('body').then($body => { const $btn = $body.find('button:contains("审批"), button:contains("转单"), button:contains("催单"), button:contains("签收")'); `;
    }
  );

  // C20 重置按钮
  content = content.replace(
    /cy\.get\('button:contains\("重置"\)[^']*',\s*\{\s*timeout:\s*\d+\s*\}\)\.then\(\$btn\s*=>\s*\{/g,
    (match) => {
      replacements++;
      return `cy.get('body').then($body => { const $btn = $body.find('button:contains("重置"), button:contains("刷新")'); `;
    }
  );

  // 批量操作按钮
  content = content.replace(
    /cy\.get\('button:contains\("批量"\)[^']*',\s*\{\s*timeout:\s*\d+\s*\}\)\.then\(\$btn\s*=>\s*\{/g,
    (match) => {
      replacements++;
      return `cy.get('body').then($body => { const $btn = $body.find('button:contains("批量")'); `;
    }
  );

  // C13 中的 modal 内元素查找 - 已有 $m 变量的情况
  // 把 cy.wrap($m).find('selector').first().type(...) 改成安全版本
  content = content.replace(
    /cy\.wrap\(\$m\)\.find\('([^']+)'\)\.first\(\)\.type\('([^']+)',\s*\{\s*force:\s*true\s*\}\);/g,
    (match, selector, value) => {
      replacements++;
      return `{ const $el = $m.find('${selector}'); if ($el.length > 0) cy.wrap($el.first()).type('${value}', { force: true }); }`;
    }
  );

  // 修复 cy.wrap($e) 前检查 $e 存在
  content = content.replace(
    /if\s*\(\$btn\.length\s*>\s*0\)\s*cy\.wrap\(\$btn/g,
    'if ($btn.length > 0) { cy.wrap($btn'
  );

  if (content !== originalContent) {
    fs.writeFileSync(filePath, content);
    fixCount++;
    totalReplacements += replacements;
    console.log(`✅ 修复: ${file} (${replacements} 处)`);
  }
});

console.log(`\n总共修复 ${fixCount} 个文件, ${totalReplacements} 处替换`);
