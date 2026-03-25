/**
 * 修复 Cypress 测试文件中的语法错误
 * 主要修复孤立的 else 语句
 */
const fs = require('fs');
const path = require('path');

const files = [
  '53-charging-settle-finance-station.cy.js',
  '54-device-ingestion-ruleengine.cy.js',
  '55-ai-iotcloud-phm.cy.js',
  '56-energy-vpp-microgrid-pvessc.cy.js',
  '57-electrade-carbontrade-demandresp.cy.js',
  '58-energyeff-multienergy-safecontrol-deviceops.cy.js',
  '59-blockchain-digitaltwin.cy.js',
  '60-analytics-builder.cy.js',
  '61-content-portal-mgmt.cy.js',
  '62-tenant-account.cy.js',
  '63-workorder-workflow-developer.cy.js',
  '64-misc-platform.cy.js',
  '65-auth-error-profile.cy.js'
];

const e2eDir = path.join(__dirname, 'e2e');

// 修复模式：将破损的 C24 测试用例替换为正确版本
const brokenC24Pattern = /it\('\[C24\] 弹窗关闭操作', \(\) => \{[\s\S]*?cy\.get\('body'\)\.then\(\$b => \{ const \$cl[\s\S]*?\}\);[\s\n]*else cy\.get\('button:contains\("取消"\)'\)[\s\S]*?\}\);/g;

const fixedC24 = `it('[C24] 弹窗关闭操作', () => {
      cy.get('button:contains("新增"), button:contains("创建"), button:contains("添加")', { timeout: 8000 }).then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn.first()).click({ force: true });
          cy.get('.ant-modal, .ant-drawer', { timeout: 6000 }).then($m => {
            if ($m.length > 0) {
              cy.get('body').then($b => { 
                const $cl = $b.find('.ant-modal-close, .ant-drawer-close'); 
                if ($cl.length > 0) cy.wrap($cl.first()).click({ force: true }); 
                else cy.get('body').type('{esc}', { force: true }); 
              });
            }
          });
        }
      });
    });`;

// 另一个模式：移除孤立的 else 行
const orphanElsePattern = /\s+else cy\.get\('button:contains\("取消"\)'\)\.first\(\)\.click\(\{ force: true \}\);/g;

// 修复多余的闭合括号 });  
const extraClosingPattern = /\}\);\s*\}\);\s*\}\);\s*\}\);(\s*\}\);)+/g;

let fixedCount = 0;

for (const fileName of files) {
  const filePath = path.join(e2eDir, fileName);
  
  if (!fs.existsSync(filePath)) {
    console.log(`文件不存在: ${fileName}`);
    continue;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  const originalContent = content;
  
  // 尝试修复 C24 测试
  if (content.includes('[C24] 弹窗关闭操作')) {
    // 移除孤立的 else 语句
    content = content.replace(orphanElsePattern, '');
    
    // 修复多余的闭合括号
    content = content.replace(/\}\);\s*\}\);\s*\}\);\s*\}\);\s*\}\);/g, '});\n          }\n        });\n      }\n    });\n  });');
  }
  
  // 简单的方法：直接移除孤立 else 行
  const lines = content.split('\n');
  const fixedLines = [];
  let skipNext = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    
    // 检查是否是孤立的 else 行
    if (trimmed.startsWith('else cy.get(\'button:contains("取消")')) {
      console.log(`${fileName}: 移除孤立 else 行 ${i + 1}`);
      // 检查上一行是否以 }); 结尾 - 如果是则这是孤立的 else
      if (fixedLines.length > 0) {
        const prevLine = fixedLines[fixedLines.length - 1].trim();
        if (prevLine.endsWith('});') || prevLine.endsWith('});')) {
          // 跳过这行孤立的 else
          continue;
        }
      }
    }
    
    // 检查是否有多余的右括号
    if (trimmed === '});' && fixedLines.length > 1) {
      const prev1 = fixedLines[fixedLines.length - 1].trim();
      const prev2 = fixedLines[fixedLines.length - 2].trim();
      if (prev1 === '});' && prev2 === '});') {
        // 可能有过多的闭合括号，但保留这行让它自然处理
      }
    }
    
    fixedLines.push(line);
  }
  
  content = fixedLines.join('\n');
  
  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ 已修复: ${fileName}`);
    fixedCount++;
  } else {
    console.log(`⚠️ 未找到修复点: ${fileName}`);
  }
}

console.log(`\n总计修复 ${fixedCount} 个文件`);

// 验证语法
console.log('\n验证语法...');
const { execSync } = require('child_process');
let errorCount = 0;

for (const fileName of files) {
  const filePath = path.join(e2eDir, fileName);
  try {
    execSync(`node --check "${filePath}"`, { encoding: 'utf8' });
    console.log(`✅ ${fileName}`);
  } catch (e) {
    console.log(`❌ ${fileName}: 仍有语法错误`);
    errorCount++;
  }
}

console.log(`\n语法错误文件数: ${errorCount}`);
