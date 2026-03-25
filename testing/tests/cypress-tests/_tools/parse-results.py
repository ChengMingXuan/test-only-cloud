"""解析 Cypress 测试日志，提取通过/失败的测试文件列表"""
import re, os

log_path = os.path.join(os.path.dirname(__file__), "cypress-full-run.log")
with open(log_path, "r", encoding="utf-8") as f:
    content = f.read()

# 匹配最后的汇总表中的每行
# × = failed, √/✓ = passed
failed = []
passed = []

# 解析 spec 文件行 - 格式如: │ ×  01-login.cy.js  或 │ √  charging.cy.js
for line in content.split("\n"):
    # 失败的 spec
    m = re.search(r'[×✗]\s+([\w\-\.]+\.cy\.js)', line)
    if m:
        spec = m.group(1)
        if spec not in failed:
            failed.append(spec)
        continue
    # 通过的 spec
    m = re.search(r'[√✓]\s+([\w\-\.]+\.cy\.js)', line)
    if m:
        spec = m.group(1)
        if spec not in passed:
            passed.append(spec)

# 去掉已通过的(有些可能同时出现)
failed_only = [f for f in failed if f not in passed]
passed_only = [f for f in passed if f not in failed]
# 同时在两边的
both = [f for f in failed if f in passed]

print(f"=== 失败的测试文件 ({len(failed_only)}) ===")
for f in sorted(failed_only):
    print(f"  FAIL: {f}")

print(f"\n=== 通过的测试文件 ({len(passed_only)}) ===")
for f in sorted(passed_only):
    print(f"  PASS: {f}")

if both:
    print(f"\n=== 既有失败也有通过 ({len(both)}) ===")
    for f in sorted(both):
        print(f"  MIXED: {f}")

# 列出 e2e 目录下所有测试文件
e2e_dir = os.path.join(os.path.dirname(__file__), "e2e")
all_specs = sorted([f for f in os.listdir(e2e_dir) if f.endswith('.cy.js')])
all_in_results = set(failed + passed)
not_run = [f for f in all_specs if f not in all_in_results]
print(f"\n=== 未运行的测试文件 ({len(not_run)}) ===")
for f in not_run:
    print(f"  SKIP: {f}")

print(f"\n=== 总计 ===")
print(f"  总测试文件: {len(all_specs)}")
print(f"  已运行: {len(all_in_results)}")
print(f"  通过: {len(passed_only)}")
print(f"  失败: {len(failed_only)}")
print(f"  混合: {len(both)}")
print(f"  未运行: {len(not_run)}")
