"""修复 :contains('中文') 引号冲突问题"""
import re
import glob
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
files = glob.glob('e2e/*.cy.js')
fixed = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    # 修复 :contains('xxx') 中单引号嵌套问题
    # 将 :contains('xxx') 替换为 :contains("xxx")
    pattern = r""":contains\('([^']*(?:'[^']*)*?)'\)"""
    # 更简单的方法：匹配 contains(' 到下一个 ') 
    new_content = content
    
    # 逐行处理，找到 contains(' 模式
    lines = content.split('\n')
    new_lines = []
    changed = False
    for line in lines:
        # 匹配 :contains('中文词') 模式 — 单引号嵌套在单引号字符串中
        if ":contains('" in line and "cy.get(" in line:
            # 提取 contains 中的文本
            new_line = re.sub(r":contains\('([^)]+?)'\)", r':contains("\1")', line)
            if new_line != line:
                changed = True
                line = new_line
        new_lines.append(line)
    
    if changed:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(new_lines))
        fixed += 1
        print(f"  修复: {os.path.basename(f)}")

print(f"\n共修复 {fixed} 个文件")
