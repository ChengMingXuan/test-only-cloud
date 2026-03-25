import os

base = r'd:\2026\aiops.v2\tests\cypress-tests\e2e'
files = [
    '53-charging-settle-finance-station.cy.js',
    '54-device-ingestion-ruleengine.cy.js',
    '55-ai-iotcloud-phm.cy.js',
    '56-energy-vpp-microgrid-pvessc.cy.js',
    '57-electrade-carbontrade-demandresp.cy.js',
    '58-energyeff-multienergy-safecontrol-deviceops.cy.js',
    '59-blockchain-digitaltwin.cy.js',
    '60-analytics-builder.cy.js',
    '61-content-portal-mgmt.cy.js',
    '62-tenant-account.cy.js',
    '63-workorder-workflow-developer.cy.js',
    '64-misc-platform.cy.js',
]

replacements = [
    # C08: 分页切换 多余 }); 
    (
        "cy.wrap($nx.first()).click({ force: true }); }); }); }",
        "cy.wrap($nx.first()).click({ force: true }); }); }",
    ),
    # C24: 修复后 }) 变成了 }) 而非 }
    (
        "else cy.get('body').type('{esc}', { force: true }); }); })",
        "else cy.get('body').type('{esc}', { force: true }); }); }",
    ),
]

for fn in files:
    fp = os.path.join(base, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    total_fixes = 0
    for old, new in replacements:
        n = content.count(old)
        if n > 0:
            content = content.replace(old, new)
            total_fixes += n
    if total_fixes > 0:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK   {fn}: {total_fixes} fix(es)')
    else:
        print(f'SKIP {fn}: no pattern matched')

print('\n完成')
