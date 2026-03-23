"""
批量修复 Cypress page25 工厂中的 C08/C24 失败断言
"""
import os
import glob

# 待修复文件
patterns = [
    "e2e/4*.cy.js",
    "e2e/5*.cy.js",
    "e2e/6*.cy.js",
]

BASE = os.path.dirname(__file__)

# ── C08 修复 ──────────────────────────────────────────────────────────────
C08_OLD = """          cy.wrap($p).find('.ant-pagination-next').then($next => {
            if ($next.length > 0 && !$next.hasClass('ant-pagination-disabled')) {
              cy.wrap($next).click({ force: true });
            }
          });"""

C08_NEW = """          cy.get('body').then($body => {
            const $next = $body.find('.ant-pagination-next:not(.ant-pagination-disabled)');
            if ($next.length > 0) cy.wrap($next.first()).click({ force: true });
          });"""

# ── C24 修复 ──────────────────────────────────────────────────────────────
C24_OLD = """              cy.get('.ant-modal-close, .ant-drawer-close').then($close => {
                if ($close.length > 0) cy.wrap($close.first()).click({ force: true });
                else cy.get('button:contains("取消"), button:contains("关闭")').first().click({ force: true });
              });"""

C24_NEW = """              cy.get('body').then($b => {
                const $cl = $b.find('.ant-modal-close, .ant-drawer-close');
                if ($cl.length > 0) cy.wrap($cl.first()).click({ force: true });
                else cy.get('body').type('{esc}', { force: true });
              });"""

fixed = 0
for pattern in patterns:
    for path in glob.glob(os.path.join(BASE, pattern)):
        with open(path, encoding='utf-8') as f:
            content = f.read()

        changed = False
        if C08_OLD in content:
            content = content.replace(C08_OLD, C08_NEW)
            changed = True

        if C24_OLD in content:
            content = content.replace(C24_OLD, C24_NEW)
            changed = True

        if changed:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed += 1
            print(f"Fixed: {os.path.basename(path)}")

print(f"\nTotal: {fixed} files fixed")
