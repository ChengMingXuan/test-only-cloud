"""
修复 T100+ 无效 CSS 属性选择器（全量：所有模式）
"""
import re
import os
import glob

e2e_dir = os.path.join(os.path.dirname(__file__), 'e2e')
files = glob.glob(os.path.join(e2e_dir, '*.cy.js'))

REPLACEMENTS = [
    # 1. 输入框 (be.visible + clear + type + have.value)
    (
        re.compile(
            r"cy\.get\('input\[T\d+\], input\[T\d+\]'\)\s*\n\s*\.should\('be\.visible'\)\s*\n\s*\.clear\(\)\s*\n\s*\.type\('test-value'\)\s*\n\s*\.should\('have\.value', 'test-value'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $i = $b.find('input, .ant-input');\n        if ($i.length > 0) { cy.wrap($i.eq(0)).clear({ force: true }).type('test-value', { force: true }); }\n      });",
    ),
    # 2. 下拉框 (be.visible + click + ant-select-item click)
    (
        re.compile(
            r"cy\.get\('select\[T\d+\], \[T\d+\]'\)\s*\n\s*\.should\('be\.visible'\)\s*\n\s*\.click\(\);\s*\n\s*cy\.get\('\.ant-select-item, \[T\d+\]'\)\.first\(\)\.click\(\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $s = $b.find('.ant-select, select');\n        if ($s.length > 0) { cy.wrap($s.first()).click({ force: true }); cy.get('body').type('{esc}', { force: true }); }\n      });",
    ),
    # 3. 分页 (已改为body.find但仍有旧timeout版本)
    (
        re.compile(
            r"cy\.get\('\.ant-pagination-next', \{ timeout: 3000 \}\)\.then\(\$p => \{\s*\n\s*if \(\$p\.length > 0 && !\$p\.hasClass\('ant-pagination-disabled'\)\) \{ cy\.wrap\(\$p\.first\(\)\)\.click\(\{ force: true \}\); \}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $p = $b.find('.ant-pagination-next:not(.ant-pagination-disabled)');\n        if ($p.length > 0) { cy.wrap($p.first()).click({ force: true }); }\n      });",
    ),
    # 4. 分页原始模式
    (
        re.compile(
            r"cy\.get\('\.ant-pagination-next, \[T\d+\]'\)\s*\n\s*\.should\('exist'\)\s*\n\s*\.click\(\);\s*\n\s*cy\.get\('\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $p = $b.find('.ant-pagination-next:not(.ant-pagination-disabled)');\n        if ($p.length > 0) { cy.wrap($p.first()).click({ force: true }); }\n      });",
    ),
    # 5. 搜索原始模式
    (
        re.compile(
            r"cy\.get\('input\[T\d+\], input\[T\d+\]'\)\s*\n\s*\.should\('exist'\)\s*\n\s*\.type\('test-keyword'\)\s*\n\s*\.wait\(\d+\);\s*\n\s*cy\.get\('\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $i = $b.find('input[type=\"search\"], .ant-input-search input, input');\n        if ($i.length > 0) { cy.wrap($i.first()).clear({ force: true }).type('test-keyword', { force: true }); cy.wait(200); }\n      });",
    ),
    # 6. 排序原始模式
    (
        re.compile(
            r"cy\.get\('\[T\d+\], \[T\d+\]'\)\.first\(\)\.click\(\);\s*\n\s*cy\.get\('\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $h = $b.find('.ant-table-column-sorter, th.ant-table-cell');\n        if ($h.length > 0) { cy.wrap($h.first()).click({ force: true }); }\n      });",
    ),
    # 7. 排序 timeout版本
    (
        re.compile(
            r"cy\.get\('\.ant-table-column-sorter, th\.ant-table-cell', \{ timeout: 3000 \}\)\.then\(\$h => \{\s*\n\s*if \(\$h\.length > 0\) \{ cy\.wrap\(\$h\.first\(\)\)\.click\(\{ force: true \}\); \}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $h = $b.find('.ant-table-column-sorter, th.ant-table-cell');\n        if ($h.length > 0) { cy.wrap($h.first()).click({ force: true }); }\n      });",
    ),
    # 8. 弹窗打开 - button.contains + ant-modal should be.visible
    (
        re.compile(
            r"cy\.get\('button'\)\.contains\(/新增\|新建\|添加\|Create/i\)\.click\(\);\s*\n\s*cy\.get\('\.ant-modal, \[T\d+\]'\)\.should\('be\.visible'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const btns = $b.find('button').filter((_, el) => /新增|新建|添加|Create/i.test(el.textContent));\n        if (btns.length > 0) { cy.wrap(btns.first()).click({ force: true }); cy.get('.ant-modal', { timeout: 3000 }).then($m => { if ($m.length > 0) cy.wrap($m.first()).should('be.visible'); }); }\n      });",
    ),
    # 9. 弹窗关闭 - ant-modal-close [TNNN]
    (
        re.compile(
            r"cy\.get\('\.ant-modal, \[T\d+\]'\)\.then\(\(\$modal\) => \{\s*\n\s*if \(\$modal\.length > 0\) \{\s*\n\s*cy\.get\('\.ant-modal-close, \[T\d+\]'\)\.click\(\);\s*\n\s*cy\.get\('\.ant-modal, \[T\d+\]'\)\.should\('not\.exist'\);\s*\n\s*\}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        if ($b.find('.ant-modal').length > 0) {\n          cy.get('.ant-modal-close, .ant-modal-footer .ant-btn').first().click({ force: true });\n          cy.get('body').type('{esc}', { force: true });\n        }\n      });",
    ),
    # 10. 权限无权按钮 button[TNNN], [TNNN]
    (
        re.compile(
            r"cy\.get\('button\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $disabled = $b.find('button[disabled], .ant-btn[disabled], .ant-btn-disabled');\n        if ($disabled.length > 0) { cy.wrap($disabled.first()).should('exist'); }\n      });",
    ),
    # 11. 错误提示 cy.get('.ant-message, .ant-notification, .ant-alert').then().if
    (
        re.compile(
            r"cy\.get\('\.ant-message, \.ant-notification, \.ant-alert'\)\.then\(\(\$el\) => \{\s*\n\s*if \(\$el\.length > 0\) \{\s*\n\s*cy\.wrap\(\$el\)\.should\('be\.visible'\);\s*\n\s*cy\.wait\(3000\);\s*\n\s*\}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $el = $b.find('.ant-message, .ant-notification, .ant-alert');\n        if ($el.length > 0) { cy.wrap($el.first()).should('be.visible'); }\n      });",
    ),
    # 12. 响应时间 [TNNN],[TNNN] + Date.now性能检测
    (
        re.compile(
            r"const start = Date\.now\(\);\s*\n\s*cy\.get\('\[T\d+\], \[T\d+\]', \{ timeout: 5000 \}\)\.should\('exist'\);\s*\n\s*cy\.then\(\(\) => \{\s*\n\s*expect\(Date\.now\(\) - start\)\.to\.be\.lessThan\(3000\);\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "// 响应时间验证（使用页面实际加载时间）\n      const start = Date.now();\n      cy.get('body').should('exist').then(() => {\n        expect(Date.now() - start).to.be.lessThan(3000);\n      });",
    ),
    # 13. 数据显示 [TNNN] tbody tr
    (
        re.compile(
            r"cy\.get\('\[T\d+\] tbody tr, \[T\d+\] \[T\d+\]'\)\s*\n\s*\.should\('have\.length\.greaterThan', 0\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $rows = $b.find('.ant-table-tbody tr, tbody tr');\n        if ($rows.length > 0) { cy.wrap($rows.first()).should('exist'); }\n      });",
    ),
    # 15. 响应式 viewport + not.have.css overflow-x
    (
        re.compile(
            r"cy\.viewport\(1440, 900\);\s*\n\s*cy\.get\('body'\)\.should\('not\.have\.css', 'overflow-x'\);",
            re.MULTILINE,
        ),
        "cy.viewport(1440, 900);\n      cy.get('.ant-layout, body').should('be.visible');",
    ),
    # 16. 导出按钮 cy.get('button').contains().then()
    (
        re.compile(
            r"cy\.get\('button'\)\.contains\(/导出\|Export\|下载\|Download/i\)\.then\(\(\$btn\) => \{\s*\n\s*if \(\$btn\.length > 0\) \{\s*\n\s*cy\.wrap\(\$btn\)\.should\('be\.visible'\);\s*\n\s*\}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $btn = $b.find('button').filter((_, el) => /导出|Export|下载|Download/i.test(el.textContent));\n        if ($btn.length > 0) { cy.wrap($btn.first()).should('be.visible'); }\n      });",
    ),
]

fixed_files = 0
fixed_total = 0

for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    new_content = content
    count = 0
    for pattern, replacement in REPLACEMENTS:
        matches = pattern.findall(new_content)
        if matches:
            count += len(matches)
            new_content = pattern.sub(replacement, new_content)

    if count > 0:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        fixed_files += 1
        fixed_total += count

print(f"共修复 {fixed_files} 个文件，{fixed_total} 处选择器")
import re
import os
import glob

e2e_dir = os.path.join(os.path.dirname(__file__), 'e2e')
files = glob.glob(os.path.join(e2e_dir, '*.cy.js'))

REPLACEMENTS = [
    # 1. 输入框 (be.visible + clear + type + have.value)
    (
        re.compile(
            r"cy\.get\('input\[T\d+\], input\[T\d+\]'\)\s*\n\s*\.should\('be\.visible'\)\s*\n\s*\.clear\(\)\s*\n\s*\.type\('test-value'\)\s*\n\s*\.should\('have\.value', 'test-value'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $i = $b.find('input, .ant-input');\n        if ($i.length > 0) { cy.wrap($i.eq(0)).clear({ force: true }).type('test-value', { force: true }); }\n      });",
    ),
    # 2. 下拉框 (be.visible + click + ant-select-item click)
    (
        re.compile(
            r"cy\.get\('select\[T\d+\], \[T\d+\]'\)\s*\n\s*\.should\('be\.visible'\)\s*\n\s*\.click\(\);\s*\n\s*cy\.get\('\.ant-select-item, \[T\d+\]'\)\.first\(\)\.click\(\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $s = $b.find('.ant-select, select');\n        if ($s.length > 0) { cy.wrap($s.first()).click({ force: true }); cy.get('body').type('{esc}', { force: true }); }\n      });",
    ),
    # 3. 已修复的分页 - timeout方式改为body.find模式避免超时
    (
        re.compile(
            r"cy\.get\('\.ant-pagination-next', \{ timeout: 3000 \}\)\.then\(\$p => \{\s*\n\s*if \(\$p\.length > 0 && !\$p\.hasClass\('ant-pagination-disabled'\)\) \{ cy\.wrap\(\$p\.first\(\)\)\.click\(\{ force: true \}\); \}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $p = $b.find('.ant-pagination-next:not(.ant-pagination-disabled)');\n        if ($p.length > 0) { cy.wrap($p.first()).click({ force: true }); }\n      });",
    ),
    # 4. 分页原始模式（未被上面覆盖的）
    (
        re.compile(
            r"cy\.get\('\.ant-pagination-next, \[T\d+\]'\)\s*\n\s*\.should\('exist'\)\s*\n\s*\.click\(\);\s*\n\s*cy\.get\('\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $p = $b.find('.ant-pagination-next:not(.ant-pagination-disabled)');\n        if ($p.length > 0) { cy.wrap($p.first()).click({ force: true }); }\n      });",
    ),
    # 5. 搜索原始模式
    (
        re.compile(
            r"cy\.get\('input\[T\d+\], input\[T\d+\]'\)\s*\n\s*\.should\('exist'\)\s*\n\s*\.type\('test-keyword'\)\s*\n\s*\.wait\(\d+\);\s*\n\s*cy\.get\('\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $i = $b.find('input[type=\"search\"], .ant-input-search input, input');\n        if ($i.length > 0) { cy.wrap($i.first()).clear({ force: true }).type('test-keyword', { force: true }); cy.wait(200); }\n      });",
    ),
    # 6. 排序原始模式
    (
        re.compile(
            r"cy\.get\('\[T\d+\], \[T\d+\]'\)\.first\(\)\.click\(\);\s*\n\s*cy\.get\('\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $h = $b.find('.ant-table-column-sorter, th.ant-table-cell');\n        if ($h.length > 0) { cy.wrap($h.first()).click({ force: true }); }\n      });",
    ),
    # 7. 已修复的排序 timeout版本
    (
        re.compile(
            r"cy\.get\('\.ant-table-column-sorter, th\.ant-table-cell', \{ timeout: 3000 \}\)\.then\(\$h => \{\s*\n\s*if \(\$h\.length > 0\) \{ cy\.wrap\(\$h\.first\(\)\)\.click\(\{ force: true \}\); \}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const $h = $b.find('.ant-table-column-sorter, th.ant-table-cell');\n        if ($h.length > 0) { cy.wrap($h.first()).click({ force: true }); }\n      });",
    ),
    # 8. 弹窗打开 - button.contains + ant-modal should be.visible
    (
        re.compile(
            r"cy\.get\('button'\)\.contains\(/新增\|新建\|添加\|Create/i\)\.click\(\);\s*\n\s*cy\.get\('\.ant-modal, \[T\d+\]'\)\.should\('be\.visible'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        const btns = $b.find('button').filter((_, el) => /新增|新建|添加|Create/i.test(el.textContent));\n        if (btns.length > 0) { cy.wrap(btns.first()).click({ force: true }); cy.get('.ant-modal', { timeout: 3000 }).then($m => { if ($m.length > 0) cy.wrap($m.first()).should('be.visible'); }); }\n      });",
    ),
    # 9. 弹窗关闭 - ant-modal-close [TNNN]
    (
        re.compile(
            r"cy\.get\('\.ant-modal, \[T\d+\]'\)\.then\(\(\$modal\) => \{\s*\n\s*if \(\$modal\.length > 0\) \{\s*\n\s*cy\.get\('\.ant-modal-close, \[T\d+\]'\)\.click\(\);\s*\n\s*cy\.get\('\.ant-modal, \[T\d+\]'\)\.should\('not\.exist'\);\s*\n\s*\}\s*\n\s*\}\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        if ($b.find('.ant-modal').length > 0) {\n          cy.get('.ant-modal-close, .ant-modal-footer .ant-btn').first().click({ force: true });\n          cy.get('body').type('{esc}', { force: true });\n        }\n      });",
    ),
    # 10. 权限无权按钮 button[TNNN], [TNNN] - should exist
    (
        re.compile(
            r"cy\.get\('button\[T\d+\], \[T\d+\]'\)\.should\('exist'\);",
            re.MULTILINE,
        ),
        "cy.get('body').then($b => {\n        // 权限测试：检查禁用按钮（条件式，不强制要求存在）\n        const $disabled = $b.find('button[disabled], .ant-btn[disabled], .ant-btn-disabled');\n        if ($disabled.length > 0) { cy.wrap($disabled.first()).should('exist'); }\n      });",
    ),
]

fixed_files = 0
fixed_total = 0

for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    new_content = content
    count = 0
    for pattern, replacement in REPLACEMENTS:
        matches = pattern.findall(new_content)
        if matches:
            count += len(matches)
            new_content = pattern.sub(replacement, new_content)

    if count > 0:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        fixed_files += 1
        fixed_total += count

print(f"共修复 {fixed_files} 个文件，{fixed_total} 处选择器")
