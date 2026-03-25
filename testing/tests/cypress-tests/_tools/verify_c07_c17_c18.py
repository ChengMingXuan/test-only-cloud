import re, glob, os

files = sorted(glob.glob('d:/2026/aiops.v2/tests/cypress-tests/e2e/*.cy.js'))
c17_issues = []
c18_issues = []
c07_issues = []

for f in files:
    content = open(f, encoding='utf-8').read()
    bn = os.path.basename(f)
    if "cy.get('.ant-table .ant-checkbox-input'" in content:
        c17_issues.append(bn)
    # C18 旧模式
    if re.search(r"cy\.get\('button:contains\(\"导入\"\)", content):
        c18_issues.append(bn)
    # C07 旧模式
    if re.search(r"cy\.get\('\.ant-table-column-sorters.*?\.then\(\$s", content, re.DOTALL):
        c07_issues.append(bn)

print(f"C07 残留: {c07_issues if c07_issues else 'NONE'}")
print(f"C17 残留: {c17_issues if c17_issues else 'NONE'}")
print(f"C18 残留: {c18_issues if c18_issues else 'NONE'}")
print(f"总文件数: {len(files)}")
if not c07_issues and not c17_issues and not c18_issues:
    print("✅ C07/C17/C18 全部修复完成！")
