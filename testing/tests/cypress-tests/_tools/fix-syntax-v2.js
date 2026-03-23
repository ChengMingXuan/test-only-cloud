/**
 * 修复 Cypress 测试文件 52-65 的语法错误
 * 主要问题：分页切换测试用例 [C08] 的括号匹配错误
 */
const fs = require('fs');
const path = require('path');

const files = [
  '52-security-full.cy.js',
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

// 使用简单字符串替换，避免复杂正则表达式

let fixedCount = 0;
let totalFixes = 0;

for (const fileName of files) {
  const filePath = path.join(e2eDir, fileName);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ 文件不存在: ${fileName}`);
    continue;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  const originalContent = content;
  let fileFixCount = 0;
  
  // 修复分页切换错误
  if (content.includes('}); }); }')) {
    content = content.replace(/\}\); \}\); \}/g, '}); }');
    fileFixCount++;
  }
  
  // 修复内联的 `}); else` 错误模式
  // 例如：}); else cy.get('button:contains("取消")').first().click({ force: true }); }
  // 应该变成：}); }
  if (content.includes('}); else cy.get(\'button:contains("取消")')) {
    content = content.replace(/\}\); else cy\.get\('button:contains\("取消"\)'\)\.first\(\)\.click\(\{ force: true \}\); \}/g, '}); }');
    fileFixCount++;
    console.log(`  - ${fileName}: 修复内联 else`);
  }
  
  // 移除孤立的 else 行
  const lines = content.split('\n');
  const fixedLines = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    
    // 孤立的 else 行 - 上一行以 }); 结尾
    if (trimmed.startsWith('else cy.get(\'button:contains("取消")')) {
      if (fixedLines.length > 0) {
        const prevTrimmed = fixedLines[fixedLines.length - 1].trim();
        if (prevTrimmed.endsWith('});') || prevTrimmed.endsWith('});')) {
          console.log(`  - ${fileName}:${i+1} 移除孤立 else`);
          fileFixCount++;
          continue; // 跳过此行
        }
      }
    }
    
    fixedLines.push(line);
  }
  
  content = fixedLines.join('\n');
  
  // 修复多余的闭合括号组合
  // 找到类似 `}); }\n      });\n    });` 应该变成 `});\n      });\n    });`
  content = content.replace(/\}\); \}\n(\s+\}\);)/g, '});\n$1');
  
  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ ${fileName}: ${fileFixCount} 处修复`);
    fixedCount++;
    totalFixes += fileFixCount;
  }
}

console.log(`\n📊 统计: ${fixedCount}/${files.length} 文件修复, 共 ${totalFixes} 处`);

// 验证语法
console.log('\n🔍 验证语法...');
const { execSync } = require('child_process');
let errorFiles = [];

for (const fileName of files) {
  const filePath = path.join(e2eDir, fileName);
  if (!fs.existsSync(filePath)) continue;
  
  try {
    execSync(`node --check "${filePath}"`, { encoding: 'utf8' });
    console.log(`✅ ${fileName}`);
  } catch (e) {
    const errMatch = e.message.match(/:(\d+)\n/);
    const errLine = errMatch ? errMatch[1] : '?';
    console.log(`❌ ${fileName}: 第 ${errLine} 行语法错误`);
    errorFiles.push({ name: fileName, line: errLine });
  }
}

if (errorFiles.length > 0) {
  console.log(`\n❌ 仍有 ${errorFiles.length} 个文件有语法错误`);
  
  // 读取第一个错误文件的问题行
  const first = errorFiles[0];
  const filePath = path.join(e2eDir, first.name);
  const lines = fs.readFileSync(filePath, 'utf8').split('\n');
  const lineNum = parseInt(first.line);
  if (lineNum > 0 && lineNum <= lines.length) {
    console.log(`\n${first.name} 行 ${lineNum}:`);
    // 显示前后各 2 行
    for (let i = Math.max(0, lineNum - 3); i <= Math.min(lines.length - 1, lineNum + 1); i++) {
      const marker = i === lineNum - 1 ? '>>>' : '   ';
      console.log(`${marker} ${i+1}: ${lines[i]}`);
    }
  }
} else {
  console.log(`\n✅ 所有文件语法正确！`);
}
