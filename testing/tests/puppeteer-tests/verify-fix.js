const fs = require('fs');
const path = require('path');

const BASE_DIR = path.join(__dirname, 'tests', 'generated');

function findTestFiles(dir) {
  let results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(findTestFiles(fullPath));
    } else if (entry.name.endsWith('.test.js')) {
      results.push(fullPath);
    }
  }
  return results;
}

const files = findTestFiles(BASE_DIR);
let r6ok = 0, r6bad = 0, a3ok = 0, a3bad = 0;

files.forEach(fp => {
  const c = fs.readFileSync(fp, 'utf8');
  if (c.includes("page.$$('script[src], script:not(:empty)')")) r6ok++;
  if (c.includes("page.$$('script[src]')")) r6bad++;
  if (c.includes('toBeLessThanOrEqual(200)')) a3ok++;
  if (c.includes('inputsWithoutLabel).toBeLessThanOrEqual(10)')) a3bad++;
});

const result = `R006已修复:${r6ok} R006未修复:${r6bad} A003已修复:${a3ok} A003未修复:${a3bad} 总文件:${files.length}`;
fs.writeFileSync(path.join(__dirname, 'verify.txt'), result);
console.log(result);
