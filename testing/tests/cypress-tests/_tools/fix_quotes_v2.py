"""修复 CSS 属性选择器中的嵌套引号冲突。
将 [attr*='value'] 改为 [attr*=value]（CSS 属性选择器的值如果是简单词不需要引号）
"""
import re
import os
import glob


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 替换 CSS 属性选择器中的单引号值
    # [class*='table'] → [class*=table]
    # [color='green'] → [color=green]
    # [attr='value'] → [attr=value]
    # [attr*='value'] → [attr*=value]
    # [attr^='value'] → [attr^=value]
    # [attr$='value'] → [attr$=value]
    # [attr~='value'] → [attr~=value]
    content = re.sub(
        r"\[([a-zA-Z\-]+)([*^$~|]?=)'([^'\]]+)'\]",
        r"[\1\2\3]",
        content
    )
    
    if content != original:
        count = len(re.findall(r"\[([a-zA-Z\-]+)([*^$~|]?=)'([^'\]]+)'\]", original))
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return count
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
