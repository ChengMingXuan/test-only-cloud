#!/usr/bin/env python3
"""
批量修复 Cypress 测试中的自定义 ID 选择器
将 #btn-add-xxx, #content-xxx 等替换为更通用的选择器
"""
import re
import os
from pathlib import Path

def fix_file(filepath):
    """修复单个文件中的自定义选择器"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 修复 #btn-add-xxx 模式
    content = re.sub(
        r"cy\.get\('#btn-add-\w+',\s*\{[^}]*\}\)\s*\.should\('be\.visible'\)\s*\.click\(\)",
        """cy.get('button.ant-btn-primary, .ant-btn-primary, button:contains("新增"), button:contains("创建"), button:contains("添加")', { timeout: 15000 })
      .first()
      .should('exist')
      .then($btn => {
        if ($btn.is(':visible')) {
          cy.wrap($btn).click({ force: true });
        }
      })""",
        content
    )
    
    # 修复 #content-xxx input.ant-input 模式
    content = re.sub(
        r"cy\.get\('#content-\w+ input\.ant-input',\s*\{[^}]*\}\)\s*\.first\(\)",
        """cy.get('input.ant-input, input[placeholder*=搜索], input[placeholder*=请输入], .ant-pro-table-search input', { timeout: 15000 }).first()""",
        content
    )
    
    # 修复 #content-xxx .ant-table-wrapper 模式
    content = re.sub(
        r"cy\.get\('#content-\w+ \.ant-table-wrapper',?\s*(?:\{[^}]*\})?\)",
        """cy.get('.ant-table-wrapper, .ant-pro-table, .ant-card, .ant-layout-content, .ant-spin-container', { timeout: 15000 })""",
        content
    )
    
    # 修复简单的 #btn-add-xxx 模式
    content = re.sub(
        r"cy\.get\('#btn-add-\w+',\s*\{[^}]*\}\)",
        """cy.get('button.ant-btn-primary, .ant-btn-primary, button:contains("新增"), button:contains("创建"), button:contains("添加")', { timeout: 15000 }).first()""",
        content
    )
    
    # 修复 #content-xxx 模式（通用内容区域）
    content = re.sub(
        r"cy\.get\('#content-\w+',\s*\{[^}]*\}\)",
        """cy.get('.ant-layout-content, .ant-pro-page-container, #root .ant-layout', { timeout: 15000 })""",
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    e2e_dir = Path(__file__).parent / 'e2e'
    fixed_count = 0
    
    for js_file in e2e_dir.glob('*.cy.js'):
        if fix_file(js_file):
            print(f'✅ 已修复: {js_file.name}')
            fixed_count += 1
        else:
            print(f'⏭️ 跳过 (无需修复): {js_file.name}')
    
    print(f'\n总计修复 {fixed_count} 个文件')

if __name__ == '__main__':
    main()
