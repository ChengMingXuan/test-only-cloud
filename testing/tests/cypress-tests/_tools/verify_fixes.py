"""验证所有修复是否生效"""
import re, glob, os

files = glob.glob('e2e/4*.cy.js') + glob.glob('e2e/5*.cy.js') + glob.glob('e2e/6*.cy.js')
problems = {}

for f in sorted(files):
    c = open(f, encoding='utf-8').read()
    issues = []

    # C06: 旧模式: cy.get('.ant-select-dropdown', {...}).should('exist')
    if re.search(r"cy\.get\('\.ant-select-dropdown',\s*\{[^}]+\}\)\.should\('exist'\)", c):
        issues.append('C06')

    # C07: 旧模式: cy.get('.ant-picker-dropdown', {...}).should('exist')
    if re.search(r"cy\.get\('\.ant-picker-dropdown',\s*\{[^}]+\}\)\.should\('exist'\)", c):
        issues.append('C07')

    # C08: 旧模式: cy.wrap($p).find('.ant-pagination-next')
    if "cy.wrap($p).find('.ant-pagination-next')" in c:
        issues.append('C08')

    # C21: 旧模式: cy.get('.ant-empty...', {...}).should('exist')
    if re.search(r"cy\.get\('\.ant-empty[^']*',\s*\{[^}]+\}\)\.should\('exist'\)", c):
        issues.append('C21')

    # C24: 旧模式: ant-modal-close, .ant-drawer-close').then($close
    if re.search(r"ant-modal-close, \.ant-drawer-close'\)\.then\(\$", c):
        issues.append('C24')

    if issues:
        problems[os.path.basename(f)] = issues

if problems:
    print("ISSUES REMAINING:")
    for k, v in sorted(problems.items()):
        print(f"  {k}: {v}")
else:
    print("ALL CLEAR - all patterns fixed!")

print(f"\nScanned {len(files)} files")
