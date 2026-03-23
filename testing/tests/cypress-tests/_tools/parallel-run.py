#!/usr/bin/env python3
"""
并行 Cypress 测试 — 6并行 + 实时进度 + 剩余时间估算
"""
import subprocess, os, sys, json, time, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import threading

CYPRESS_DIR = Path(__file__).parent
E2E_DIR = CYPRESS_DIR / "e2e"
RESULTS_DIR = CYPRESS_DIR / "parallel-results"
RESULTS_DIR.mkdir(exist_ok=True)

# 收集所有测试文件（排除 _debug）
all_specs = sorted([
    f.name for f in E2E_DIR.glob("*.cy.js")
    if not f.name.startswith("_debug")
])
TOTAL = len(all_specs)

# 6并行, 超时600秒
PARALLEL = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TIMEOUT_SEC = 600

CYPRESS_CMD = str(CYPRESS_DIR / "node_modules" / ".bin" / "cypress.cmd")

# 线程安全计数
lock = threading.Lock()
completed_count = 0
passed_count = 0
failed_count = 0
timeout_count = 0
start_all = time.time()
all_results = []

def fmt_time(secs):
    m, s = divmod(int(secs), 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h}h{m:02d}m{s:02d}s"
    return f"{m}m{s:02d}s"

def run_spec(spec_name):
    global completed_count, passed_count, failed_count, timeout_count
    t0 = time.time()
    log_file = RESULTS_DIR / f"{spec_name}.log"
    env = os.environ.copy()
    env["NO_COLOR"] = "1"
    try:
        result = subprocess.run(
            f'"{CYPRESS_CMD}" run --spec "e2e/{spec_name}" --reporter spec',
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            cwd=str(CYPRESS_DIR), timeout=TIMEOUT_SEC, env=env, shell=True
        )
        elapsed = time.time() - t0
        output = result.stdout + "\n" + result.stderr
        log_file.write_text(output, encoding='utf-8')
        pass_m = re.search(r'(\d+)\s+passing', output)
        fail_m = re.search(r'(\d+)\s+failing', output)
        passing = int(pass_m.group(1)) if pass_m else 0
        failing = int(fail_m.group(1)) if fail_m else 0
        status = "PASS" if result.returncode == 0 else "FAIL"
        r = {"spec": spec_name, "status": status, "passing": passing, "failing": failing, "elapsed": round(elapsed, 1)}
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        log_file.write_text(f"TIMEOUT after {TIMEOUT_SEC}s", encoding='utf-8')
        r = {"spec": spec_name, "status": "TIMEOUT", "passing": 0, "failing": 0, "elapsed": round(elapsed, 1)}
    except Exception as e:
        elapsed = time.time() - t0
        r = {"spec": spec_name, "status": "ERROR", "passing": 0, "failing": 0, "elapsed": round(elapsed, 1), "error": str(e)}

    with lock:
        completed_count += 1
        all_results.append(r)
        if r["status"] == "PASS": passed_count += 1
        elif r["status"] == "FAIL": failed_count += 1
        else: timeout_count += 1

        remain = TOTAL - completed_count
        elapsed_total = time.time() - start_all
        avg_per_batch = elapsed_total / (completed_count / PARALLEL) if completed_count >= PARALLEL else elapsed_total
        remain_batches = remain / PARALLEL
        est_remain = remain_batches * avg_per_batch / (completed_count / PARALLEL) if completed_count > 0 else 0
        # 简化估算：平均每个spec耗时 × 剩余 / 并行数
        avg_per_spec = elapsed_total / completed_count
        est_remain = (remain * avg_per_spec) / PARALLEL

        icon = {"PASS": "✅", "FAIL": "❌", "TIMEOUT": "⏰", "ERROR": "💥"}.get(r["status"], "?")
        print(
            f"[{completed_count}/{TOTAL}] {icon} {r['spec']:<42s} "
            f"p={r['passing']} f={r['failing']} {r['elapsed']:.0f}s | "
            f"已完成{completed_count} 剩余{remain} | "
            f"✅{passed_count} ❌{failed_count} ⏰{timeout_count} | "
            f"已用{fmt_time(elapsed_total)} 预计还需{fmt_time(est_remain)}",
            flush=True
        )
    return r

print(f"{'=' * 130}")
print(f"Cypress 并行测试 — 共 {TOTAL} 个文件, {PARALLEL} 并行, 单文件超时 {TIMEOUT_SEC}s")
print(f"{'=' * 130}")

with ThreadPoolExecutor(max_workers=PARALLEL) as executor:
    futures = {executor.submit(run_spec, spec): spec for spec in all_specs}
    for future in as_completed(futures):
        future.result()

elapsed_total = time.time() - start_all
p = [r for r in all_results if r["status"] == "PASS"]
f = [r for r in all_results if r["status"] == "FAIL"]
t = [r for r in all_results if r["status"] == "TIMEOUT"]
e = [r for r in all_results if r["status"] == "ERROR"]
total_pass_cases = sum(r["passing"] for r in all_results)
total_fail_cases = sum(r["failing"] for r in all_results)

print(f"\n{'=' * 130}")
print(f"全部完成! 总耗时: {fmt_time(elapsed_total)}")
print(f"Spec: ✅通过 {len(p)}/{TOTAL} | ❌失败 {len(f)} | ⏰超时 {len(t)} | 💥错误 {len(e)}")
print(f"用例: 通过 {total_pass_cases} | 失败 {total_fail_cases}")

if f:
    print(f"\n❌ 失败文件 ({len(f)}):")
    for r in sorted(f, key=lambda x: x["spec"]):
        print(f"  {r['spec']:<45s} pass={r['passing']} fail={r['failing']}")

if t:
    print(f"\n⏰ 超时文件 ({len(t)}):")
    for r in sorted(t, key=lambda x: x["spec"]):
        print(f"  {r['spec']}")

# 保存JSON
(RESULTS_DIR / "results.json").write_text(json.dumps({
    "total": TOTAL, "passed": len(p), "failed": len(f), "timeout": len(t),
    "total_cases_pass": total_pass_cases, "total_cases_fail": total_fail_cases,
    "elapsed_seconds": round(elapsed_total),
    "specs": sorted(all_results, key=lambda x: x["spec"])
}, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"\n结果已保存: parallel-results/results.json")

if f:
    (RESULTS_DIR / "failed-specs.txt").write_text(
        "\n".join(r["spec"] for r in sorted(f, key=lambda x: x["spec"])), encoding='utf-8')
    print(f"失败列表: parallel-results/failed-specs.txt")
