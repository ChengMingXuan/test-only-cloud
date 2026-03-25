"""
修复 C24 - 使用正则宽松匹配所有变体
"""
import re, glob, os

BASE = os.path.dirname(__file__)

# 匹配所有 C24 变体:
# cy.get('.ant-modal-close, .ant-drawer-close').then($xxx => {
#   if ($xxx.length > 0) cy.wrap($xxx.first()).click({ force: true });
#   else cy.get('button:contains(...)').first().click({ force: true });
# });
C24_PATTERN = re.compile(
    r"cy\.get\('\.ant-modal-close, \.ant-drawer-close'\)\.then\(\$\w+ => \{[^}]+\}\);",
    re.DOTALL
)

C24_NEW = """cy.get('body').then($b => { const $cl = $b.find('.ant-modal-close, .ant-drawer-close'); if ($cl.length > 0) cy.wrap($cl.first()).click({ force: true }); else cy.get('body').type('{esc}', { force: true }); });"""

files = (
    glob.glob(os.path.join(BASE, "e2e", "4*.cy.js")) +
    glob.glob(os.path.join(BASE, "e2e", "5*.cy.js")) +
    glob.glob(os.path.join(BASE, "e2e", "6*.cy.js"))
)

fixed = 0
for path in sorted(files):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    if ".ant-modal-close, .ant-drawer-close').then" not in content:
        continue

    new_content, count = C24_PATTERN.subn(C24_NEW, content)
    if count > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        fixed += 1
        print(f"Fixed {count}x C24: {os.path.basename(path)}")
    else:
        # 正则未匹配，输出实际代码供调试
        m = re.search(r"(cy\.get\('\.ant-modal-close.{0,200})", content, re.DOTALL)
        if m:
            print(f"  UNMATCHED in {os.path.basename(path)}: {repr(m.group(1)[:100])}")

print(f"\nFixed {fixed} files")
