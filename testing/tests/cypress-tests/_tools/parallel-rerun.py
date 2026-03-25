# -*- coding: utf-8 -*-
"""parallel-rerun.py — 6并行重跑仅失败的spec，实时进度"""
import subprocess, os, sys, time, json, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

CYPRESS_CMD = r"D:\2026\aiops.v2\tests\cypress-tests\node_modules\.bin\cypress.cmd"
E2E_DIR = "e2e"
RESULTS_DIR = "parallel-results"
WORKERS = 6
TIMEOUT = 900  # 15分钟, 对大文件更充裕

# 仅重跑上次失败+超时的spec
FAIL_SPECS = [
    '65-auth-error-profile',
]

specs = [f"{s}.cy.js" for s in FAIL_SPECS if os.path.exists(os.path.join(E2E_DIR, f"{s}.cy.js"))]
total = len(specs)

lock = threading.Lock()
done = 0
ok = 0
fail = 0
timeout_count = 0
start_time = time.time()

def fmt_time(s):
    m, sec = divmod(int(s), 60)
    return f"{m}m{sec:02d}s"

def run_spec(spec):
    global done, ok, fail, timeout_count
    log_path = os.path.join(RESULTS_DIR, f"{spec}.log")
    t0 = time.time()
    try:
        result = subprocess.run(
            [CYPRESS_CMD, "run", "--spec", f"{E2E_DIR}/{spec}", "--reporter", "spec"],
            capture_output=True, text=True, timeout=TIMEOUT, shell=True,
            cwd=os.getcwd()
        )
        elapsed = time.time() - t0
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout + "\n" + result.stderr)

        # 解析结果
        import re
        p_match = re.search(r'(\d+)\s+passing', result.stdout)
        f_match = re.search(r'(\d+)\s+failing', result.stdout)
        passing = int(p_match.group(1)) if p_match else 0
        failing = int(f_match.group(1)) if f_match else 0

        with lock:
            done += 1
            if failing > 0:
                fail += 1
                status = "❌"
            else:
                ok += 1
                status = "✅"
            elapsed_total = time.time() - start_time
            remaining = total - done
            avg = elapsed_total / done
            eta = avg * remaining
            print(f"[{done}/{total}] {status} {spec:<45} p={passing} f={failing} {int(elapsed)}s | "
                  f"已完成{done} 剩余{remaining} | ✅{ok} ❌{fail} ⏰{timeout_count} | "
                  f"已用{fmt_time(elapsed_total)} 预计还需{fmt_time(eta)}")
        return {'spec': spec, 'status': 'pass' if failing == 0 else 'fail', 'passing': passing, 'failing': failing, 'time': elapsed}
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("TIMEOUT")
        with lock:
            done += 1
            timeout_count += 1
            elapsed_total = time.time() - start_time
            remaining = total - done
            avg = elapsed_total / done
            eta = avg * remaining
            print(f"[{done}/{total}] ⏰ {spec:<45} p=0 f=0 {int(elapsed)}s | "
                  f"已完成{done} 剩余{remaining} | ✅{ok} ❌{fail} ⏰{timeout_count} | "
                  f"已用{fmt_time(elapsed_total)} 预计还需{fmt_time(eta)}")
        return {'spec': spec, 'status': 'timeout', 'passing': 0, 'failing': 0, 'time': elapsed}

print(f"=== 重跑仅失败spec: {total}个, {WORKERS}并行, 超时{TIMEOUT}s ===\n")
sys.stdout.flush()

results = []
with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(run_spec, s): s for s in specs}
    for future in as_completed(futures):
        results.append(future.result())

# 汇总
results.sort(key=lambda r: r['spec'])
with open(os.path.join(RESULTS_DIR, 'rerun-results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

elapsed_total = time.time() - start_time
print(f"\n=== 重跑完成: {total}个spec, 用时{fmt_time(elapsed_total)} ===")
print(f"✅ {ok}通过 | ❌ {fail}失败 | ⏰ {timeout_count}超时")

if fail > 0 or timeout_count > 0:
    print("\n--- 仍失败的spec ---")
    for r in results:
        if r['status'] != 'pass':
            print(f"  {r['status'].upper():8s} {r['spec']} (p={r['passing']} f={r['failing']})")

sys.stdout.flush()
