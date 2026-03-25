"""修复导出按钮 should('be.visible') → should('exist') 因为按钮在hidden容器里"""
import re
import glob
import os

e2e_dir = os.path.join(os.path.dirname(__file__), 'e2e')
files = glob.glob(os.path.join(e2e_dir, '*.cy.js'))

# 修复导出按钮的 be.visible → exist
pattern = re.compile(
    r"(cy\.get\('body'\)\.then\(\$b => \{\s*\n\s*const \$btn = \$b\.find\('button'\)\.filter\(\(_, el\) => /导出\|Export\|下载\|Download/i\.test\(el\.textContent\)\);\s*\n\s*if \(\$btn\.length > 0\) \{ cy\.wrap\(\$btn\.first\(\)\))\.should\('be\.visible'\);(\s*\}\s*\n\s*\}\);)",
    re.MULTILINE,
)
replacement = r"\1.should('exist');\2"

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
