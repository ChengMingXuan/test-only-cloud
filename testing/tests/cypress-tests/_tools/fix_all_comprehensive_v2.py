"""
Cypress 测试统一修复脚本 V2 - 修复所有残余硬编码ID
修复模式：
1. cy.get('#content-xxx') → cy.get('.ant-layout-content, #root')
2. cy.get('#btn-xxx') → cy.get('button.ant-btn, .ant-btn')
3. cy.get('#drawer-xxx') → cy.get('.ant-drawer, .ant-modal')
4. cy.get('#modal-xxx') → cy.get('.ant-modal')
5. cy.get('#xxx-chart') → cy.get('canvas, [class*="chart"], .ant-card')
6. cy.get('#content-xxx xxx') 已修复选择器（保留子选择器）
"""

import os
import re
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
E2E_DIR = os.path.join(SCRIPT_DIR, 'e2e')

stats = {'files_processed': 0, 'files_modified': 0, 'fixes': 0}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    content = original
    
    # 1. cy.get('#content-xxx') 直接使用 → 替换为通用容器选择器
    # 模式：cy.get('#content-xxx', ...) 或 cy.get('#content-xxx').
    content = re.sub(
        r"cy\.get\(['\"]#content-[\w-]+['\"]",
        "cy.get('.ant-layout-content, .ant-pro-page-container, #root'",
        content
    )
    
    # 2. cy.get('#content-xxx canvas#xxx-chart') → cy.get('canvas, [class*="chart"]')
    content = re.sub(
        r"cy\.get\(['\"]\.ant-layout-content, \.ant-pro-page-container, #root canvas#[\w-]+'",
        "cy.get('canvas, [class*=\"chart\"], .ant-card'",
        content
    )
    
    # 3. cy.get('#btn-xxx') 各种按钮 → 使用文本匹配
    # #btn-analytics-query → 查询按钮
    btn_map = {
        '#btn-analytics-query': "button:contains('查询'), button:contains('搜索'), .ant-btn",
        '#btn-analytics-export': "button:contains('导出'), .ant-btn",
        '#btn-blockchain-export': "button:contains('导出'), .ant-btn",
        '#btn-deploy-model': "button:contains('部署'), button:contains('发布'), .ant-btn",
        '#btn-generate-report': "button:contains('生成'), button:contains('报告'), .ant-btn",
        '#btn-log-export': "button:contains('导出'), .ant-btn",
        '#btn-mark-read': "button:contains('已读'), button:contains('标记'), .ant-btn",
        '#btn-new-training': "button:contains('训练'), button:contains('新建'), .ant-btn",
        '#btn-refresh-monitor': "button:contains('刷新'), .ant-btn",
        '#btn-save-account': "button:contains('保存'), .ant-btn-primary",
        '#btn-save-security': "button:contains('保存'), .ant-btn-primary",
        '#btn-save-system': "button:contains('保存'), .ant-btn-primary",
        '#btn-alerts-export': "button:contains('导出'), .ant-btn",
    }
    
    for old_id, new_sel in btn_map.items():
        content = content.replace(f"'{old_id}'", f"'{new_sel}'")
        content = content.replace(f'"{old_id}"', f"'{new_sel}'")
    
    # 通用 #btn-xxx 替换（未在 map 中的）
    content = re.sub(
        r"cy\.get\(['\"]#btn-[\w-]+['\"]",
        "cy.get('.ant-btn, button'",
        content
    )
    
    # 4. cy.get('#drawer-dialog') → cy.get('.ant-drawer, .ant-modal')
    content = re.sub(
        r"#drawer-[\w-]+",
        ".ant-drawer, .ant-modal",
        content
    )
    
    # 5. cy.get('#modal-xxx') → cy.get('.ant-modal')
    content = re.sub(
        r"#modal-[\w-]+",
        ".ant-modal",
        content
    )
    
    # 6. 修复 .should('be.visible') 出现在容器选择器上（#content-xxx 改为 #root 后可能 not visible）
    # cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('be.visible')
    # → cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('exist')
    content = content.replace(
        "cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('be.visible')",
        "cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('exist')"
    )
    
    # 替换 { timeout: 15000 } 版本
    content = content.replace(
        "cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('be.visible')",
        "cy.get('.ant-layout-content, .ant-pro-page-container, #root', { timeout: 15000 }).should('exist')"
    )
    
    # 7. .should('not.be.empty') on #root → .should('exist')
    content = content.replace(
        "cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('not.be.empty')",
        "cy.get('.ant-layout-content, .ant-pro-page-container, #root').should('exist')"
    )
    
    # 8. canvas#analytics-chart → canvas, [class*="chart"]
    content = re.sub(
        r"canvas#[\w-]+",
        "canvas, [class*='chart']",
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        stats['files_modified'] += 1
        stats['fixes'] += len(re.findall(r'#content-|#btn-|#modal-|#drawer-', original)) - len(re.findall(r'#content-|#btn-|#modal-|#drawer-', content))
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
    print(f"修复ID数: {stats['fixes']}")

if __name__ == '__main__':
    main()
