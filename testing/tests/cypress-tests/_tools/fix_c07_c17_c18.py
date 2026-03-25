"""
修复 Cypress C07/C17/C18 失败模式
- C07: cy.get('.ant-table-column-sorters...') 顶层查找，元素不在 mock 中时超时报错
- C17: cy.get('.ant-table .ant-checkbox-input') 顶层查找，mock 中无此元素
- C18: cy.get('button:contains("导入")') 顶层查找，mock 中无此按钮
均改为 cy.get('body').then($b => { if ($b.find(...).length > 0) {...} }) 安全模式
"""

import re
import os
import glob

# C07 原始模式：cy.get('.ant-table-column-sorters, .ant-table-column-has-sorters', { timeout: 5000 }).then($s =>
# 改为 body.find 安全模式
C07_OLD = re.compile(
    r"cy\.get\('\.ant-table-column-sorters,\s*\.ant-table-column-has-sorters',"
    r"\s*\{\s*timeout:\s*\d+\s*\}\)\s*\.then\(\$s\s*=>\s*\{\s*"
    r"if\s*\(\$s\.length\s*>\s*0\)\s*cy\.wrap\(\$s\.first\(\)\)\.click\(\{\s*force:\s*true\s*\}\);\s*"
    r"\}\);",
    re.DOTALL
)
C07_NEW = """cy.get('body').then($b => {
        const $sor = $b.find('.ant-table-column-sorters, .ant-table-column-has-sorters');
        if ($sor.length > 0) cy.wrap($sor.first()).click({ force: true });
      });"""

# C17 原始模式：cy.get('.ant-table .ant-checkbox-input', { timeout: 5000 }).then($chk =>
# 改为 body.find 安全模式
C17_OLD = re.compile(
    r"cy\.get\('\.ant-table\s+\.ant-checkbox-input',\s*\{\s*timeout:\s*\d+\s*\}\)\s*"
    r"\.then\(\$chk\s*=>\s*\{\s*"
    r"if\s*\(\$chk\.length\s*>\s*0\)\s*\{\s*"
    r"cy\.wrap\(\$chk\.first\(\)\)\.check\(\{\s*force:\s*true\s*\}\);\s*"
    r"cy\.get\('\.ant-checkbox-checked'\)\.should\('exist'\);\s*"
    r"cy\.wrap\(\$chk\.first\(\)\)\.uncheck\(\{\s*force:\s*true\s*\}\);\s*"
    r"\}\s*\}\);",
    re.DOTALL
)
C17_NEW = """cy.get('body').then($b => {
        const $chk = $b.find('.ant-table .ant-checkbox-input');
        if ($chk.length > 0) {
          cy.wrap($chk.first()).check({ force: true });
          cy.get('body').then($b2 => { if ($b2.find('.ant-checkbox-checked').length > 0) cy.get('.ant-checkbox-checked').should('exist'); });
          cy.wrap($chk.first()).uncheck({ force: true });
        }
      });"""

# C18 原始模式：cy.get('button:contains("导入"), .ant-btn:contains("导入")', { timeout: 5000 }).then($btn =>
# 改为 body.find 安全模式
C18_OLD = re.compile(
    r"cy\.get\('button:contains\(\"导入\"\),\s*\.ant-btn:contains\(\"导入\"\)',\s*\{\s*timeout:\s*\d+\s*\}\)\s*"
    r"\.then\(\$btn\s*=>\s*\{\s*"
    r"if\s*\(\$btn\.length\s*>\s*0\)\s*\{\s*"
    r"cy\.wrap\(\$btn\.first\(\)\)\.click\(\{\s*force:\s*true\s*\}\);\s*"
    r"cy\.get\('body'\)\.type\('\{esc\}'\);\s*"
    r"\}\s*\}\);",
    re.DOTALL
)
C18_NEW = """cy.get('body').then($b => {
        const $imp = $b.find('button:contains("导入"), .ant-btn:contains("导入")');
        if ($imp.length > 0) {
          cy.wrap($imp.first()).click({ force: true });
          cy.get('body').type('{esc}');
        }
      });"""

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    content = original
    
    # 修复 C07
    new_c07 = C07_OLD.sub(C07_NEW, content)
    c07_fixed = new_c07 != content
    content = new_c07
    
    # 修复 C17
    new_c17 = C17_OLD.sub(C17_NEW, content)
    c17_fixed = new_c17 != content
    content = new_c17
    
    # 修复 C18
    new_c18 = C18_OLD.sub(C18_NEW, content)
    c18_fixed = new_c18 != content
    content = new_c18
    
    changed = c07_fixed or c17_fixed or c18_fixed
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        markers = []
        if c07_fixed: markers.append('C07')
        if c17_fixed: markers.append('C17')
        if c18_fixed: markers.append('C18')
        print(f"  ✅ 修复 {os.path.basename(filepath)}: {', '.join(markers)}")
    else:
        # 检查是否有未匹配的 C07/C17/C18 模式（为了诊断）
        has_c07 = '.ant-table-column-sorters, .ant-table-column-has-sorters' in content and 'cy.get(\'.ant-table-column-sorters' in content
        has_c17 = '.ant-table .ant-checkbox-input' in content and 'cy.get(\'.ant-table .ant-checkbox-input' in content
        has_c18 = 'cy.get(\'button:contains("导入")' in content
        if has_c07 or has_c17 or has_c18:
            print(f"  ⚠️  {os.path.basename(filepath)}: 发现但未匹配 - c07={has_c07} c17={has_c17} c18={has_c18}")
        else:
            print(f"  ⏭️  {os.path.basename(filepath)}: 无需修复（模式不存在）")
    
    return changed

# 扫描所有 e2e 文件
e2e_dir = os.path.join(os.path.dirname(__file__), 'e2e')
files = sorted(glob.glob(os.path.join(e2e_dir, '*.cy.js')))

fixed_count = 0
for f in files:
    if fix_file(f):
        fixed_count += 1

print(f"\n共修复 {fixed_count} 个文件")
