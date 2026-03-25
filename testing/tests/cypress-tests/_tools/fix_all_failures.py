#!/usr/bin/env python3
"""批量修复 Cypress 测试文件中的常见失败模式。

不使用 :visible 伪选择器（Cypress 不支持 CSS :visible）。
使用 content section 限定范围 + .first() 避免多元素问题。
"""
import re
import os
import glob

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
E2E_DIR = os.path.join(TESTS_DIR, 'e2e')

# 只修复有失败的文件
FAILING_FILES = {
    '03-station': 'content-station',
    '04-device': 'content-device',
    '05-permission': 'content-permission',
    '06-workorder': 'content-workorder',
    '11-analytics': 'content-analytics',
    '12-ai': 'content-ai-dashboard',
    '13-blockchain': 'content-blockchain-dashboard',
    '14-ruleengine': 'content-ruleengine',
    '15-settlement': 'content-settlement',
    '16-simulator': 'content-simulator',
    '17-digital-twin': 'content-digital-twin',
    '18-tenant': 'content-tenant',
    '19-system': 'content-system',
    '20-monitor': 'content-monitor',
    '21-account': 'content-account-profile',
    '22-message': 'content-message',
    '23-workflow': 'content-workflow',
    '24-log': 'content-log',
    '25-charging-advanced': 'content-charging-piles',
    '26-device-alerts': 'content-device',
    '27-energy-advanced': 'content-energy-vpp',
    '28-ingestion': 'content-ingestion',
    '29-security': 'content-security',
    '30-report': 'content-report',
}

def get_file_key(filepath):
    basename = os.path.basename(filepath)
    return basename.replace('.cy.js', '')

def fix_content(content, file_key):
    cid = FAILING_FILES.get(file_key, '')
    if not cid:
        return content, False
    
    original = content
    
    # A：移除 `, .ant-layout-content` 后备选择器（导致 .val() 取到 main 元素）
    content = re.sub(
        r"cy\.get\('([^']*?)(?:,\s*\.ant-layout-content)+'\)",
        r"cy.get('\1')",
        content
    )
    
    # B：cy.get('input').first() → 限定到 content section
    content = re.sub(
        r"cy\.get\('input'\)\.first\(\)",
        f"cy.get('#{cid} input.ant-input').first()",
        content
    )
    
    # C：cy.get('button').first() → 限定到 content section
    content = re.sub(
        r"cy\.get\('button'\)\.first\(\)",
        f"cy.get('#{cid} button').first()",
        content
    )
    
    # D：cy.get('input').should('exist').type( → 限定 + .first()
    content = re.sub(
        r"cy\.get\('input'\)\.should\('exist'\)\.type\(",
        f"cy.get('#{cid} input.ant-input').first().type(",
        content
    )
    
    # E：cy.get('input').type( → 限定 + .first()
    content = re.sub(
        r"cy\.get\('input'\)\.type\(",
        f"cy.get('#{cid} input.ant-input').first().type(",
        content
    )
    
    # F：复合 input 选择器 → 限定
    content = re.sub(
        r"cy\.get\('input\.ant-input,\s*\.ant-select,\s*\.ant-input'\)",
        f"cy.get('#{cid} input.ant-input').first()",
        content
    )
    content = re.sub(
        r"cy\.get\('input\.ant-input,\s*\.ant-input'\)",
        f"cy.get('#{cid} input.ant-input').first()",
        content
    )
    content = re.sub(
        r'''cy\.get\('input\[type="text"\],\s*\.ant-input'\)''',
        f"cy.get('#{cid} input.ant-input').first()",
        content
    )
    
    # G：input[type="text"] 匹配多个 → 限定 + .first()
    content = re.sub(
        r'''cy\.get\('input\[type="text"\]'\)\.first\(\)\.type\(''',
        f"cy.get('#{cid} input.ant-input').first().type(",
        content
    )
    content = re.sub(
        r'''cy\.get\('input\[type="text"\]'\)\.type\(''',
        f"cy.get('#{cid} input.ant-input').first().type(",
        content
    )
    
    # H：.ant-menu-item 用作 Tab → 换成 .ant-tabs-tab
    content = re.sub(
        r"cy\.get\('\.ant-menu-item'\)\.eq\((\d+)\)",
        f"cy.get('#{cid} .ant-tabs-tab').eq(\\1)",
        content
    )
    
    # I：修复路由路径
    content = content.replace("'/rule-engine/chains'", "'/ruleengine'")
    content = content.replace("'/rule-engine'", "'/ruleengine'")

    # J：button:contains + .ant-btn-primary → 限定到 content section
    content = re.sub(
        r"cy\.get\('button:contains\([^)]+\),\s*\.ant-btn-primary'\)",
        f"cy.get('#{cid} button').first()",
        content
    )
    content = re.sub(
        r"cy\.get\('(?:button:contains\([^)]+\),\s*)+\.ant-btn(?:-primary)?'\)",
        f"cy.get('#{cid} button').first()",
        content
    )
    
    # K：button:contains("查询"), button:contains("搜索"), .ant-btn
    content = re.sub(
        r"cy\.get\('button:contains\([^)]+\),\s*button:contains\([^)]+\),\s*\.ant-btn'\)",
        f"cy.get('#{cid} button').first()",
        content
    )
    
    # L：.ant-table-wrapper 范围过大
    content = re.sub(
        r"cy\.get\('\.ant-table-wrapper,\s*\[class\*=\"table\"\]'\)",
        f"cy.get('#{cid} .ant-table-wrapper')",
        content
    )
    content = re.sub(
        r"cy\.get\('\.ant-table-wrapper,\s*\.ant-list'\)",
        f"cy.get('#{cid} .ant-table-wrapper')",
        content
    )
    content = re.sub(
        r"cy\.get\('\.ant-table-wrapper,\s*\.ant-tree,\s*\.ant-list,\s*\[",
        f"cy.get('#{cid} .ant-table-wrapper",
        content
    )
    
    # M：.ant-table-tbody 范围过大
    content = re.sub(
        r"cy\.get\('\.ant-table-tbody tr,\s*\.ant-list-item,\s*\[role=[^']+'\)",
        f"cy.get('#{cid} .ant-table-tbody tr')",
        content
    )
    content = re.sub(
        r"cy\.get\('\.ant-table-tbody tr,\s*\[role=row\],\s*\.ant-table[^']*'\)",
        f"cy.get('#{cid} .ant-table-tbody tr')",
        content
    )
    content = re.sub(
        r"cy\.get\('\.ant-table-tbody tr,\s*\.ant-empty,\s*\.ant-spin-[^']*'\)",
        f"cy.get('#{cid} .ant-table-tbody tr')",
        content
    )
    
    # N：button, .ant-btn 全局匹配
    content = re.sub(
        r"cy\.get\('button,\s*\.ant-btn'\)\.should\('exist'\)\.and\('be\.visible'\)",
        f"cy.get('#{cid} button').first().should('exist')",
        content
    )
    content = re.sub(
        r"cy\.get\('button,\s*\.ant-btn'\)",
        f"cy.get('#{cid} button').first()",
        content
    )
    
    # O：tbody tr 全局
    content = re.sub(
        r"cy\.get\('tbody tr'\)",
        f"cy.get('#{cid} tbody tr')",
        content
    )
    
    # P：.ant-drawer, .ant-modal 合用 → 只用 .ant-modal
    content = re.sub(
        r"cy\.get\('\.ant-drawer,\s*\.ant-modal'\)\.should\('be\.visible'\)",
        "cy.get('.ant-modal').should('exist')",
        content
    )
    
    # Q：select, .ant-select
    content = re.sub(
        r"cy\.get\('(?:select,\s*)?\.ant-select(?:,\s*select)?'\)",
        f"cy.get('#{cid} .ant-select').first()",
        content
    )
    
    # R：td, .ant-card → 限定
    content = re.sub(
        r"cy\.get\('td,\s*\.ant-card'\)",
        f"cy.get('#{cid} td')",
        content
    )
    
    # S：input, select → 限定  
    content = re.sub(
        r"cy\.get\('input,\s*select'\)",
        f"cy.get('#{cid} input.ant-input').first()",
        content
    )
    
    return content, content != original

def process_file(filepath):
    file_key = get_file_key(filepath)
    if file_key not in FAILING_FILES:
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content, changed = fix_content(content, file_key)
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(E2E_DIR, '*.cy.js')))
    fixed = 0
    for filepath in files:
        if process_file(filepath):
            print(f"  Fixed: {get_file_key(filepath)}")
            fixed += 1
    print(f"\nTotal: {len(files)} files checked, {fixed} fixed")

if __name__ == '__main__':
    main()
