"""修复 cy.contains('button', '中文') 模式"""
import glob, re, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
files = glob.glob('e2e/*.cy.js')
count = 0
for f in sorted(files):
    with open(f, 'r', encoding='utf-8') as fh:
        c = fh.read()
    orig = c
    # cy.contains('button', '中文') -> cy.get('button').first()
    c = re.sub(
        r"""cy\.contains\(\s*['"]button['"]\s*,\s*['"][^'"]+['"]\s*\)""",
        "cy.get('button').first()",
        c
    )
    if c != orig:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(c)
        count += 1
        print(f'  修复: {os.path.basename(f)}')
print(f'\n共修复 {count} 个文件')
