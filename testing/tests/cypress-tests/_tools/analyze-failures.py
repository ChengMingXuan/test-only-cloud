"""分析已完成的并行测试结果，提取失败原因分类"""
import re, os, json
from pathlib import Path
from collections import Counter

RESULTS_DIR = Path(__file__).parent / "parallel-results"

error_patterns = Counter()
spec_errors = {}

for log_file in sorted(RESULTS_DIR.glob("*.cy.js.log")):
    content = log_file.read_text(encoding='utf-8', errors='replace')
    spec = log_file.name.replace('.log', '')
    
    # 检查是否有失败
    fail_match = re.search(r'(\d+)\s+failing', content)
    if not fail_match:
        continue
    
    failing = int(fail_match.group(1))
    if failing == 0:
        continue
    
    # 提取失败的测试名和错误
    errors = []
    # 匹配模式: N) 测试名
    test_failures = re.findall(r'^\s+\d+\)\s+(.+)$', content, re.MULTILINE)
    # 匹配错误详情
    error_details = re.findall(r'(AssertionError|CypressError|TypeError|Error):?\s*(.+?)(?:\n|$)', content)
    
    for detail in error_details:
        err_type = detail[0]
        err_msg = detail[1].strip()[:150]
        error_patterns[err_msg] += 1
        errors.append(f"{err_type}: {err_msg}")
    
    spec_errors[spec] = {
        "failing": failing,
        "test_names": test_failures[:20],
        "errors": errors[:10]
    }

print(f"=== 已分析 {len(spec_errors)} 个失败 spec ===\n")

for spec, info in sorted(spec_errors.items()):
    print(f"❌ {spec} (failing={info['failing']})")
    for t in info['test_names'][:5]:
        print(f"  测试: {t}")
    for e in info['errors'][:3]:
        print(f"  错误: {e[:120]}")
    print()

print(f"\n=== 错误模式统计 (Top 20) ===")
for pattern, count in error_patterns.most_common(20):
    print(f"  [{count:3d}次] {pattern[:120]}")
