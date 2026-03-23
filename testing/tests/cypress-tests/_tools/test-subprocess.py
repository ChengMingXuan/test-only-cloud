import subprocess, os, re
CYPRESS_CMD = r'd:\2026\aiops.v2\tests\cypress-tests\node_modules\.bin\cypress.cmd'
try:
    result = subprocess.run(
        [CYPRESS_CMD, 'run', '--spec', 'e2e/01-login.cy.js', '--reporter', 'spec'],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=r'd:\2026\aiops.v2\tests\cypress-tests', timeout=120
    )
    print(f'returncode: {result.returncode}')
    print(f'stdout len: {len(result.stdout)}')
    print(f'stderr len: {len(result.stderr)}')
    pass_match = re.search(r'(\d+)\s+passing', result.stdout)
    fail_match = re.search(r'(\d+)\s+failing', result.stdout)
    p = pass_match.group(1) if pass_match else 'none'
    f = fail_match.group(1) if fail_match else 'none'
    print(f'passing: {p}')
    print(f'failing: {f}')
except Exception as e:
    print(f'ERROR: {e}')
