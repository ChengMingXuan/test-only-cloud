/**
 * 批量修复分页切换测试用例的语法错误
 */
const fs = require('fs');
const path = require('path');

const files = [
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

// 错误的分页切换模式（被截断的版本）
const brokenPattern = `    it('[C08] 分页切换', () => {
      cy.get('.ant-pagination', { timeout: 5000 }).then($p => {
        if ($p.length > 0) { cy.get('body').then($body => { const $nx = $body.find('.ant-pagination-next:not(.ant-pagination-disabled)'); if ($nx.length > 0) cy.wrap($nx.first()).click({ force: true }); }
      });
    });`;

// 正确的分页切换模式
const fixedPattern = `    it('[C08] 分页切换', () => {
      cy.get('.ant-pagination', { timeout: 5000 }).then($p => {
        if ($p.length > 0) { 
          cy.get('body').then($body => { 
            const $nx = $body.find('.ant-pagination-next:not(.ant-pagination-disabled)'); 
            if ($nx.length > 0) cy.wrap($nx.first()).click({ force: true }); 
          }); 
        }
      });
    });`;

let fixedCount = 0;

for (const fileName of files) {
  const filePath = path.join(e2eDir, fileName);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ 文件不存在: ${fileName}`);
    continue;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  if (content.includes(brokenPattern)) {
    content = content.replace(brokenPattern, fixedPattern);
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ ${fileName}: 修复分页切换`);
    fixedCount++;
  } else {
    console.log(`⚠️ ${fileName}: 未找到匹配模式`);
  }
}

console.log(`\n📊 修复了 ${fixedCount} 个文件`);

// 验证
const { execSync } = require('child_process');
console.log('\n🔍 验证语法...');
let errors = 0;
for (const fileName of files) {
  const filePath = path.join(e2eDir, fileName);
  try {
    execSync(`node --check "${filePath}"`, { encoding: 'utf8' });
    console.log(`✅ ${fileName}`);
  } catch (e) {
    console.log(`❌ ${fileName}`);
    errors++;
  }
}
console.log(`\n❌ 错误文件数: ${errors}`);
