# -*- coding: utf-8 -*-
"""分析并行测试的失败模式，为batch-fix-v4提供输入"""
import re, os, json

log_dir = 'parallel-results'
fail_data = {}

for fname in os.listdir(log_dir):
    if not fname.endswith('.log'):
        continue
    spec = fname.replace('.log', '')
    fpath = os.path.join(log_dir, fname)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Find failed test count
    failed_tests = re.findall(r'(\d+)\s+failing', content)
    if not failed_tests or int(failed_tests[0]) == 0:
        continue

    # Find actual test titles that failed
    titles = re.findall(r'^\s+\d+\)\s+(.+)$', content, re.MULTILINE)
    errors = re.findall(r'(?:AssertionError|CypressError|Timed out.+?|Error):\s*(.+?)(?:\r?\n|$)', content)

    fail_data[spec] = {
        'count': int(failed_tests[0]),
        'titles': titles[:15],
        'errors': errors[:10]
    }

print(f"共 {len(fail_data)} 个失败 spec")
for spec in sorted(fail_data.keys()):
    d = fail_data[spec]
    c = d['count']
    print(f"\n=== {spec} ({c} failures) ===")
    for t in d['titles']:
        print(f"  T: {t}")
    for e in d['errors'][:5]:
        print(f"  E: {e[:120]}")
