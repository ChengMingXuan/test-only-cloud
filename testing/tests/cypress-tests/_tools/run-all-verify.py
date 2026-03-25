"""
自动运行全部 Cypress 测试文件并收集结果。
"""
import subprocess, glob, os, re, sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
E2E_DIR = os.path.join(TESTS_DIR, 'e2e')

files = sorted(glob.glob(os.path.join(E2E_DIR, '*.cy.js')))

results = []
total_pass = 0
total_fail = 0
failed_files = []

for i, fpath in enumerate(files):
    fname = os.path.basename(fpath)
    print(f"[{i+1}/{len(files)}] 运行 {fname}...", end=" ", flush=True)
    
    proc = subprocess.run(
        ['npx.cmd', 'cypress', 'run', '--config-file', 'cypress.fast.config.js', '--spec', fpath],
        capture_output=True, text=True, cwd=TESTS_DIR, timeout=300
    )
    
    output = proc.stdout + proc.stderr
    
    # 提取通过/失败数
    m = re.search(r'(\d+)\s+(\d+)\s+(\d+|-)\s+(\d+|-)\s+(\d+|-)', output)
    if m:
        tests = int(m.group(1))
        passing = int(m.group(2))
        failing = int(m.group(3)) if m.group(3) != '-' else 0
    else:
        # 尝试另一种格式
        m2 = re.search(r'通过 (\d+).*失败 (\d+).*总计 (\d+)', output)
        if m2:
            passing = int(m2.group(1))
            failing = int(m2.group(2))
            tests = int(m2.group(3))
        else:
            tests = 0; passing = 0; failing = -1
    
    total_pass += passing
    total_fail += max(failing, 0)
    
    if failing > 0:
        # 提取具体失败用例
        fail_matches = re.findall(r'(\d+\).*?)(?=\n\s*\d+\)|$)', output, re.DOTALL)
        error_lines = [line.strip() for line in output.split('\n') if 'AssertionError' in line or 'Timed out' in line]
        failed_files.append((fname, failing, error_lines[:3]))
        print(f"❌ {passing}/{tests} ({failing} 失败)")
    elif failing == 0:
        print(f"✅ {passing}/{tests}")
    else:
        print(f"⚠️ 解析失败")
    
    results.append((fname, tests, passing, failing))

print(f"\n{'='*60}")
print(f"📊 总计: {total_pass} 通过, {total_fail} 失败, {total_pass+total_fail} 总计")
print(f"📁 {len(files)} 个文件, {len(failed_files)} 个有失败")

if failed_files:
    print(f"\n❌ 失败文件详情:")
    for fname, count, errors in failed_files:
        print(f"  {fname}: {count} 个失败")
        for err in errors:
            print(f"    - {err[:120]}")
