"""运行全量测试并输出结果摘要"""
import subprocess, sys, os, time
os.chdir(r'd:\2026\aiops.v2\tests')

print(f"开始全量测试... {time.strftime('%H:%M:%S')}", flush=True)
start = time.time()

result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'api/', 'automated/', 'security/', 'test-automation/',
     '-q', '--tb=line', '-p', 'no:allure_listener', '-p', 'no:html', '-p', 'no:metadata', '--no-header'],
    capture_output=True, text=True, timeout=600
)

elapsed = time.time() - start
lines = (result.stdout + result.stderr).strip().split('\n')
print(f"\n{'='*60}")
print(f"全量测试完成 — 耗时 {elapsed:.1f}s")
print(f"{'='*60}")
for line in lines[-15:]:
    print(line)
print(f"\nRETURN_CODE={result.returncode}")
