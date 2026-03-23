# -*- coding: utf-8 -*-
"""fix-double-nesting.py — 修复双重嵌套 cy.get('body').then() 模式"""
import re, os, glob

e2e_dir = 'e2e'
total_fixes = 0

# 模式：cy.get('body').then($b => { if ($b.find('X').length > 0) cy.get('body').then($b => { if ($b.find('X')...
# 修复：去掉外层，变成单层
pattern = re.compile(
    r"cy\.get\('body'\)\.then\(\$b\s*=>\s*\{\s*"
    r"if\s*\(\$b\.find\('([^']*)'\)\.length\s*>\s*0\)\s*"
    r"cy\.get\('body'\)\.then\(\$b\s*=>\s*\{\s*"
    r"if\s*\(\$b\.find\('\1'\)\.length\s*>\s*0\)\s*"
    r"(cy\.get\('\1'\)[^;]*;)"
    r"\s*else\s+cy\.log\([^)]*\);\s*\}\);\s*"
    r"else\s+cy\.log\([^)]*\);\s*\}\)",
    re.DOTALL
)

def fix_double(m):
    global total_fixes
    total_fixes += 1
    sel = m.group(1)
    inner_action = m.group(2)
    return (f"cy.get('body').then($b => {{ "
            f"if ($b.find('{sel}').length > 0) {inner_action} "
            f"else cy.log('元素未找到: {sel}'); }})")

for fpath in sorted(glob.glob(os.path.join(e2e_dir, '*.cy.js'))):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = pattern.sub(fix_double, content)
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ {os.path.basename(fpath)}")

print(f"\n修复 {total_fixes} 处双重嵌套")
