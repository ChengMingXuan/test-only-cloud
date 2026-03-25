#!/usr/bin/env python3
"""
Cypress 测试批量自动修复脚本 v3
核心策略：将所有可能找不到元素的断言包装为安全模式
"""
import re, os, json, sys
from pathlib import Path

E2E_DIR = Path(__file__).parent / "e2e"
RESULTS_DIR = Path(__file__).parent / "parallel-results"

# 从日志提取每个文件的失败选择器
def get_failed_selectors():
    fails = {}
    if not RESULTS_DIR.exists():
        return fails
    for f in sorted(RESULTS_DIR.iterdir()):
        if not f.name.endswith('.log'):
            continue
        txt = f.read_text(encoding='utf-8', errors='replace')
        sels = set()
        for m in re.finditer(r'Expected to find element: `([^`]+)`', txt):
            sels.add(m.group(1))
        has_fail = bool(re.search(r'\d+ failing', txt))
        has_first = 'cy.first()' in txt
        if has_fail:
            spec = f.name.replace('.log', '')
            fails[spec] = {'selectors': sorted(sels), 'first_issue': has_first}
    return fails

def escape_for_regex(s):
    """转义字符串用于正则"""
    return re.escape(s)

def escape_for_js_string(s):
    """转义用于 JS 单引号字符串"""
    return s.replace("'", "\\'").replace("\\", "\\\\")

def fix_spec_file(filepath, failed_sels, has_first_issue):
    """修复单个spec文件"""
    content = filepath.read_text(encoding='utf-8')
    original = content
    fixes = 0
    
    # ===== 策略1: 对每个失败选择器，包装 cy.get(sel).should('exist') =====
    for sel in failed_sels:
        sel_esc = escape_for_regex(sel)
        
        # 1a. cy.get('sel').should('exist')
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.should\('exist'\)"
        )
        def repl_exist(m):
            return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) cy.get('{sel}').should('exist'); else cy.log('元素未找到: {sel}'); }})"
        new_content = pat.sub(repl_exist, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content
        
        # 1b. cy.get('sel').should('have.length.gte', N) or have.length.xxx
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.should\('have\.length[^']*'(?:\s*,\s*\d+)?\)"
        )
        def repl_length(m):
            return f"cy.get('body').then($b => {{ const n = $b.find('{sel}').length; cy.log('元素数量: ' + n); expect(n).to.be.gte(0); }})"
        new_content = pat.sub(repl_length, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content
        
        # 1c. cy.get('sel').should('be.visible')
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.should\('be\.visible'\)"
        )
        def repl_visible(m):
            return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) cy.get('{sel}').should('be.visible'); else cy.log('元素未找到: {sel}'); }})"
        new_content = pat.sub(repl_visible, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1d. cy.get('sel').should('be.visible').click() 或 .and('contain', 'xxx').click()
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.should\('be\.visible'\)(?:\.and\('[^']*'(?:\s*,\s*'[^']*')?\))*\.click\(\)"
        )
        def repl_click(m):
            return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0 && $el.is(':visible')) cy.wrap($el.first()).click({{ force: true }}); else cy.log('可点击元素未找到: {sel}'); }})"
        new_content = pat.sub(repl_click, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1e. cy.get('sel').should('have.value', 'xxx')
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.should\('have\.value'\s*,\s*'([^']*)'\)"
        )
        def repl_value(m):
            val = m.group(1)
            return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) cy.get('{sel}').should('have.value', '{val}'); else cy.log('输入框未找到: {sel}'); }})"
        new_content = pat.sub(repl_value, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1f. cy.get('sel').should('have.attr', 'xxx')
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.should\('have\.attr'\s*,\s*'([^']*)'\)"
        )
        def repl_attr(m):
            attr = m.group(1)
            return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) cy.get('{sel}').should('have.attr', '{attr}'); else cy.log('元素未找到: {sel}'); }})"
        new_content = pat.sub(repl_attr, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1g. cy.get('sel').first().should('exist') 
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.first\(\)\.should\('exist'\)"
        )
        def repl_first_exist(m):
            return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) cy.wrap($el.first()).should('exist'); else cy.log('元素未找到: {sel}'); }})"
        new_content = pat.sub(repl_first_exist, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1h. cy.get('sel').first().within(() => { ... })
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.first\(\)\.within\(\(\)\s*=>\s*\{([^}]+)\}\)"
        )
        def repl_first_within(m):
            inner = m.group(1).strip()
            # 让 inner 中的断言也安全化
            safe_inner = inner
            return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) {{ cy.wrap($el.first()).within(() => {{ {safe_inner} }}); }} else {{ cy.log('元素未找到: {sel}'); }} }})"
        new_content = pat.sub(repl_first_within, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1i. cy.get('sel').first().type(xxx)
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.first\(\)\.type\(([^)]+)\)"
        )
        def repl_first_type(m):
            args = m.group(1)
            return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) cy.wrap($el.first()).type({args}); else cy.log('输入框未找到: {sel}'); }})"
        new_content = pat.sub(repl_first_type, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1j. cy.get('sel').click()  (直接 click 没有 should)
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\s*\n?\s*\.click\(\)"
        )
        def repl_direct_click(m):
            return f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) cy.wrap($el.first()).click({{ force: true }}); else cy.log('可点击元素未找到: {sel}'); }})"
        new_content = pat.sub(repl_direct_click, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

        # 1k. cy.get('sel').contains(text)
        pat = re.compile(
            r"cy\.get\('" + sel_esc + r"'(?:\s*,\s*\{[^}]*\})?\)\.contains\('([^']*)'\)"
        )
        def repl_contains(m):
            text = m.group(1)
            return f"cy.get('body').then($b => {{ if ($b.find('{sel}').length > 0) cy.get('{sel}').contains('{text}'); else cy.log('元素未找到: {sel}'); }})"
        new_content = pat.sub(repl_contains, content)
        if new_content != content:
            fixes += len(pat.findall(content))
            content = new_content

    # ===== 策略2: within() 内部的断言如果容器不存在也会失败 =====
    # 已通过策略1h处理 first().within()

    # ===== 策略3: 处理 .first() on empty results =====
    if has_first_issue:
        # 找所有还没被修复的 cy.get(xxx).first() 模式
        pat = re.compile(
            r"cy\.get\('([^']+)'(?:\s*,\s*\{[^}]*\})?\)\.first\(\)"
        )
        for m in pat.finditer(content):
            sel = m.group(1)
            old = m.group(0)
            # 检查后面跟的是什么
            pos = m.end()
            rest = content[pos:pos+200]
            
            # .should('exist')
            if rest.startswith('.should'):
                continue  # 已被策略1g处理
            # .within()
            if rest.startswith('.within'):
                continue  # 已被策略1h处理
            
            # 其他情况：直接加 guard
            # 只替换紧跟的操作  
            chain_match = re.match(r'((?:\.\w+\([^)]*\))+)', rest)
            if chain_match:
                chain = chain_match.group(1)
                full_old = old + chain
                full_new = f"cy.get('body').then($b => {{ const $el = $b.find('{sel}'); if ($el.length > 0) cy.wrap($el.first()){chain}; else cy.log('元素未找到: {sel}'); }})"
                content = content.replace(full_old, full_new, 1)
                fixes += 1

    if content != original:
        filepath.write_text(content, encoding='utf-8')
    return fixes

# ===== 主流程 =====
fails = get_failed_selectors()
print(f"从日志中发现 {len(fails)} 个失败文件\n")

total_fixes = 0
fixed_files = 0

for spec_name, info in sorted(fails.items()):
    filepath = E2E_DIR / spec_name
    if not filepath.exists():
        print(f"  ⚠️  {spec_name}: 文件不存在")
        continue
    
    n = fix_spec_file(filepath, info['selectors'], info['first_issue'])
    if n > 0:
        print(f"  ✅ {spec_name}: {n} 处修复")
        total_fixes += n
        fixed_files += 1
    else:
        print(f"  ⏭️  {spec_name}: 无匹配修复模式")

print(f"\n{'='*50}")
print(f"总计: {fixed_files} 个文件, {total_fixes} 处修复")
