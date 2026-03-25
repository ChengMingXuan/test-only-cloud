"""修复导出按钮 cy.get('button').contains(/regex/).then() 模式"""
import re
import glob
import os

e2e_dir = os.path.join(os.path.dirname(__file__), 'e2e')
files = glob.glob(os.path.join(e2e_dir, '*.cy.js'))

# 不带 /i 的导出模式
pattern = re.compile(
    r"cy\.get\('button'\)\.contains\(/导出\|Export\|下载\|Download/\)\.then\(\(\$btn\) => \{\s*\n\s*if \(\$btn\.length > 0\) \{\s*\n\s*cy\.wrap\(\$btn\)\.should\('be\.visible'\);\s*\n\s*\}\s*\n\s*\}\);",
    re.MULTILINE,
)
replacement = (
    "cy.get('body').then($b => {\n"
    "        const $btn = $b.find('button').filter((_, el) => /导出|Export|下载|Download/i.test(el.textContent));\n"
    "        if ($btn.length > 0) { cy.wrap($btn.first()).should('be.visible'); }\n"
    "      });"
)

fixed = 0
for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()
    count = len(pattern.findall(content))
    if count:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(pattern.sub(replacement, content))
        fixed += count

print(f"修复 {fixed} 处")
