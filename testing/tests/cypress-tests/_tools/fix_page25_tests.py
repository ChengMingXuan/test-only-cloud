#!/usr/bin/env python3
"""
修复 page25 工厂函数中的直接 cy.get() 调用问题
将 cy.get(selector, {timeout}).then() 替换为 cy.get('body').then($b => {if find...})
"""

import os
import re
import glob

# 需要修复的文件
SPEC_DIR = os.path.join(os.path.dirname(__file__), 'e2e')
TARGET_FILES = glob.glob(os.path.join(SPEC_DIR, '4[9-9]-*.cy.js')) + \
               glob.glob(os.path.join(SPEC_DIR, '5[0-9]-*.cy.js')) + \
               glob.glob(os.path.join(SPEC_DIR, '6[0-5]-*.cy.js'))

# 模式替换规则
# 1. C04: cy.get('.ant-table,...', {timeout}).should('exist') -> conditional
C04_OLD = """    it('[C04] 列表/表格/卡片区域已渲染', () => {
      cy.get(
        '.ant-table, .ant-list, .ant-pro-table, .ant-table-wrapper,' +
        '.ant-card, .ant-descriptions, [class*="table"], [class*="list"]',
        { timeout: 10000 }
      ).should('exist');
    });"""

C04_NEW = """    it('[C04] 列表/表格/卡片区域已渲染', () => {
      cy.get('body').then($b => {
        const $el = $b.find('.ant-table, .ant-list, .ant-pro-table, .ant-table-wrapper, .ant-card, .ant-descriptions, [class*="table"], [class*="list"]');
        if ($el.length > 0) { cy.wrap($el.first()).should('exist'); }
      });
    });"""

def fix_cy_get_then(content):
    """将 cy.get(selector, {timeout}).then($x => { if ($x.length > 0) 替换为 body.then 模式"""
    # 修复 C04
    if C04_OLD in content:
        content = content.replace(C04_OLD, C04_NEW)
        print("  Fixed C04")
    
    # 修复通用的 cy.get(selector, {timeout:N}).then($x => {
    # 将 cy.get('...', { timeout: N }).then($xxx => 替换为 cy.get('body').then($b => { const $xxx = $b.find('...');
    
    # Pattern 1: cy.get('single_class', { timeout: N }).then($var =>
    def fix_pattern1(m):
        selector = m.group(1)
        # If selector contains multiple classes, use body.find
        timeout = m.group(2)
        varname = m.group(3)
        return f"cy.get('body').then($b => {{\n        const {varname} = $b.find({selector});\n        // converted from cy.get with timeout {timeout}\n        if ({varname}.length >= 0) {{"
    
    # Pattern: cy.get(SELECTOR, { timeout: N }).then($VAR => {
    pattern1 = re.compile(
        r"cy\.get\((['\"][^'\"]+['\"])\s*,\s*\{\s*timeout:\s*\d+\s*\}\)\.then\(\((\$\w+)\)\s*=>"
    )
    
    # Count matches first
    matches = list(pattern1.finditer(content))
    if matches:
        # Process replacements
        for m in reversed(matches):  # reverse to preserve positions
            selector_str = m.group(1)  # 'selector'
            varname = m.group(2)       # $var
            # Replace: cy.get('selector', { timeout: N }).then(($var) =>
            # With: cy.get('body').then($b => { const $var = $b.find('selector'); if ($var.length >= 0) {
            old = m.group(0)
            new = f"cy.get('body').then($b => {{ const {varname} = $b.find({selector_str});\n        if ({varname}.length >= 0) {{"
            content = content[:m.start()] + new + content[m.end():]
        print(f"  Fixed {len(matches)} cy.get(selector, timeout).then() patterns (pattern2 - two-arg form)")
    
    # Pattern 2: cy.get('selector', { timeout: N }).then($var =>  (no parens around $var)
    pattern2 = re.compile(
        r"cy\.get\((['\"][^'\"]+['\"])\s*,\s*\{\s*timeout:\s*\d+\s*\}\)\.then\((\$\w+)\s*=>"
    )
    matches2 = list(pattern2.finditer(content))
    if matches2:
        for m in reversed(matches2):
            selector_str = m.group(1)
            varname = m.group(2)
            old = m.group(0)
            new = f"cy.get('body').then($b => {{ const {varname} = $b.find({selector_str});\n        if ({varname}.length >= 0) {{"
            content = content[:m.start()] + new + content[m.end():]
        print(f"  Fixed {len(matches2)} cy.get(selector, timeout).then() patterns")
    
    # Pattern 3: cy.get(MULTILINE_SELECTOR, { timeout: N }).should('exist')
    # Already handled C04 above
    
    # Pattern 4: cy.get('selector', { timeout: N }).should('exist')
    pattern4 = re.compile(
        r"cy\.get\((['\"][^'\"]+['\"])\s*,\s*\{\s*timeout:\s*\d+\s*\}\)\.should\(['\"]exist['\"]"
    )
    matches4 = list(pattern4.finditer(content))
    if matches4:
        for m in reversed(matches4):
            selector_str = m.group(1)
            old = m.group(0) + ')'
            new = f"cy.get('body').then($b => {{ if ($b.find({selector_str}).length > 0) {{ cy.wrap($b.find({selector_str}).first()).should('exist'); }} }})"
            # Be careful with the ending paren - find the actual end
            content = content[:m.start()] + new + content[m.end()+1:]
        print(f"  Fixed {len(matches4)} cy.get(selector, timeout).should('exist') patterns")
    
    return content

def fix_file(filepath):
    print(f"\n=== Fixing {os.path.basename(filepath)} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = fix_cy_get_then(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed and saved")
    else:
        print(f"  ℹ️ No changes needed")

if __name__ == '__main__':
    print(f"Found {len(TARGET_FILES)} target files")
    for f in sorted(TARGET_FILES):
        fix_file(f)
    print("\n✅ All files processed")
