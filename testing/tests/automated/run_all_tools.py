"""
五工具联合测试运行器
按顺序执行5种测试工具，聚合结果，输出联合报告
"""
import subprocess, sys, json, time, os
from datetime import datetime

ROOT = r"D:\2026\aiops.v2"
TEST_DIR = os.path.join(ROOT, "tests", "automated")
RESULT_DIR = os.path.join(ROOT, "TestResults")
os.makedirs(RESULT_DIR, exist_ok=True)

summary = {
    "timestamp": datetime.now().isoformat(),
    "tools": {},
    "overall": {"total": 0, "passed": 0, "failed": 0, "warnings": 0, "skipped": 0}
}

def run_tool(name, cmd, cwd, result_file=None):
    """运行测试工具并捕获结果"""
    print(f"\n{'='*60}")
    print(f"  运行 {name}")
    print(f"{'='*60}")
    start = time.time()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
        elapsed = round(time.time() - start, 1)
        output = proc.stdout + proc.stderr
        print(output[-3000:] if len(output) > 3000 else output)

        tool_result = {"status": "completed", "duration_s": elapsed, "returncode": proc.returncode}

        # 尝试读取 JSON 结果文件
        if result_file and os.path.isfile(result_file):
            with open(result_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            tool_result["total"] = data.get("total", 0)
            tool_result["passed"] = data.get("passed", 0)
            tool_result["failed"] = data.get("failed", 0)
            tool_result["warnings"] = data.get("warnings", 0)
        elif name == "pytest":
            # 从 stdout 解析 pytest 摘要
            for line in output.split("\n"):
                if "passed" in line:
                    import re
                    m = re.search(r"(\d+) passed", line)
                    if m: tool_result["passed"] = int(m.group(1))
                    m = re.search(r"(\d+) failed", line)
                    if m: tool_result["failed"] = int(m.group(1))
                    m = re.search(r"(\d+) skipped", line)
                    if m: tool_result["skipped"] = int(m.group(1))
                    tool_result["total"] = tool_result.get("passed",0) + tool_result.get("failed",0) + tool_result.get("skipped",0)

        summary["tools"][name] = tool_result
        # 累加到总体
        for k in ("total", "passed", "failed", "warnings"):
            summary["overall"][k] += tool_result.get(k, 0)
        summary["overall"]["skipped"] += tool_result.get("skipped", 0)

        return tool_result
    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - start, 1)
        tool_result = {"status": "timeout", "duration_s": elapsed}
        summary["tools"][name] = tool_result
        print(f"[超时] {name} 超过 300s")
        return tool_result
    except Exception as e:
        tool_result = {"status": "error", "error": str(e)}
        summary["tools"][name] = tool_result
        print(f"[错误] {name}: {e}")
        return tool_result


# ── 工具1: pytest ──
run_tool(
    "pytest",
    [sys.executable, "-m", "pytest", "--tb=short", "-q", "--no-header", "-x", "--timeout=30"],
    cwd=TEST_DIR,
)

# ── 工具2: k6 ──
k6_exe = r"C:\Program Files\k6\k6.exe"
run_tool(
    "k6",
    [k6_exe, "run", "--summary-export", os.path.join(RESULT_DIR, "k6-results.json"),
     os.path.join(TEST_DIR, "k6_perf_test.js")],
    cwd=ROOT,
    result_file=None,  # k6 结果手动解析
)
# 手动补 k6 统计
k6_json = os.path.join(RESULT_DIR, "k6-results.json")
if os.path.isfile(k6_json):
    with open(k6_json, "r", encoding="utf-8") as f:
        k6d = json.load(f)
    metrics = k6d.get("metrics", {})
    http_fails = metrics.get("http_req_failed", {}).get("values", {}).get("rate", 0)
    total_reqs = int(metrics.get("http_reqs", {}).get("values", {}).get("count", 0))
    failed_reqs = int(total_reqs * http_fails)
    summary["tools"]["k6"]["total"] = total_reqs
    summary["tools"]["k6"]["passed"] = total_reqs - failed_reqs
    summary["tools"]["k6"]["failed"] = failed_reqs
    summary["overall"]["total"] += total_reqs
    summary["overall"]["passed"] += (total_reqs - failed_reqs)
    summary["overall"]["failed"] += failed_reqs

# ── 工具3: PowerShell ──
run_tool(
    "powershell",
    ["powershell", "-ExecutionPolicy", "Bypass", "-File",
     os.path.join(TEST_DIR, "ps_infra_test.ps1")],
    cwd=ROOT,
    result_file=os.path.join(RESULT_DIR, "ps-infra-results.json"),
)

# ── 工具4: psql ──
run_tool(
    "psql",
    [sys.executable, os.path.join(TEST_DIR, "psql_db_test.py")],
    cwd=TEST_DIR,
    result_file=os.path.join(RESULT_DIR, "psql-db-results.json"),
)

# ── 工具5: security ──
run_tool(
    "security",
    [sys.executable, os.path.join(TEST_DIR, "security_test.py")],
    cwd=TEST_DIR,
    result_file=os.path.join(RESULT_DIR, "security-results.json"),
)

# ── 汇总 ──
combined_path = os.path.join(RESULT_DIR, "combined-results.json")
with open(combined_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"  五工具联合测试汇总")
print(f"{'='*60}")
for name, tr in summary["tools"].items():
    status_icon = "✅" if tr.get("failed", 0) == 0 else "❌"
    print(f"  {status_icon} {name:12s} | 耗时 {tr.get('duration_s','?')}s | "
          f"通过 {tr.get('passed','-')} | 失败 {tr.get('failed','-')} | 警告 {tr.get('warnings','-')}")

ov = summary["overall"]
print(f"\n  总计: {ov['total']} | 通过: {ov['passed']} | 失败: {ov['failed']} | 警告: {ov['warnings']} | 跳过: {ov['skipped']}")
print(f"  结果: {combined_path}")
