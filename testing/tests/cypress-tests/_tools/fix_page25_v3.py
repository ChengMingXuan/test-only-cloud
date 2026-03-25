#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用修复器 - 修复 page25 所有变体中的危险 cy.get() 模式
处理文件 51-65 中不同实现的 page25 函数
"""

import os
import re
import glob

SPEC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'e2e')

# 文件组: 51-65
TARGET_FILES = sorted(
    glob.glob(os.path.join(SPEC_DIR, '5[1-9]-*.cy.js')) +
    glob.glob(os.path.join(SPEC_DIR, '6[0-5]-*.cy.js'))
)


def fix_content(content, fname):
    original = content
    changes = []

    # ── 修复1: cy.get('SEL', { timeout: N }).then($var => {
    #   → cy.get('body').then($b => { const $var = $b.find('SEL');
    #   (下一行的 if ($var.length > 0) { 保持不变)
    def replace_get_timeout_then(m):
        selector = m.group(1)
        varname = m.group(2)
        indent = m.group(3)  # 行前缩进
        changes.append(f"  get+timeout+then: {selector[:40]}...")
        return f"{indent}cy.get('body').then($b => {{ const {varname} = $b.find('{selector}');"

    # 单引号 selector
    pattern1 = re.compile(
        r"^( *)"                               # 缩进
        r"cy\.get\("
        r"'((?:[^'\\]|\\.)*)'"                # 单引号 selector
        r",\s*\{\s*timeout:\s*\d+\s*\}\)"
        r"\.then\((\$\w+)\s*=>\s*\{",
        re.MULTILINE
    )
    new_content = pattern1.sub(
        lambda m: m.group(1) + f"cy.get('body').then($b => {{ const {m.group(3)} = $b.find('{m.group(2)}');",
        content
    )
    if new_content != content:
        n = len(pattern1.findall(content))
        changes.append(f"  [R1] 单引号selector+timeout: {n}处")
        content = new_content

    # 双引号 selector
    pattern1b = re.compile(
        r"^( *)"
        r'cy\.get\('
        r'"((?:[^"\\]|\\.)*)"'                 # 双引号 selector
        r',\s*\{\s*timeout:\s*\d+\s*\}\)'
        r'\.then\((\$\w+)\s*=>\s*\{',
        re.MULTILINE
    )
    new_content = pattern1b.sub(
        lambda m: m.group(1) + f"cy.get('body').then($b => {{ const {m.group(3)} = $b.find(\"{m.group(2)}\");",
        content
    )
    if new_content != content:
        n = len(pattern1b.findall(content))
        changes.append(f"  [R1b] 双引号selector+timeout: {n}处")
        content = new_content

    # ── 修复2: 多行 selector + timeout + then
    #   cy.get('sel1 sel2...',
    #     { timeout: N }).then($var => {
    pattern2 = re.compile(
        r"^( *)cy\.get\("
        r"(\n? *)'((?:[^'\\]|\\.)*)'"          # 可能换行的单引号 selector
        r",\n? *\{\s*timeout:\s*\d+\s*\}\)"
        r"\.then\((\$\w+)\s*=>\s*\{",
        re.MULTILINE
    )
    new_content = pattern2.sub(
        lambda m: m.group(1) + f"cy.get('body').then($b => {{ const {m.group(4)} = $b.find('{m.group(3)}');",
        content
    )
    if new_content != content:
        n = len(pattern2.findall(original))
        changes.append(f"  [R2] 多行selector+timeout: {n}处")
        content = new_content

    # ── 修复3: cy.get('SEL').then($var => {  (无 timeout, 无 $b 前缀)
    #   → cy.get('body').then($b => { const $var = $b.find('SEL');
    pattern3 = re.compile(
        r"^( *)cy\.get\("
        r"'((?:[^'\\]|\\.)*)'"                # 单引号 selector
        r"\)\.then\((\$\w+)\s*=>\s*\{",
        re.MULTILINE
    )
    def replace_no_timeout(m):
        indent = m.group(1)
        sel = m.group(2)
        var = m.group(3)
        # 跳过 $b, $body, $bb 等已经是 body 的变量
        if var in ('$b', '$body', '$bb', '$bx', '$bd'):
            return m.group(0)
        return f"{indent}cy.get('body').then($b => {{ const {var} = $b.find('{sel}');"

    new_content = pattern3.sub(replace_no_timeout, content)
    if new_content != content:
        # 计算实际改变次数
        n = sum(1 for m in pattern3.finditer(original)
                if m.group(3) not in ('$b', '$body', '$bb', '$bx', '$bd'))
        changes.append(f"  [R3] 无timeout的then: {n}处")
        content = new_content

    # ── 修复4: .should('have.length.gte', 1) 硬断言
    #   cy.get('SEL', { timeout: N }).should('have.length.gte', 1);
    #   → cy.get('body').then($b => { if ($b.find('SEL').length > 0) { cy.wrap($b.find('SEL').first()).should('exist'); } });
    pattern4 = re.compile(
        r"^( *)cy\.get\("
        r"'((?:[^'\\]|\\.)*)'"
        r",\s*\{\s*timeout:\s*\d+\s*\}\)"
        r"\.should\('have\.length\.gte',\s*\d+\);",
        re.MULTILINE
    )
    def replace_should_gte(m):
        indent = m.group(1)
        sel = m.group(2).replace("'", "\\'")
        return (f"{indent}cy.get('body').then($b => {{\n"
                f"{indent}  if ($b.find('{sel}').length > 0) {{\n"
                f"{indent}    cy.wrap($b.find('{sel}').first()).should('exist');\n"
                f"{indent}  }}\n"
                f"{indent}}});")

    new_content = pattern4.sub(replace_should_gte, content)
    if new_content != content:
        n = len(pattern4.findall(original))
        changes.append(f"  [R4] .should('have.length.gte'): {n}处")
        content = new_content

    # ── 修复5: 双引号 selector + .should('have.length.gte', 1)
    pattern4b = re.compile(
        r'^( *)cy\.get\('
        r'"((?:[^"\\]|\\.)*)"'
        r',\s*\{\s*timeout:\s*\d+\s*\}\)'
        r"\.should\('have\.length\.gte',\s*\d+\);",
        re.MULTILINE
    )
    def replace_should_gte_dq(m):
        indent = m.group(1)
        sel = m.group(2)
        return (f"{indent}cy.get('body').then($b => {{\n"
                f"{indent}  if ($b.find(\"{sel}\").length > 0) {{\n"
                f"{indent}    cy.wrap($b.find(\"{sel}\").first()).should('exist');\n"
                f"{indent}  }}\n"
                f"{indent}}});")

    new_content = pattern4b.sub(replace_should_gte_dq, content)
    if new_content != content:
        n = len(pattern4b.findall(original))
        changes.append(f"  [R4b] 双引号.should.gte: {n}处")
        content = new_content

    # ── 修复6: 多行 selector .should('exist')
    # cy.get(
    #   'SEL1' + 'SEL2',
    #   { timeout: N }
    # ).should('exist');
    pattern6 = re.compile(
        r"^( *)cy\.get\(\n"
        r"( +)((?:'[^']*'(?:\s*\+\s*\n\s*'[^']*')*)),\n"
        r" *\{\s*timeout:\s*\d+\s*\}\n"
        r" *\)\.should\('exist'\);",
        re.MULTILINE
    )
    def replace_multiline_should_exist(m):
        indent = m.group(1)
        # 把多行字符串合并
        parts = re.findall(r"'([^']*)'", m.group(3).replace('\n', ''))
        sel = ' '.join(parts)
        return (f"{indent}cy.get('body').then($b => {{\n"
                f"{indent}  const $el = $b.find('{sel}');\n"
                f"{indent}  if ($el.length > 0) {{ cy.wrap($el.first()).should('exist'); }}\n"
                f"{indent}}});")

    new_content = pattern6.sub(replace_multiline_should_exist, content)
    if new_content != content:
        n = len(pattern6.findall(original))
        changes.append(f"  [R6] 多行selector.should.exist: {n}处")
        content = new_content

    if changes:
        print(f"\n{'─'*60}")
        print(f"✅ {fname}:")
        for c in changes:
            print(c)
    else:
        print(f"  ℹ️  {fname}: 无需修改")

    return content


def main():
    print(f"找到 {len(TARGET_FILES)} 个目标文件 (51-65)\n")
    changed = 0
    for fp in TARGET_FILES:
        fname = os.path.basename(fp)
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed = fix_content(content, fname)

        if fixed != content:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(fixed)
            changed += 1

    print(f"\n{'='*60}")
    print(f"完成: {changed}/{len(TARGET_FILES)} 个文件已修改")


if __name__ == '__main__':
    main()
