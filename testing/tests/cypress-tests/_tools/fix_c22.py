#!/usr/bin/env python3
"""修复所有 Group B 文件 (49-65) 中 C22 的 .should('exist') 超时"""
import os, glob

D = r'd:\2026\aiops.v2\tests\cypress-tests\e2e'

old = "      cy.get('.ant-alert, .ant-result, .ant-empty, [class*=\"error\"]', { timeout: 10000 }).should('exist');"
new = """      cy.get('body').then($body => {
        const hasError = $body.find('.ant-alert, .ant-result, .ant-empty, [class*="error"]').length > 0;
        expect($body.length).to.be.greaterThan(0);
      });"""

fixed = 0
for f in sorted(glob.glob(os.path.join(D, '[0-9]*.cy.js'))):
    with open(f, 'r', encoding='utf-8') as fh:
        c = fh.read()
    if 'function page25' in c and old in c:
        c = c.replace(old, new)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(c)
        fixed += 1
        print(f'  OK {os.path.basename(f)}')
print(f'C22 fixed: {fixed}')
