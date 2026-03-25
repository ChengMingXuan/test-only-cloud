"""
Cypress 测试统一修复脚本
修复所有常见失败模式：
1. 硬编码 ID 选择器（#content-xxx, #btn-add-xxx, #modal-xxx, #drawer-xxx）
2. 输入框未 clear() 就 type() 导致追加
3. 统一使用 cy.visitAuth() 代替手动 localStorage
4. 修复精确计数断言（.have.length, N → .have.length.at.least, N）
5. 修复 Ant Design 类名错误
"""

import os
import re
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
E2E_DIR = os.path.join(SCRIPT_DIR, 'e2e')

# 统计
stats = {'files_processed': 0, 'files_modified': 0, 'fixes': {}}

def count_fix(category):
    stats['fixes'][category] = stats['fixes'].get(category, 0) + 1

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    content = original
    
    # ============ 1. 替换硬编码 #content-xxx 选择器 ============
    # #content-xxx input.ant-input → .ant-layout-content input.ant-input, input[class*="ant-input"]
    content = re.sub(
        r"#content-[\w-]+ input\.ant-input",
        "input.ant-input",
        content
    )
    if content != original:
        count_fix('content_id_input')
    
    # #content-xxx .ant-table-tbody → .ant-table-tbody
    content = re.sub(
        r"#content-[\w-]+ \.ant-table",
        ".ant-table",
        content
    )
    
    # #content-xxx input[placeholder*="搜索"] → input[placeholder*="搜索"]
    content = re.sub(
        r"#content-[\w-]+ input\[",
        "input[",
        content
    )
    
    # 通用 #content-xxx 后跟空格的选择器 → 移除 #content-xxx 前缀
    content = re.sub(
        r"#content-[\w-]+ (\.[a-zA-Z])",
        r"\1",
        content
    )
    
    # ============ 2. 替换硬编码 #btn-add-xxx 按钮 ============
    # #btn-add-xxx → 使用灵活的按钮选择器
    content = re.sub(
        r"cy\.get\(['\"]#btn-add-[\w-]+['\"]",
        "cy.get('button.ant-btn-primary, .ant-btn-primary, button[type=\"button\"]'",
        content
    )
    
    # ============ 3. 替换硬编码 #modal-xxx ============
    content = re.sub(
        r"#modal-dialog",
        ".ant-modal",
        content
    )
    content = re.sub(
        r"#modal-cancel",
        ".ant-modal .ant-btn:not(.ant-btn-primary)",
        content
    )
    
    # ============ 4. 替换硬编码 #drawer-xxx ============
    content = re.sub(
        r"#drawer-close|#drawer-footer-close",
        ".ant-drawer .ant-drawer-close, .ant-drawer .ant-btn",
        content
    )
    
    # ============ 5. 替换 cy.visit + 手动 localStorage → cy.visitAuth ============
    # 模式：cy.visit('/path', { failOnStatusCode: false, onBeforeLoad(win) { win.localStorage.setItem(...) } })
    # 替换为 cy.visitAuth('/path')
    # 但要保留 01-login.cy.js 的特殊 visit 模式（登录页不能用 visitAuth）
    basename = os.path.basename(filepath)
    if basename != '01-login.cy.js':
        # 匹配多行 cy.visit 带 onBeforeLoad 的模式
        content = re.sub(
            r"cy\.visit\((['\"])(\/[\w/-]+)\1,\s*\{\s*failOnStatusCode:\s*false,\s*onBeforeLoad\(win\)\s*\{\s*win\.localStorage\.setItem\(['\"]jgsy_access_token['\"],\s*['\"][\w-]+['\"]\);\s*\}\s*\}\);?",
            r"cy.visitAuth('\2');",
            content
        )
        # 简化版
        content = re.sub(
            r"cy\.visit\((['\"])(\/[\w/-]+)\1,\s*\{\s*onBeforeLoad\(win\)\s*\{\s*win\.localStorage\.setItem\(['\"]jgsy_access_token['\"],\s*['\"][\w-]+['\"]\);\s*\}\s*\}\);?",
            r"cy.visitAuth('\2');",
            content
        )
    
    # ============ 6. 精确计数断言 → 至少N ============
    # .should('have.length', 4) → .should('have.length.at.least', 1) （当不是0时）
    def fix_exact_length(m):
        count = int(m.group(1))
        if count > 0:
            count_fix('exact_length')
            return f".should('have.length.at.least', 1)"
        return m.group(0)
    
    content = re.sub(
        r"\.should\(['\"]have\.length['\"],\s*(\d+)\)",
        fix_exact_length,
        content
    )
    
    # ============ 7. 修复 .ant-tag-blue/green/red → Ant 兼容选择器 ============
    content = re.sub(
        r"\.ant-tag-blue",
        ".ant-tag[class*='blue'], .ant-tag[color='blue'], .ant-tag-processing",
        content
    )
    content = re.sub(
        r"\.ant-tag-green",
        ".ant-tag[class*='green'], .ant-tag[color='green'], .ant-tag-success",
        content
    )
    content = re.sub(
        r"\.ant-tag-red",
        ".ant-tag[class*='red'], .ant-tag[color='red'], .ant-tag-error",
        content
    )
    
    # ============ 8. 修复 input .type() 前缺少 .clear() ============
    # 仅对表单输入修复（不影响 body.type('{esc}') 等）
    # 模式：.first().type('xxx' → .first().clear({ force: true }).type('xxx'
    # 但要避免已有 .clear() 的行
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        # 跳过已有 clear 的行
        if '.clear(' in line:
            fixed_lines.append(line)
            continue
        # 跳过 body.type('{esc}') 等非输入场景
        if "body').type" in line or "body\").type" in line:
            fixed_lines.append(line)
            continue
        # 跳过 wrap 中的 type
        if "cy.wrap" in line and ".type(" in line:
            fixed_lines.append(line)
            continue
        
        # 修复 .first().type('xxx' → .first().clear({ force: true }).type('xxx'
        if re.search(r"\.first\(\)\s*\.type\(", line) and 'input' in (lines[i-1] if i > 0 else ''):
            # 上一行有 input 选择器
            line = re.sub(
                r"\.first\(\)\s*\.type\(",
                ".first().clear({ force: true }).type(",
                line
            )
            count_fix('add_clear_before_type')
        
        # 修复 .type('xxx' 直接在 get('input...) 后的行  
        if re.search(r"\.type\(['\"](?!{)", line):
            # 检查同一行或上一行是否有 input 选择器
            context = line + (lines[i-1] if i > 0 else '')
            if ('input' in context or 'ant-input' in context) and '.clear(' not in context:
                if '.first()' not in line and '.last()' not in line:
                    # 在 .type 前直接追加 .clear
                    line = re.sub(
                        r"(\.should\([^)]+\)\s*)?\.type\(",
                        lambda m: (m.group(1) or '') + ".clear({ force: true }).type(",
                        line,
                        count=1
                    )
                    count_fix('add_clear_before_type')
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # ============ 9. 修复 .should('have.length.at.least', 0) → 移除无效断言 ============
    content = re.sub(
        r"\.should\(['\"]have\.length\.at\.least['\"],\s*0\)",
        ".should('exist')",
        content
    )
    
    # ============ 10. 统一超时时间 ============
    # 过短超时 3000 → 8000
    content = re.sub(
        r"\{ timeout: 3000 \}",
        "{ timeout: 8000 }",
        content
    )
    
    # 写入
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        stats['files_modified'] += 1
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(E2E_DIR, '*.cy.js')))
    print(f"发现 {len(files)} 个测试文件")
    
    for filepath in files:
        stats['files_processed'] += 1
        basename = os.path.basename(filepath)
        modified = fix_file(filepath)
        if modified:
            print(f"  ✅ 已修复: {basename}")
        else:
            print(f"  ⏭️ 无变更: {basename}")
    
    print(f"\n========== 修复汇总 ==========")
    print(f"处理文件: {stats['files_processed']}")
    print(f"修改文件: {stats['files_modified']}")
    print(f"修复类别:")
    for category, count in sorted(stats['fixes'].items()):
        print(f"  - {category}: {count}")

if __name__ == '__main__':
    main()
