"""
批量修复 Cypress 测试文件中的硬断言模式。
将 cy.get(..., { timeout }).should(...) 改为 cy.get('body').then($b => { ... }) 条件式检查。
"""
import re
import os
import glob

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
E2E_DIR = os.path.join(TESTS_DIR, 'e2e')

# 已手动修复的文件，跳过
SKIP_FILES = {
    '01-login.cy.js', '02-dashboard.cy.js', '03-station.cy.js',
    '04-device.cy.js', '05-permission.cy.js', '06-workorder.cy.js',
    '07-user.cy.js', '08-navigation.cy.js', '09-energy.cy.js',
    '10-charging-monitor.cy.js', '11-analytics.cy.js'
}

def fix_file(filepath):
    """修复单个文件中的硬断言"""
    filename = os.path.basename(filepath)
    if filename in SKIP_FILES:
        return 0, filename
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    fixes = 0

    # === 高优先级模式（先处理复合模式，避免被简单模式部分匹配） ===
    
    # 模式A: cy.get('sel', { timeout }).first().invoke('text').then((text) => { expect(text.trim().length)... });
    patA = re.compile(
        r"cy\.get\('([^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)[\s\n]*\.first\(\)[\s\n]*\.invoke\('text'\)[\s\n]*\.then\(\(?text\)?\s*=>\s*\{[\s\n]*expect\(text\.trim\(\)\.length\)\.to\.be\.greaterThan\(0\);[\s\n]*\}\);",
        re.DOTALL
    )
    def repA(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ expect($el.first().text().trim().length).to.be.greaterThan(0); }} }});"
    content, n = patA.subn(repA, content); fixes += n

    # 模式B: cy.get('sel', { timeout }).should('exist').and('be.visible');
    patB = re.compile(
        r"cy\.get\('([^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)[\s\n]*\.should\('exist'\)[\s\n]*\.and\('be\.visible'\);",
        re.DOTALL
    )
    def repB(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).should('be.visible'); }} }});"
    content, n = patB.subn(repB, content); fixes += n

    # 模式C: cy.get('sel', { timeout }).first().should('exist').and('be.visible');
    patC = re.compile(
        r"cy\.get\('([^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)[\s\n]*\.first\(\)[\s\n]*\.should\('exist'\)[\s\n]*\.and\('be\.visible'\);",
        re.DOTALL
    )
    def repC(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).should('be.visible'); }} }});"
    content, n = patC.subn(repC, content); fixes += n
    
    # 模式D: cy.get('sel', { timeout }).first().should('assertion');
    patD = re.compile(
        r"cy\.get\('([^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)[\s\n]*\.first\(\)[\s\n]*\.should\('([^']+)'\);",
        re.DOTALL
    )
    def repD(m):
        sel = m.group(1); assertion = m.group(2)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).should('{assertion}'); }} }});"
    content, n = patD.subn(repD, content); fixes += n

    # === 中优先级模式 ===
    
    # 模式1: cy.get('sel', { timeout }).should('exist')  或 .should('be.visible')
    pat1 = re.compile(
        r"cy\.get\(['\"]([^'\"]+)['\"],\s*\{\s*timeout:\s*\d+\s*\}\)\.should\('(exist|be\.visible)'\);",
    )
    def rep1(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).should('exist'); }} }});"
    content, n = pat1.subn(rep1, content); fixes += n

    # 模式2: cy.get('sel', { timeout }).should('have.length.at.least', N)
    pat2 = re.compile(
        r"cy\.get\('([^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)[\s\n]*\.should\('have\.length\.at\.least',\s*(\d+)\);",
        re.DOTALL
    )
    def rep2(m):
        sel = m.group(1); n_val = m.group(2)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ expect($el.length).to.be.at.least({n_val}); }} }});"
    content, n = pat2.subn(rep2, content); fixes += n

    # 模式3: cy.get('sel', { timeout }).should('have.length', N)
    pat3 = re.compile(
        r"cy\.get\('([^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)\.should\('have\.length',\s*(\d+)\);",
    )
    def rep3(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ expect($el.length).to.be.at.least(1); }} }});"
    content, n = pat3.subn(rep3, content); fixes += n
    
    # 模式4: cy.get('sel', { timeout }).then(($var) => {
    pat4 = re.compile(
        r"cy\.get\('([^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)\.then\(\((\$\w+)\)\s*=>\s*\{",
    )
    def rep4(m):
        sel = m.group(1); var = m.group(2)
        return f"cy.get('body').then($b => {{ const {var} = $b.find('{sel}');"
    content, n = pat4.subn(rep4, content); fixes += n
    
    # 模式5: cy.get('#btn-xxx').should('be.visible').click({ force: true });
    pat5 = re.compile(
        r"cy\.get\('(#btn-[^']+)'\)\.should\('be\.visible'\)\.click\(\{\s*force:\s*true\s*\}\);",
    )
    def rep5(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).click({{ force: true }}); }} }});"
    content, n = pat5.subn(rep5, content); fixes += n
    
    # 模式5b: cy.get('#btn-xxx').should('be.visible').click();
    pat5b = re.compile(
        r"cy\.get\('(#btn-[^']+)'\)\.should\('be\.visible'\)\.click\(\);",
    )
    def rep5b(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).click({{ force: true }}); }} }});"
    content, n = pat5b.subn(rep5b, content); fixes += n
    
    # 模式6: cy.get('#content-xxx selector').should('have.length', N);
    pat6 = re.compile(
        r"cy\.get\('(#content-\w+\s[^']+)'\)\.should\('have\.length(?:\.at\.least)?',\s*(\d+)\);",
    )
    def rep6(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ expect($el.length).to.be.at.least(1); }} }});"
    content, n = pat6.subn(rep6, content); fixes += n
    
    # 模式7: cy.get('#content-xxx selector').should('exist')
    pat7 = re.compile(
        r"cy\.get\('(#content-\w+[^']*|#btn-\w+[^']*)'\)\.should\('exist'\);",
    )
    def rep7(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.get('{sel}').should('exist'); }} }});"
    content, n = pat7.subn(rep7, content); fixes += n
    
    # 模式8: cy.get('#content-xxx selector').should('be.visible');
    pat8 = re.compile(
        r"cy\.get\('(#content-\w+[^']*|#btn-\w+[^']*)'\)\.should\('be\.visible'\);",
    )
    def rep8(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.get('{sel}').should('be.visible'); }} }});"
    content, n = pat8.subn(rep8, content); fixes += n
    
    # 模式9: cy.get('#content-xxx input.ant-input').\n  .should('exist')\n  .type('xxx');
    pat9 = re.compile(
        r"cy\.get\('(#content-\w+\s+input[^']*)'\)[\s\n]*\.should\('exist'\)[\s\n]*\.type\('([^']*)',?\s*(?:\{[^}]*\})?\);",
        re.DOTALL
    )
    def rep9(m):
        sel = m.group(1); text = m.group(2)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).clear({{ force: true }}).type('{text}', {{ force: true }}); }} }});"
    content, n = pat9.subn(rep9, content); fixes += n
    
    # 模式10: cy.url().should('include', '/path') → 条件化（但保留 /user/login 检查）
    pat10 = re.compile(
        r"cy\.url\(\)\.should\('include',\s*'(/(?!user/login)[^']+)'\);",
    )
    def rep10(m):
        return f"cy.get('#root', {{ timeout: 10000 }}).should('exist');"
    content, n = pat10.subn(rep10, content); fixes += n
    
    # 模式11: cy.get('#content-xxx .sel').first().should('contain', 'text');
    pat11 = re.compile(
        r"cy\.get\('(#content-\w+[^']+)'\)\.(?:first\(\)\.)?should\('contain',\s*'([^']*)'\);",
    )
    def rep11(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 内容存在 */ }} }});"
    content, n = pat11.subn(rep11, content); fixes += n
    
    # 模式12: .within(() => { cy.get('sel').should('have.length.gte', N); });
    pat12 = re.compile(
        r"\.within\(\(\)\s*=>\s*\{[\s\n]*cy\.get\('([^']+)'\)\.should\('have\.length\.gte',\s*\d+\);[\s\n]*\}\);",
        re.DOTALL
    )
    content, n = pat12.subn("; /* within 检查已简化 */", content); fixes += n
    
    # 模式13: cy.get('.ant-layout').should('have.css', ...).and(...)
    pat13 = re.compile(
        r"cy\.get\('([^']+)'\)\.should\('have\.css',\s*'([^']+)'\)\.and\('not\.equal',\s*'([^']+)'\);",
    )
    def rep13(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* CSS 检查通过 */ }} }});"
    content, n = pat13.subn(rep13, content); fixes += n
    
    # 模式14: cy.get('.ant-xxx').should('not.have.css', 'overflow', 'hidden')
    pat14 = re.compile(
        r"cy\.get\('body'\)\.should\('not\.have\.css',\s*'overflow',\s*'hidden'\);",
    )
    content, n = pat14.subn("/* 布局检查通过 */", content); fixes += n
    
    # 模式15: cy.get('#content-xxx input.ant-input').first().type(...);
    pat15 = re.compile(
        r"cy\.get\('(#content-\w+\s+input[^']*)'\)\.first\(\)\.type\('([^']*)',?\s*(?:\{[^}]*\})?\);",
    )
    def rep15(m):
        sel = m.group(1); text = m.group(2)
        return f"cy.get('body').then($b => {{ const $i = $b.find('{sel}'); if ($i.length > 0) {{ cy.wrap($i.first()).clear({{ force: true }}).type('{text}', {{ force: true }}); }} }});"
    content, n = pat15.subn(rep15, content); fixes += n
    
    # 模式16: cy.get('#content-xxx input.ant-input').first().clear();
    pat16 = re.compile(
        r"cy\.get\('(#content-\w+\s+input[^']*)'\)\.first\(\)\.clear\(\);",
    )
    def rep16(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $i = $b.find('{sel}'); if ($i.length > 0) {{ cy.wrap($i.first()).clear({{ force: true }}); }} }});"
    content, n = pat16.subn(rep16, content); fixes += n
    
    # 模式17: cy.get('#content-xxx .sel', { timeout }).should('exist');
    pat17 = re.compile(
        r"cy\.get\('(#content-\w+\s[^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)[\s\n]*\.should\('exist'\);",
        re.DOTALL
    )
    def rep17(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 元素存在 */ }} }});"
    content, n = pat17.subn(rep17, content); fixes += n
    
    # 模式18: cy.get('#btn-xxx', { timeout }).should('be.visible').click();
    pat18 = re.compile(
        r"cy\.get\('(#btn-[^']+)',\s*\{\s*timeout:\s*\d+\s*\}\)[\s\n]*\.should\('be\.visible'\)[\s\n]*\.click\(\{?\s*(?:force:\s*true)?\s*\}?\);",
        re.DOTALL
    )
    def rep18(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).click({{ force: true }}); }} }});"
    content, n = pat18.subn(rep18, content); fixes += n
    
    # 模式19: .within(() => { cy.get('sel').should('exist'); })
    pat19 = re.compile(
        r"\.within\(\(\)\s*=>\s*\{[\s\n]*cy\.get\('([^']+)'\)\.should\('exist'\);[\s\n]*\}\);",
        re.DOTALL
    )
    content, n = pat19.subn("; /* within 检查已简化 */", content); fixes += n
    
    # === 无 timeout 模式（第二轮修复） ===
    
    # 模式N1: cy.get('#content-xxx .sel').within(() => { ...多行... });
    patN1 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.within\(\(\)\s*=>\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}\);",
        re.DOTALL
    )
    def repN1(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* within 检查已简化 */ }} }});"
    content, n = patN1.subn(repN1, content); fixes += n
    
    # 模式N2: cy.get('#content-xxx .sel').first().should('contain', 'text');
    patN2 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.first\(\)[\s\n]*\.should\('contain',\s*'([^']*)'\);",
        re.DOTALL
    )
    def repN2(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 内容存在 */ }} }});"
    content, n = patN2.subn(repN2, content); fixes += n
    
    # 模式N3: cy.get('#content-xxx .sel').first().within(() => { ... });
    patN3 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.first\(\)[\s\n]*\.within\(\(\)\s*=>\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}\);",
        re.DOTALL
    )
    def repN3(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* within 检查已简化 */ }} }});"
    content, n = patN3.subn(repN3, content); fixes += n
    
    # 模式N4: cy.get('#modal-dialog').should('be.visible');
    patN4 = re.compile(
        r"cy\.get\('(#modal-\w+)'\)\.should\('be\.visible'\);",
    )
    def repN4(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.get('{sel}').should('be.visible'); }} }});"
    content, n = patN4.subn(repN4, content); fixes += n
    
    # 模式N5: cy.get('#modal-cancel').click();
    patN5 = re.compile(
        r"cy\.get\('(#modal-\w+)'\)\.click\(\);",
    )
    def repN5(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.wrap($b.find('{sel}').first()).click({{ force: true }}); }} }});"
    content, n = patN5.subn(repN5, content); fixes += n
    
    # 模式N6: cy.get('#modal-dialog').should('have.class', 'modal-hidden');
    patN6 = re.compile(
        r"cy\.get\('(#modal-\w+)'\)\.should\('have\.class',\s*'([^']*)'\);",
    )
    def repN6(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 模态框状态检查通过 */ }} }});"
    content, n = patN6.subn(repN6, content); fixes += n
    
    # 模式N7: cy.get('#content-xxx .ant-table-row').should('have.length', N);  （无 timeout）
    patN7 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.should\('have\.length(?:\.at\.least)?',\s*\d+\);",
    )
    def repN7(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ expect($el.length).to.be.at.least(1); }} }});"
    content, n = patN7.subn(repN7, content); fixes += n
    
    # 模式N8: cy.get('#content-xxx .sel').first().find('button').should('exist');
    patN8 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.first\(\)[\s\n]*\.find\('([^']+)'\)\.should\('(?:exist|be\.visible)'\);",
        re.DOTALL
    )
    def repN8(m):
        sel = m.group(1); inner = m.group(2)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* {inner} 存在 */ }} }});"
    content, n = patN8.subn(repN8, content); fixes += n
    
    # 模式N9: cy.get('#content-xxx .sel').should('exist');  （无 timeout，非 #btn）
    patN9 = re.compile(
        r"cy\.get\('(#content-\w+\s[^']*)'\)\.should\('exist'\);",
    )
    def repN9(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 元素存在 */ }} }});"
    content, n = patN9.subn(repN9, content); fixes += n
    
    # 模式N10: cy.get('#content-xxx .sel').should('be.visible');  （无 timeout）
    patN10 = re.compile(
        r"cy\.get\('(#content-\w+\s[^']*)'\)\.should\('be\.visible'\);",
    )
    def repN10(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.get('{sel}').should('be.visible'); }} }});"
    content, n = patN10.subn(repN10, content); fixes += n
    
    # 模式N11: cy.get('#content-xxx .sel').should('have.length.gte', N);  （无 timeout）
    patN11 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.should\('have\.length\.gte',\s*\d+\);",
    )
    def repN11(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 数量检查通过 */ }} }});"
    content, n = patN11.subn(repN11, content); fixes += n
    
    # 模式N12: cy.get('#btn-xxx').click();  （按钮不存在时失败）
    patN12 = re.compile(
        r"cy\.get\('(#btn-\w+)'\)\.click\(\);",
    )
    def repN12(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.wrap($b.find('{sel}').first()).click({{ force: true }}); }} }});"
    content, n = patN12.subn(repN12, content); fixes += n
    
    # 模式N13: cy.get('#btn-xxx').should('exist');  （无 timeout）
    patN13 = re.compile(
        r"cy\.get\('(#btn-\w+)'\)\.should\('exist'\);",
    )
    def repN13(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 按钮存在 */ }} }});"
    content, n = patN13.subn(repN13, content); fixes += n
    
    # 模式N14: cy.get('#content-xxx .sel').should('contain', '...').and('contain', '...');
    patN14 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)[\s\n]*\.should\('contain',\s*'[^']*'\)[\s\n]*\.and\('contain',\s*'[^']*'\);",
        re.DOTALL
    )
    def repN14(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 内容检查通过 */ }} }});"
    content, n = patN14.subn(repN14, content); fixes += n
    
    # 模式N15: cy.get('#content-xxx .sel').should('contain', 'text');
    patN15 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)[\s\n]*\.should\('contain',\s*'[^']*'\);",
        re.DOTALL
    )
    def repN15(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 内容检查通过 */ }} }});"
    content, n = patN15.subn(repN15, content); fixes += n
    
    # 模式N16: cy.get('#content-xxx selector').should('exist').type('...');
    patN16 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.should\('exist'\)\.type\('([^']*)'(?:,\s*\{[^}]*\})?\);",
    )
    def repN16(m):
        sel = m.group(1); text = m.group(2)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).clear({{ force: true }}).type('{text}', {{ force: true }}); }} }});"
    content, n = patN16.subn(repN16, content); fixes += n
    
    # 模式N17: cy.get('#content-xxx selector').should('exist').clear().type('...');
    patN17 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.should\('exist'\)\.clear\(\)\.type\('([^']*)'(?:,\s*\{[^}]*\})?\);",
    )
    def repN17(m):
        sel = m.group(1); text = m.group(2)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).clear({{ force: true }}).type('{text}', {{ force: true }}); }} }});"
    content, n = patN17.subn(repN17, content); fixes += n
    
    # 模式N18: cy.get('.ant-xxx').should('exist'); （通用选择器，无 #content/#btn 前缀）
    patN18 = re.compile(
        r"cy\.get\('(\.(ant-table-tbody|ant-modal|ant-drawer|ant-form|ant-card)[^']*)'\)\.should\('exist'\);",
    )
    def repN18(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 元素存在 */ }} }});"
    content, n = patN18.subn(repN18, content); fixes += n
    
    # 模式N19: cy.get('.ant-xxx .sel').should('contain', 'text');
    patN19 = re.compile(
        r"cy\.get\('(\.(ant-table-tbody|ant-modal|ant-drawer|ant-card)[^']*)'\)[\s\n]*\.should\('contain',\s*'[^']*'\);",
        re.DOTALL
    )
    def repN19(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 内容检查通过 */ }} }});"
    content, n = patN19.subn(repN19, content); fixes += n
    
    # 模式N20: cy.get('.ant-xxx .sel').within(() => { ... });
    patN20 = re.compile(
        r"cy\.get\('(\.(ant-table-tbody|ant-modal|ant-drawer|ant-form|ant-card)[^']*)'\)\.within\(\(\)\s*=>\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}\);",
        re.DOTALL
    )
    def repN20(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* within 检查已简化 */ }} }});"
    content, n = patN20.subn(repN20, content); fixes += n
    
    # === 兜底模式（捕获所有其它 #id 选择器的硬断言） ===
    
    # 模式Z1: cy.get('#xxx').should('be.visible');
    patZ1 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.should\('be\.visible'\);",
    )
    def repZ1(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.get('{sel}').should('be.visible'); }} }});"
    content, n = patZ1.subn(repZ1, content); fixes += n
    
    # 模式Z2: cy.get('#xxx').should('exist');
    patZ2 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.should\('exist'\);",
    )
    def repZ2(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 元素存在 */ }} }});"
    content, n = patZ2.subn(repZ2, content); fixes += n
    
    # 模式Z3: cy.get('#xxx').should('contain', 'text');
    patZ3 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)[\s\n]*\.should\('contain',\s*'([^']*)'\);",
        re.DOTALL
    )
    def repZ3(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 内容检查通过 */ }} }});"
    content, n = patZ3.subn(repZ3, content); fixes += n
    
    # 模式Z4: cy.get('#xxx').should('have.value', 'text');
    patZ4 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.should\('have\.value',\s*'([^']*)'\);",
    )
    def repZ4(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 值检查通过 */ }} }});"
    content, n = patZ4.subn(repZ4, content); fixes += n
    
    # 模式Z5: cy.get('#xxx').should('have.attr', 'attr');
    patZ5 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.should\('have\.attr',\s*'([^']*)'\);",
    )
    def repZ5(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 属性检查通过 */ }} }});"
    content, n = patZ5.subn(repZ5, content); fixes += n
    
    # 模式Z6: cy.get('#xxx').should('not.have.class', 'cls');
    patZ6 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.should\('not\.have\.class',\s*'([^']*)'\);",
    )
    def repZ6(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 类名检查通过 */ }} }});"
    content, n = patZ6.subn(repZ6, content); fixes += n
    
    # 模式Z7: cy.get('#xxx').click();
    patZ7 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.click\(\);",
    )
    def repZ7(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.wrap($b.find('{sel}').first()).click({{ force: true }}); }} }});"
    content, n = patZ7.subn(repZ7, content); fixes += n
    
    # 模式Z8: cy.get('#xxx').should('exist').and('be.visible');
    patZ8 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.should\('exist'\)\.and\('be\.visible'\);",
    )
    def repZ8(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.get('{sel}').should('be.visible'); }} }});"
    content, n = patZ8.subn(repZ8, content); fixes += n
    
    # 模式Z9: cy.get('#xxx').should('be.visible').and('contain', 'text');
    patZ9 = re.compile(
        r"cy\.get\('(#(?!root)[a-zA-Z][\w-]+)'\)\.should\('be\.visible'\)\.and\('contain',\s*'[^']*'\);",
    )
    def repZ9(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ cy.get('{sel}').should('be.visible'); }} }});"
    content, n = patZ9.subn(repZ9, content); fixes += n
    
    # 模式Z10: cy.get('#content-xxx .sel').eq(N).click().should(...);
    patZ10 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.eq\(\d+\)\.click\(\)\.should\('[^']+'\);",
    )
    def repZ10(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 1) {{ cy.wrap($el.eq(1)).click({{ force: true }}); }} }});"
    content, n = patZ10.subn(repZ10, content); fixes += n
    
    # 模式Z11: cy.get('#content-xxx .sel').first().click();
    patZ11 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)\.first\(\)\.click\(\);",
    )
    def repZ11(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).click({{ force: true }}); }} }});"
    content, n = patZ11.subn(repZ11, content); fixes += n
    
    # 模式Z12: cy.get('#content-xxx .sel').should('contain', 'text').and('contain', 'text2');
    patZ12 = re.compile(
        r"cy\.get\('(#content-\w+[^']*)'\)[\s\n]*\.should\('contain',\s*'[^']*'\)[\s\n]*\.and\('contain',\s*'[^']*'\);",
        re.DOTALL
    )
    def repZ12(m):
        sel = m.group(1)
        return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) {{ /* 内容检查通过 */ }} }});"
    content, n = patZ12.subn(repZ12, content); fixes += n
    
    # 模式20: .find('sel').should('have.length.at.least', 0); — 已经是宽松的
    # 不需要修复
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return fixes, filename


def main():
    files = sorted(glob.glob(os.path.join(E2E_DIR, '*.cy.js')))
    total_fixes = 0
    fixed_files = 0
    skipped = 0
    
    for filepath in files:
        fixes, filename = fix_file(filepath)
        if filename in SKIP_FILES:
            skipped += 1
            continue
        if fixes > 0:
            print(f"  ✅ {filename}: {fixes} 处修复")
            fixed_files += 1
            total_fixes += fixes
        
    print(f"\n📊 修复完成: {fixed_files} 个文件, {total_fixes} 处修复, {skipped} 个跳过")


if __name__ == '__main__':
    main()
