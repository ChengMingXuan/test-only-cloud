#!/usr/bin/env python3
"""解析 Cypress 全量运行日志，提取失败的 spec 文件和测试用例"""
import re
import os

log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'cypress-full-run.log')
if not os.path.exists(log_path):
    log_path = os.path.join(os.path.dirname(__file__), 'full-run.log')

with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# 提取 Run Finished 之后的摘要
summary_match = re.search(r'Run Finished.*', text, re.DOTALL)
summary = summary_match.group(0) if summary_match else ""

# 提取失败 spec - 匹配带 X 标记的行
fail_specs = re.findall(r'[^\w](e2e/\S+\.cy\.js)\s', summary)
# 也尝试从整体提取
if not fail_specs:
    fail_specs = re.findall(r'Spec\s+.*?(e2e/\S+\.cy\.js).*?[Ff]ail', text)

# 从 "Spec" 表格提取 - 查找有失败数的行
table_fails = []
for line in summary.split('\n'):
    # 匹配带失败数(非0)的行: ✖ spec-name  duration  passed  failed
    m = re.search(r'(e2e/\S+\.cy\.js)', line)
    if m:
        # 检查这行是否有失败标记
        if any(c in line for c in ['✖', '×', 'fail']):
            table_fails.append(m.group(1))
        elif re.search(r'\d+\s+of\s+\d+\s+failed', line):
            table_fails.append(m.group(1))

all_fails = sorted(set(fail_specs + table_fails))

# 提取失败的测试用例 - 从每个 spec 的输出中找
fail_tests = re.findall(r'^\s+\d+\)\s+(.+)$', text, re.MULTILINE)

print(f"=== 失败的 spec 文件 ({len(all_fails)}) ===")
for s in all_fails:
    print(f"  {s}")

print(f"\n=== 失败的测试用例 ({len(fail_tests)}) ===")
for t in fail_tests[:100]:
    print(f"  {t}")

# 找未运行的 spec
all_specs = sorted(os.listdir(os.path.join(os.path.dirname(__file__), 'e2e')))
all_specs = [f"e2e/{s}" for s in all_specs if s.endswith('.cy.js')]
mentioned_specs = set(re.findall(r'(e2e/\S+\.cy\.js)', text))
not_run = [s for s in all_specs if s not in mentioned_specs]
if not_run:
    print(f"\n=== 未运行的 spec ({len(not_run)}) ===")
    for s in not_run:
        print(f"  {s}")

# 统计总览
pass_specs = []
for line in summary.split('\n'):
    m = re.search(r'(e2e/\S+\.cy\.js)', line)
    if m and '✓' in line:
        pass_specs.append(m.group(1))

print(f"\n=== 总览 ===")
print(f"总 spec 文件: {len(all_specs)}")
print(f"已运行: {len(mentioned_specs)}")
print(f"通过: {len(pass_specs)}")
print(f"失败: {len(all_fails)}")
print(f"未运行: {len(not_run)}")
