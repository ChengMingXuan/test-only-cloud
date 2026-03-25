"""批量运行 Cypress 测试并报告结果"""
import subprocess
import re
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

specs = sys.argv[1:] if len(sys.argv) > 1 else [
    "e2e/03-station.cy.js",
    "e2e/04-device.cy.js",
    "e2e/05-permission.cy.js",
    "e2e/06-workorder.cy.js",
    "e2e/07-user.cy.js",
    "e2e/08-navigation.cy.js",
    "e2e/09-energy.cy.js",
    "e2e/10-charging-monitor.cy.js",
]

results = []
for spec in specs:
    name = os.path.basename(spec)
    print(f"\n{'='*60}")
    print(f"运行: {name}")
    print(f"{'='*60}")
    
    proc = subprocess.run(
        ["npx", "cypress", "run", "--config-file", "cypress.fast.config.js",
         "--spec", spec, "--config", "retries=0"],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        timeout=180, shell=True
    )
    output = proc.stdout + proc.stderr
    
    # 解析结果
    passing = 0
    failing = 0
    total = 0
    m_pass = re.search(r'Passing:\s+(\d+)', output)
    m_fail = re.search(r'Failing:\s+(\d+)', output)
    m_total = re.search(r'Tests:\s+(\d+)', output)
    if m_pass: passing = int(m_pass.group(1))
    if m_fail: failing = int(m_fail.group(1))
    if m_total: total = int(m_total.group(1))
    
    status = "PASS" if failing == 0 and passing > 0 else "FAIL"
    results.append((name, passing, failing, total, status))
    print(f"  结果: {passing}/{total} 通过, {failing} 失败 [{status}]")
    
    # 如果有失败，打印错误摘要
    if failing > 0:
        errors = re.findall(r'(?:AssertionError|CypressError|Error):.*', output)
        for err in errors[:3]:
            print(f"  错误: {err[:120]}")

print(f"\n{'='*60}")
print(f"📊 汇总报告")
print(f"{'='*60}")
total_pass = sum(r[1] for r in results)
total_fail = sum(r[2] for r in results)
total_tests = sum(r[3] for r in results)
for name, p, f, t, s in results:
    icon = "✅" if s == "PASS" else "❌"
    print(f"  {icon} {name}: {p}/{t} 通过" + (f", {f} 失败" if f else ""))

print(f"\n  总计: {total_pass}/{total_tests} 通过, {total_fail} 失败")
print(f"  通过率: {total_pass/total_tests*100:.1f}%" if total_tests > 0 else "")
