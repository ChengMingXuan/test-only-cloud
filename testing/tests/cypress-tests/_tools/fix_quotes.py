"""修复 CSS 属性选择器中的引号冲突问题。
问题：cy.get('[class*='table']') - 单引号内嵌套单引号导致 JS 语法错误
修复：将属性选择器值的引号改为双引号 [class*="table"] 或去掉引号
"""
import re
import os
import glob


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    fixes = 0
    
    # 修复 cy.get('...') 中的嵌套单引号问题
    # 模式: cy.get('...[attr='value']...')  → cy.get("...[attr='value']...")
    # 更好的方式: 将属性选择器中的引号改为不引号或双引号
    
    # 方法：找到所有 cy.get('...') 调用，检查内部是否有嵌套的单引号
    def fix_get_quotes(match):
        nonlocal fixes
        full = match.group(0)
        prefix = match.group(1)  # cy.get(
        selector = match.group(2)  # 选择器内容
        suffix = match.group(3)  # ' 或 ', {
        
        # 检查选择器内是否有嵌套的单引号（属性选择器）
        if "'" in selector:
            # 将 [attr='value'] 中的单引号去掉 → [attr=value]
            fixed = re.sub(r"\[([^\]]*?)='([^']*?)'\]", r'[\1=\2]', selector)
            if fixed != selector:
                fixes += 1
                return f"{prefix}{fixed}{suffix}"
        return full
    
    # 匹配 cy.get('...选择器...')  和 cy.get('...选择器...', {
    content = re.sub(
        r"""(cy\.get\(')(.*?)('(?:,\s*\{|\)))""",
        fix_get_quotes,
        content,
        flags=re.DOTALL
    )
    
    # 同样修复 .find('...') .within('...') .contains('...') 等
    for method in ['find', 'within', 'filter', 'closest', 'parents', 'children', 'siblings']:
        content = re.sub(
            rf"""(\.{method}\(')(.*?)('(?:,\s*\{{|\)))""",
            fix_get_quotes,
            content,
            flags=re.DOTALL
        )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return fixes
    return 0


def main():
    e2e_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'e2e')
    files = sorted(glob.glob(os.path.join(e2e_dir, '*.cy.js')))
    
    total_fixed = 0
    total_fixes = 0
    
    for filepath in files:
        fixes = fix_file(filepath)
        if fixes:
            filename = os.path.basename(filepath)
            total_fixed += 1
            total_fixes += fixes
            print(f"✅ {filename}: {fixes} 处引号修复")
    
    print(f"\n📊 总计: 修复了 {total_fixed} 个文件，共 {total_fixes} 处引号冲突")


if __name__ == '__main__':
    main()
