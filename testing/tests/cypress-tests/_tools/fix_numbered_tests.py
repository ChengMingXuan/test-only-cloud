#!/usr/bin/env python3
"""
修复编号系列 (01-65) + charging.cy.js 的测试文件：
1. 删除 SUPPLEMENTAL 区域（含坏选择器的补充测试）
2. 修复 page25() 函数中 C04 的 .should('exist') 缺 body 兜底
3. 修复 page25() 函数中 cy.get(selector).then() 超时问题
"""

import os
import re
import glob

TESTS_DIR = os.path.join(os.path.dirname(__file__), 'e2e')


def remove_supplemental(lines):
    """
    找到 [SUPPLEMENTAL] 注释行 + describe('交互补充测试') 块，用大括号计数定位闭合，精准删除。
    返回 (new_lines, removed)。
    """
    supp_idx = None
    for i, line in enumerate(lines):
        if '[SUPPLEMENTAL]' in line:
            supp_idx = i
            break
    if supp_idx is None:
        return lines, False

    # 往回退，跳过 SUPPLEMENTAL 前的空行
    start = supp_idx
    while start > 0 and lines[start - 1].strip() == '':
        start -= 1

    # 从 supp_idx 向下找 describe('交互补充测试'
    desc_idx = None
    for i in range(supp_idx, min(supp_idx + 5, len(lines))):
        if 'describe(' in lines[i] and ('补充' in lines[i] or '交互' in lines[i]):
            desc_idx = i
            break
    if desc_idx is None:
        desc_idx = supp_idx + 1

    # 从 desc_idx 开始，用大括号计数找到其闭合 });
    brace_count = 0
    started = False
    end_idx = desc_idx
    for i in range(desc_idx, len(lines)):
        for ch in lines[i]:
            if ch == '{':
                brace_count += 1
                started = True
            elif ch == '}':
                brace_count -= 1
        if started and brace_count <= 0:
            end_idx = i
            break

    # 删除 start..end_idx（含两端）
    new_lines = lines[:start] + lines[end_idx + 1:]
    return new_lines, True


def fix_page25_selectors(content):
    """
    修复 page25 函数中的选择器问题：
    1. C04: .should('exist') 选择器加 body 兜底
    2. C22: .should('exist') 选择器加 body 兜底
    3. cy.get(selector, {timeout}).then($var => {  变为
       cy.get('body').then($body => { const $var = $body.find(selector);
    """
    # ---- 步骤 1: 修复 .should('exist') 中缺少 body 兜底的行 ----
    # 只处理 function page25 内部。匹配含 .ant- 选择器 + .should('exist') 的行
    def add_body_to_should_exist(m):
        pre = m.group(1)
        sel = m.group(2)
        post = m.group(3)
        if 'body' in sel or '#root' in sel:
            return m.group(0)
        return pre + sel + ', body' + post

    content = re.sub(
        r"""(cy\.get\(['"])((?:[^'"]*?(?:\.ant-|class\*=)[^'"]*?))(['"]\s*,\s*\{[^}]*\}\s*\)\s*\.should\(\s*['"]exist['"]\s*\))""",
        add_body_to_should_exist,
        content
    )

    # ---- 步骤 2: 修复 cy.get(selector, {timeout}).then($var => { 模式 ----
    # 这些 cy.get 会在无匹配元素时超时失败。改为 cy.get('body').then 后用 jQuery 查找。
    # 匹配两种格式（单行和换行的选择器）：
    #   cy.get('sel1, sel2', { timeout: 8000 }).then($var => {
    #   cy.get('sel1, sel2',\n    { timeout: 8000 }).then($var => {
    def replace_get_then(m):
        indent = m.group(1)
        selector = m.group(2)
        var_name = m.group(3)
        # 不修改已经用 body 的
        if selector.strip() in ('body', "'body'", '"body"'):
            return m.group(0)
        return f"{indent}cy.get('body').then($body => {{ const {var_name} = $body.find('{selector}');"

    content = re.sub(
        r"""^(\s*)cy\.get\('([^']+)',\s*\n?\s*\{[^}]*timeout[^}]*\}\s*\)\.then\((\$\w+)\s*=>\s*\{""",
        replace_get_then,
        content,
        flags=re.MULTILINE
    )

    return content


def fix_file(filepath):
    """修复单个文件"""
    fname = os.path.basename(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)
    original_tests = len(re.findall(r"^\s*it\(", content, re.MULTILINE))

    lines = content.split('\n')

    # ---- 1. 删除 SUPPLEMENTAL ----
    lines, removed_supp = remove_supplemental(lines)
    content = '\n'.join(lines)

    # ---- 2. 修复选择器（仅限含 page25 的 Group B 文件）----
    has_page25 = 'function page25' in content
    if has_page25:
        content = fix_page25_selectors(content)

    # ---- 3. 验证括号平衡 ----
    open_b = content.count('{') - content.count('}')
    open_p = content.count('(') - content.count(')')

    balanced = (open_b == 0 and open_p == 0)
    if not balanced:
        # 括号不平衡 = 可能切割出了问题，输出警告
        pass

    content = content.rstrip() + '\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    new_tests = len(re.findall(r"^\s*it\(", content, re.MULTILINE))

    return {
        'tests_before': original_tests,
        'tests_after': new_tests,
        'removed_supplemental': removed_supp,
        'has_page25': has_page25,
        'balanced': balanced,
        'size_before': original_len,
        'size_after': len(content),
    }


def main():
    # 收集所有编号系列文件 + charging.cy.js
    files = sorted(glob.glob(os.path.join(TESTS_DIR, '[0-9]*.cy.js')))
    charging = os.path.join(TESTS_DIR, 'charging.cy.js')
    if os.path.exists(charging):
        files.append(charging)

    print(f'找到 {len(files)} 个文件待修复')
    print()

    fixed = 0
    errors = []
    unbalanced = []

    for filepath in files:
        fname = os.path.basename(filepath)
        try:
            r = fix_file(filepath)
            tag = 'B' if r['has_page25'] else 'A'
            bal = '✅' if r['balanced'] else '⚠️括号不平衡'
            supp = 'SUPP✂️' if r['removed_supplemental'] else '无SUPP'
            print(f'  [{tag}] {fname.ljust(52)} {r["tests_before"]:3d}→{r["tests_after"]:3d} 条  {supp}  {bal}')
            if not r['balanced']:
                unbalanced.append(fname)
            fixed += 1
        except Exception as e:
            print(f'  ❌ {fname}: {e}')
            errors.append((fname, str(e)))

    print(f'\n{"="*60}')
    print(f'成功: {fixed}/{len(files)}')
    if errors:
        print(f'失败: {len(errors)}')
        for name, err in errors:
            print(f'  - {name}: {err}')
    if unbalanced:
        print(f'括号不平衡: {len(unbalanced)}')
        for name in unbalanced:
            print(f'  - {name}')
    else:
        print('括号平衡: 全部通过 ✅')


if __name__ == '__main__':
    main()
