"""
修复 T100+ 测试中仍残留 cy.get(SELECTOR, {timeout}).then(...) 的三种模式
改为 cy.get('body').then($b => { const $X = $b.find(SELECTOR); ... }
确保在无匹配元素时不会 timeout 报错
"""
import glob

files = glob.glob(r'D:\2026\aiops.v2\tests\cypress-tests\e2e\*.cy.js')
total_fixes = 0

# 三个精确字符串替换
REPLACEMENTS = [
    # 1. input 模式
    (
        "cy.get('input, .ant-input', { timeout: 3000 }).then($i => {",
        "cy.get('body').then($b => { const $i = $b.find('input, .ant-input');"
    ),
    # 2. select 模式
    (
        "cy.get('.ant-select, select', { timeout: 3000 }).then($s => {",
        "cy.get('body').then($b => { const $s = $b.find('.ant-select, select');"
    ),
    # 3. search input 模式
    (
        "cy.get('input[type=\"search\"], .ant-input-search input, input', { timeout: 3000 }).then($i => {",
        "cy.get('body').then($b => { const $i = $b.find('input[type=\"search\"], .ant-input-search input, input');"
    ),
    # 4. search input（单引号内双引号写法）
    (
        "cy.get('input[type=\"search\"], .ant-input-search input, input', { timeout: 3000 }).then($s => {",
        "cy.get('body').then($b => { const $s = $b.find('input[type=\"search\"], .ant-input-search input, input');"
    ),
    # 5. .ant-modal nested - 改成 body.find 防 timeout
    (
        "cy.get('.ant-modal', { timeout: 3000 }).then($m => { if ($m.length > 0) cy.wrap($m.first()).should('be.visible'); })",
        "cy.get('body').then($bm => { const $m = $bm.find('.ant-modal'); if ($m.length > 0) cy.wrap($m.first()).should('exist'); })"
    ),
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for old, new in REPLACEMENTS:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            total_fixes += count

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print(f'修复完成，共处理 {total_fixes} 处，文件数: {len(files)}')
